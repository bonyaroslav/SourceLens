import { ImportJobDto, ImportSubmissionDto, SourceDto } from '../../core/api/workspace-api.types';

export interface SourcesState {
  items: SourceDto[];
  loading: boolean;
  loaded: boolean;
  error: string | null;
}

export interface ImportState {
  submitting: boolean;
  error: string | null;
  activeSubmission: ImportSubmissionDto | null;
  activeJob: ImportJobDto | null;
}

export interface AskState {
  question: string;
}

export interface WorkspaceState {
  sources: SourcesState;
  activeSourceId: string | null;
  import: ImportState;
  ask: AskState;
}

export const initialWorkspaceState: WorkspaceState = {
  sources: {
    items: [],
    loading: false,
    loaded: false,
    error: null
  },
  activeSourceId: null,
  import: {
    submitting: false,
    error: null,
    activeSubmission: null,
    activeJob: null
  },
  ask: {
    question: ''
  }
};
