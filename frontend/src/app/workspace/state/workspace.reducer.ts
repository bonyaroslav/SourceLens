import { createFeature, createReducer, on } from '@ngrx/store';

import { SourceDto } from '../../core/api/workspace-api.types';
import { workspaceActions } from './workspace.actions';
import { WorkspaceState, initialWorkspaceState } from './workspace.state';

export const workspaceFeature = createFeature({
  name: 'workspace',
  reducer: createReducer(
    initialWorkspaceState,
    on(workspaceActions.loadSources, (state): WorkspaceState => ({
      ...state,
      sources: {
        ...state.sources,
        loading: true,
        error: null
      }
    })),
    on(workspaceActions.loadSourcesSuccess, (state, { sources }): WorkspaceState => ({
      ...state,
      sources: {
        items: sources,
        loading: false,
        loaded: true,
        error: null
      },
      activeSourceId: reconcileActiveSourceId(
        state.activeSourceId,
        state.import.activeSubmission?.source_id ?? null,
        sources
      )
    })),
    on(workspaceActions.loadSourcesFailure, (state, { error }): WorkspaceState => ({
      ...state,
      sources: {
        ...state.sources,
        loading: false,
        loaded: true,
        error
      }
    })),
    on(workspaceActions.setActiveSource, (state, { sourceId }): WorkspaceState => ({
      ...state,
      activeSourceId: sourceId
    })),
    on(workspaceActions.submitImport, (state): WorkspaceState => ({
      ...state,
      import: {
        ...state.import,
        submitting: true,
        error: null
      }
    })),
    on(workspaceActions.submitImportSuccess, (state, { submission }): WorkspaceState => ({
      ...state,
      activeSourceId: submission.source_id,
      import: {
        submitting: false,
        error: null,
        activeSubmission: submission,
        activeJob: null
      }
    })),
    on(workspaceActions.submitImportFailure, (state, { error }): WorkspaceState => ({
      ...state,
      import: {
        ...state.import,
        submitting: false,
        error
      }
    })),
    on(workspaceActions.pollImportJob, (state): WorkspaceState => ({
      ...state,
      import: {
        ...state.import,
        error: null
      }
    })),
    on(workspaceActions.pollImportJobSuccess, (state, { job }): WorkspaceState => ({
      ...state,
      import: {
        ...state.import,
        activeJob: job,
        error: null
      },
      sources: {
        ...state.sources,
        items: updateSourceStatus(state.sources.items, job.source_id, job.status)
      }
    })),
    on(workspaceActions.pollImportJobFailure, (state, { error }): WorkspaceState => ({
      ...state,
      import: {
        ...state.import,
        error
      }
    }))
  )
});

function reconcileActiveSourceId(
  currentActiveSourceId: string | null,
  submittedSourceId: string | null,
  sources: SourceDto[]
): string | null {
  const ids = new Set(sources.map((source) => source.id));

  if (currentActiveSourceId !== null && ids.has(currentActiveSourceId)) {
    return currentActiveSourceId;
  }

  if (submittedSourceId !== null && ids.has(submittedSourceId)) {
    return submittedSourceId;
  }

  return sources[0]?.id ?? null;
}

function updateSourceStatus(
  sources: SourceDto[],
  sourceId: string,
  importStatus: string
): SourceDto[] {
  return sources.map((source) =>
    source.id === sourceId
      ? {
          ...source,
          import_status: importStatus
        }
      : source
  );
}
