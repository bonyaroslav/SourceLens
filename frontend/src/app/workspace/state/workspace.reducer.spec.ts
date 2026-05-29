import { workspaceActions } from './workspace.actions';
import { workspaceFeature } from './workspace.reducer';
import { initialWorkspaceState } from './workspace.state';

const TEST_RESULT = {
  source_id: 'source-1',
  question: 'What changed?',
  answer: 'A grounded answer.',
  grounding_status: 'grounded',
  evidence: [
    {
      chunk_id: 'chunk-1',
      chunk_index: 0,
      text: 'Alpha paragraph.',
      score: 0.91,
      relative_path: 'alpha.md',
    },
  ],
};

describe('workspace reducer', () => {
  it('clears stale ask state as soon as a new import is queued', () => {
    const state = {
      ...initialWorkspaceState,
      ask: {
        submitting: false,
        error: 'Old ask error',
        result: TEST_RESULT,
      },
      import: {
        ...initialWorkspaceState.import,
        activeSubmission: {
          source_id: 'old-source',
          job_id: 'old-job',
          status: 'failed',
        },
        activeJob: {
          job_id: 'old-job',
          source_id: 'old-source',
          status: 'failed',
          started_at: '2026-04-12T10:00:00Z',
          finished_at: '2026-04-12T10:05:00Z',
          error_message: 'Old import failed.',
        },
      },
    };

    const nextState = workspaceFeature.reducer(
      state,
      workspaceActions.submitImport({ request: { path: 'C:\\docs\\plan.md' } }),
    );

    expect(nextState.ask).toEqual({
      submitting: false,
      error: null,
      result: null,
    });
    expect(nextState.import.activeSubmission).toBeNull();
    expect(nextState.import.activeJob).toBeNull();
  });

  it('clears the previous ask result when a new ask starts', () => {
    const state = {
      ...initialWorkspaceState,
      ask: {
        submitting: false,
        error: 'Old error',
        result: TEST_RESULT,
      },
    };

    const nextState = workspaceFeature.reducer(
      state,
      workspaceActions.submitAsk({ sourceId: 'source-1', question: 'What changed?' }),
    );

    expect(nextState.ask).toEqual({
      submitting: true,
      error: null,
      result: null,
    });
  });

  it('stores the latest ask result on success', () => {
    const nextState = workspaceFeature.reducer(
      initialWorkspaceState,
      workspaceActions.submitAskSuccess({ result: TEST_RESULT }),
    );

    expect(nextState.ask).toEqual({
      submitting: false,
      error: null,
      result: TEST_RESULT,
    });
  });

  it('clears ask state when the active source changes', () => {
    const state = {
      ...initialWorkspaceState,
      activeSourceId: 'source-1',
      ask: {
        submitting: false,
        error: 'Request failed',
        result: TEST_RESULT,
      },
    };

    const nextState = workspaceFeature.reducer(
      state,
      workspaceActions.setActiveSource({ sourceId: 'source-2' }),
    );

    expect(nextState.activeSourceId).toBe('source-2');
    expect(nextState.ask).toEqual({
      submitting: false,
      error: null,
      result: null,
    });
  });
});
