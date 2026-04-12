import { createFeature, createReducer, on } from '@ngrx/store';

import { SourceDto } from '../../core/api/workspace-api.types';
import { workspaceActions } from './workspace.actions';
import { AskState, WorkspaceState, initialWorkspaceState } from './workspace.state';

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
    on(workspaceActions.loadSourcesSuccess, (state, { sources }): WorkspaceState => {
      const nextActiveSourceId = reconcileActiveSourceId(
        state.activeSourceId,
        state.import.activeSubmission?.source_id ?? null,
        sources
      );

      return {
        ...state,
        sources: {
          items: sources,
          loading: false,
          loaded: true,
          error: null
        },
        activeSourceId: nextActiveSourceId,
        ask: nextActiveSourceId !== state.activeSourceId ? resetAskState(state.ask) : state.ask
      };
    }),
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
      activeSourceId: sourceId,
      ask: resetAskState(state.ask)
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
      },
      ask: resetAskState(state.ask)
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
    })),
    on(workspaceActions.submitAsk, (state): WorkspaceState => ({
      ...state,
      ask: {
        submitting: true,
        error: null,
        result: null
      }
    })),
    on(workspaceActions.submitAskSuccess, (state, { result }): WorkspaceState => ({
      ...state,
      ask: {
        submitting: false,
        error: null,
        result
      }
    })),
    on(workspaceActions.submitAskFailure, (state, { error }): WorkspaceState => ({
      ...state,
      ask: {
        submitting: false,
        error,
        result: null
      }
    }))
  )
});

function resetAskState(currentState: AskState): AskState {
  return {
    ...currentState,
    submitting: false,
    error: null,
    result: null
  };
}

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
