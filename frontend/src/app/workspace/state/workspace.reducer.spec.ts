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
      score: 0.91
    }
  ]
};

describe('workspace reducer', () => {
  it('clears the previous ask result when a new ask starts', () => {
    const state = {
      ...initialWorkspaceState,
      ask: {
        submitting: false,
        error: 'Old error',
        result: TEST_RESULT
      }
    };

    const nextState = workspaceFeature.reducer(
      state,
      workspaceActions.submitAsk({ sourceId: 'source-1', question: 'What changed?' })
    );

    expect(nextState.ask).toEqual({
      submitting: true,
      error: null,
      result: null
    });
  });

  it('stores the latest ask result on success', () => {
    const nextState = workspaceFeature.reducer(
      initialWorkspaceState,
      workspaceActions.submitAskSuccess({ result: TEST_RESULT })
    );

    expect(nextState.ask).toEqual({
      submitting: false,
      error: null,
      result: TEST_RESULT
    });
  });

  it('clears ask state when the active source changes', () => {
    const state = {
      ...initialWorkspaceState,
      activeSourceId: 'source-1',
      ask: {
        submitting: false,
        error: 'Request failed',
        result: TEST_RESULT
      }
    };

    const nextState = workspaceFeature.reducer(
      state,
      workspaceActions.setActiveSource({ sourceId: 'source-2' })
    );

    expect(nextState.activeSourceId).toBe('source-2');
    expect(nextState.ask).toEqual({
      submitting: false,
      error: null,
      result: null
    });
  });
});
