import { HttpErrorResponse } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Actions, createEffect, ofType } from '@ngrx/effects';
import { EMPTY, concat, of, timer } from 'rxjs';
import { catchError, exhaustMap, expand, map, switchMap } from 'rxjs/operators';

import { WorkspaceApiService } from '../../core/api/workspace-api.service';
import { ImportJobDto } from '../../core/api/workspace-api.types';
import { workspaceActions } from './workspace.actions';

const POLL_INTERVAL_MS = 1200;

@Injectable()
export class WorkspaceEffects {
  private readonly actions$ = inject(Actions);
  private readonly workspaceApi = inject(WorkspaceApiService);

  readonly workspaceEntered$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.workspaceEntered),
      map(() => workspaceActions.loadSources()),
    ),
  );

  readonly loadSources$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.loadSources),
      switchMap(() =>
        this.workspaceApi.listSources().pipe(
          map((sources) => workspaceActions.loadSourcesSuccess({ sources })),
          catchError((error: unknown) =>
            of(workspaceActions.loadSourcesFailure({ error: getErrorMessage(error) })),
          ),
        ),
      ),
    ),
  );

  readonly submitImport$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.submitImport),
      switchMap(({ request }) =>
        this.workspaceApi.submitImport(request).pipe(
          switchMap((submission) =>
            concat(
              of(workspaceActions.submitImportSuccess({ submission })),
              of(workspaceActions.loadSources()),
              of(workspaceActions.pollImportJob({ jobId: submission.job_id })),
            ),
          ),
          catchError((error: unknown) =>
            of(workspaceActions.submitImportFailure({ error: getErrorMessage(error) })),
          ),
        ),
      ),
    ),
  );

  readonly pollImportJob$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.pollImportJob),
      switchMap(({ jobId }) =>
        this.workspaceApi.getImportJob(jobId).pipe(
          expand((job) =>
            isTerminalJob(job)
              ? EMPTY
              : timer(POLL_INTERVAL_MS).pipe(
                  switchMap(() => this.workspaceApi.getImportJob(jobId)),
                ),
          ),
          map((job) => workspaceActions.pollImportJobSuccess({ job })),
          catchError((error: unknown) =>
            of(workspaceActions.pollImportJobFailure({ error: getErrorMessage(error) })),
          ),
        ),
      ),
    ),
  );

  readonly refreshSourcesOnTerminalJob$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.pollImportJobSuccess),
      switchMap(({ job }) => (isTerminalJob(job) ? of(workspaceActions.loadSources()) : EMPTY)),
    ),
  );

  readonly submitAsk$ = createEffect(() =>
    this.actions$.pipe(
      ofType(workspaceActions.submitAsk),
      exhaustMap(({ sourceId, question }) =>
        this.workspaceApi.askSource(sourceId, { question }).pipe(
          map((result) => workspaceActions.submitAskSuccess({ result })),
          catchError((error: unknown) =>
            of(workspaceActions.submitAskFailure({ error: getAskErrorMessage(error) })),
          ),
        ),
      ),
    ),
  );
}

function isTerminalJob(job: ImportJobDto): boolean {
  return job.status === 'completed' || job.status === 'failed';
}

function getErrorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (typeof error.error === 'object' && error.error !== null && 'detail' in error.error) {
      const detail = error.error.detail;
      if (typeof detail === 'string') {
        return detail;
      }
    }

    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Unexpected request failure.';
}

function getAskErrorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    switch (error.status) {
      case 400:
        return 'Enter a valid question before asking the source.';
      case 404:
        return 'The selected source could not be found. Refresh the catalog and choose another source.';
      case 409:
        return 'This source is not ready yet. Wait for indexing to finish before asking.';
      default: {
        const detail =
          typeof error.error === 'object' &&
          error.error !== null &&
          'detail' in error.error &&
          typeof error.error.detail === 'string'
            ? error.error.detail
            : error.message;

        return detail ? `The ask request failed. ${detail}` : 'The ask request failed.';
      }
    }
  }

  if (error instanceof Error) {
    return `The ask request failed. ${error.message}`;
  }

  return 'The ask request failed.';
}
