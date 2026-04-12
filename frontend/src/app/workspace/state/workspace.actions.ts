import { createActionGroup, emptyProps, props } from '@ngrx/store';

import {
  AskResponseDto,
  ImportJobDto,
  ImportSourceRequest,
  ImportSubmissionDto,
  SourceDto
} from '../../core/api/workspace-api.types';

export const workspaceActions = createActionGroup({
  source: 'Workspace',
  events: {
    workspaceEntered: emptyProps(),
    loadSources: emptyProps(),
    loadSourcesSuccess: props<{ sources: SourceDto[] }>(),
    loadSourcesFailure: props<{ error: string }>(),
    setActiveSource: props<{ sourceId: string }>(),
    submitImport: props<{ request: ImportSourceRequest }>(),
    submitImportSuccess: props<{ submission: ImportSubmissionDto }>(),
    submitImportFailure: props<{ error: string }>(),
    pollImportJob: props<{ jobId: string }>(),
    pollImportJobSuccess: props<{ job: ImportJobDto }>(),
    pollImportJobFailure: props<{ error: string }>(),
    submitAsk: props<{ sourceId: string; question: string }>(),
    submitAskSuccess: props<{ result: AskResponseDto }>(),
    submitAskFailure: props<{ error: string }>()
  }
});
