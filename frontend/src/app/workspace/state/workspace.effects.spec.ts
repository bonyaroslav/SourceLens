import { HttpErrorResponse } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideMockActions } from '@ngrx/effects/testing';
import { Action } from '@ngrx/store';
import { firstValueFrom, of, Subject, throwError } from 'rxjs';

import { WorkspaceApiService } from '../../core/api/workspace-api.service';
import { AskResponseDto } from '../../core/api/workspace-api.types';
import { WorkspaceEffects } from './workspace.effects';
import { workspaceActions } from './workspace.actions';

const TEST_ASK_RESULT: AskResponseDto = {
  source_id: 'source-1',
  question: 'What changed?',
  answer: 'Grounded answer.',
  grounding_status: 'grounded',
  evidence: [
    {
      chunk_id: 'chunk-1',
      chunk_index: 0,
      text: 'Alpha paragraph.',
      score: 0.93,
      relative_path: 'alpha.md',
    },
  ],
};

describe('WorkspaceEffects', () => {
  let actions$: Subject<Action>;
  let effects: WorkspaceEffects;
  let workspaceApi: {
    listSources: typeof WorkspaceApiService.prototype.listSources;
    getSource: typeof WorkspaceApiService.prototype.getSource;
    submitImport: typeof WorkspaceApiService.prototype.submitImport;
    getImportJob: typeof WorkspaceApiService.prototype.getImportJob;
    askSource: typeof WorkspaceApiService.prototype.askSource;
  };

  beforeEach(() => {
    actions$ = new Subject<Action>();
    workspaceApi = {
      listSources: () => of([]),
      getSource: () =>
        of({
          id: 'source-1',
          name: 'plan.md',
          description: 'Locked scope',
          source_type: 'local_file',
          import_status: 'completed',
          created_at: '2026-04-12T10:00:00Z',
          updated_at: '2026-04-12T10:05:00Z',
        }),
      submitImport: () =>
        of({
          source_id: 'source-1',
          job_id: 'job-1',
          status: 'queued',
        }),
      getImportJob: () =>
        of({
          job_id: 'job-1',
          source_id: 'source-1',
          status: 'completed',
          started_at: '2026-04-12T10:00:00Z',
          finished_at: '2026-04-12T10:05:00Z',
          error_message: null,
        }),
      askSource: () => of(TEST_ASK_RESULT),
    };

    TestBed.configureTestingModule({
      providers: [
        WorkspaceEffects,
        provideMockActions(() => actions$),
        {
          provide: WorkspaceApiService,
          useValue: workspaceApi,
        },
      ],
    });

    effects = TestBed.inject(WorkspaceEffects);
  });

  afterEach(() => {
    actions$.complete();
  });

  it('submits ask requests and emits the successful result', async () => {
    let receivedSourceId: string | null = null;
    let receivedQuestion: string | null = null;
    workspaceApi.askSource = (sourceId, request) => {
      receivedSourceId = sourceId;
      receivedQuestion = request.question;
      return of(TEST_ASK_RESULT);
    };

    const actionPromise = firstValueFrom(effects.submitAsk$);
    actions$.next(workspaceActions.submitAsk({ sourceId: 'source-1', question: 'What changed?' }));

    await expect(actionPromise).resolves.toEqual(
      workspaceActions.submitAskSuccess({ result: TEST_ASK_RESULT }),
    );
    expect(receivedSourceId).toBe('source-1');
    expect(receivedQuestion).toBe('What changed?');
  });

  [
    [400, 'Enter a valid question before asking the source.'],
    [404, 'The selected source could not be found. Refresh the catalog and choose another source.'],
    [409, 'This source is not ready yet. Wait for indexing to finish before asking.'],
  ].forEach(([status, message]) => {
    it(`maps ${status} ask failures to a stable UI message`, async () => {
      workspaceApi.askSource = () =>
        throwError(
          () =>
            new HttpErrorResponse({
              status: Number(status),
              error: { detail: 'Backend detail.' },
            }),
        );

      const actionPromise = firstValueFrom(effects.submitAsk$);
      actions$.next(
        workspaceActions.submitAsk({ sourceId: 'source-1', question: 'What changed?' }),
      );

      await expect(actionPromise).resolves.toEqual(
        workspaceActions.submitAskFailure({ error: String(message) }),
      );
    });
  });

  it('uses exhaustMap to ignore duplicate in-flight ask requests', () => {
    const response$ = new Subject<AskResponseDto>();
    const emitted: Action[] = [];
    let callCount = 0;

    workspaceApi.askSource = () => {
      callCount += 1;
      return response$;
    };

    const subscription = effects.submitAsk$.subscribe((action) => emitted.push(action));

    actions$.next(workspaceActions.submitAsk({ sourceId: 'source-1', question: 'First question' }));
    actions$.next(
      workspaceActions.submitAsk({ sourceId: 'source-1', question: 'Second question' }),
    );

    expect(callCount).toBe(1);

    response$.next(TEST_ASK_RESULT);
    response$.complete();

    expect(emitted).toEqual([workspaceActions.submitAskSuccess({ result: TEST_ASK_RESULT })]);

    subscription.unsubscribe();
  });
});
