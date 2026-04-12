import {
  ChangeDetectionStrategy,
  Component,
  OnInit,
  ViewEncapsulation,
  computed,
  inject
} from '@angular/core';
import { Store } from '@ngrx/store';

import { ImportSourceRequest } from '../../core/api/workspace-api.types';
import { AskPanelComponent } from './ask-panel.component';
import { EvidencePanelComponent } from './evidence-panel.component';
import { ImportFormComponent } from './import-form.component';
import { SourceListComponent } from './source-list.component';
import { workspaceActions } from '../state/workspace.actions';
import {
  selectActiveSourceViewModel,
  selectAskError,
  selectAskDisabledReason,
  selectAskResult,
  selectAskSubmitting,
  selectCanAsk,
  selectEvidenceItems,
  selectHasInsufficientEvidence,
  selectImportPanelViewModel,
  selectSourceListItems,
  selectSourcesError,
  selectSourcesLoading
} from '../state/workspace.selectors';

@Component({
  selector: 'app-workspace-shell',
  imports: [ImportFormComponent, SourceListComponent, AskPanelComponent, EvidencePanelComponent],
  templateUrl: './workspace-shell.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  encapsulation: ViewEncapsulation.None
})
export class WorkspaceShellComponent implements OnInit {
  private readonly store = inject(Store);

  readonly sources = this.store.selectSignal(selectSourceListItems);
  readonly sourcesLoading = this.store.selectSignal(selectSourcesLoading);
  readonly sourcesError = this.store.selectSignal(selectSourcesError);
  readonly activeSource = this.store.selectSignal(selectActiveSourceViewModel);
  readonly importPanel = this.store.selectSignal(selectImportPanelViewModel);
  readonly canAsk = this.store.selectSignal(selectCanAsk);
  readonly askDisabledReason = this.store.selectSignal(selectAskDisabledReason);
  readonly askSubmitting = this.store.selectSignal(selectAskSubmitting);
  readonly askError = this.store.selectSignal(selectAskError);
  readonly askResult = this.store.selectSignal(selectAskResult);
  readonly evidenceItems = this.store.selectSignal(selectEvidenceItems);
  readonly hasInsufficientEvidence = this.store.selectSignal(selectHasInsufficientEvidence);
  readonly activeSourceId = computed(() => this.activeSource()?.id ?? null);
  readonly sourceCountLabel = computed(() => `${this.sources().length} sources`);
  readonly activeSourceName = computed(
    () => this.activeSource()?.name ?? 'No active source selected'
  );

  ngOnInit(): void {
    this.store.dispatch(workspaceActions.workspaceEntered());
  }

  onSelectSource(sourceId: string): void {
    this.store.dispatch(workspaceActions.setActiveSource({ sourceId }));
  }

  onSubmitImport(request: ImportSourceRequest): void {
    this.store.dispatch(workspaceActions.submitImport({ request }));
  }

  onSubmitAsk(question: string): void {
    const sourceId = this.activeSourceId();
    if (!sourceId) {
      return;
    }

    this.store.dispatch(workspaceActions.submitAsk({ sourceId, question }));
  }
}
