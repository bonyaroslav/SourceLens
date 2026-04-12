import { createSelector } from '@ngrx/store';

import {
  toActiveSourceViewModel,
  toImportPanelViewModel,
  toSourceListItemViewModel,
  toSourceStatusMeta
} from '../../core/api/workspace-api.mappers';
import { workspaceFeature } from './workspace.reducer';

export const selectSources = createSelector(
  workspaceFeature.selectSources,
  (sourcesState) => sourcesState.items
);

export const selectSourcesLoading = createSelector(
  workspaceFeature.selectSources,
  (sourcesState) => sourcesState.loading
);

export const selectSourcesError = createSelector(
  workspaceFeature.selectSources,
  (sourcesState) => sourcesState.error
);

export const selectSourceListItems = createSelector(selectSources, (sources) =>
  sources.map(toSourceListItemViewModel)
);

export const selectActiveSource = createSelector(
  selectSources,
  workspaceFeature.selectActiveSourceId,
  (sources, activeSourceId) => sources.find((source) => source.id === activeSourceId) ?? null
);

export const selectActiveSourceViewModel = createSelector(selectActiveSource, (source) =>
  source ? toActiveSourceViewModel(source) : null
);

export const selectImportPanelViewModel = createSelector(
  workspaceFeature.selectImport,
  (importState) =>
    toImportPanelViewModel(
      importState.activeSubmission,
      importState.activeJob,
      importState.error,
      importState.submitting
    )
);

export const selectCanAsk = createSelector(
  selectActiveSource,
  (source) => source?.import_status === 'completed'
);

export const selectAskDisabledReason = createSelector(
  selectActiveSource,
  selectCanAsk,
  (source, canAsk) => {
    if (source === null) {
      return 'Import a source or wait for one to load before the ask flow can continue.';
    }

    if (!canAsk) {
      return `This source is ${toSourceStatusMeta(source.import_status).label.toLowerCase()}. Ask stays disabled until the import completes.`;
    }

    return 'This source is ready. Asking and evidence rendering land in Phase 2.';
  }
);
