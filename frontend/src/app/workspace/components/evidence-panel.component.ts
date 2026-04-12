import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { TagModule } from 'primeng/tag';

import { ActiveSourceViewModel } from '../workspace.models';

@Component({
  selector: 'app-evidence-panel',
  imports: [TagModule],
  template: `
    <div class="panel-heading">
      <div>
        <span class="panel-kicker">Evidence + details</span>
        <h2>Inspect source status beside the answer</h2>
      </div>
      <span class="panel-meta">{{ activeSource?.statusLabel ?? 'No source' }}</span>
    </div>

    @if (activeSource) {
      <div class="detail-grid">
        <div class="detail-item">
          <span class="detail-label">Active source</span>
          <strong>{{ activeSource.name }}</strong>
        </div>
        <div class="detail-item">
          <span class="detail-label">Type</span>
          <strong>{{ activeSource.typeLabel }}</strong>
        </div>
        <div class="detail-item">
          <span class="detail-label">Created</span>
          <strong>{{ activeSource.createdLabel }}</strong>
        </div>
        <div class="detail-item">
          <span class="detail-label">Updated</span>
          <strong>{{ activeSource.updatedLabel }}</strong>
        </div>
      </div>

      <div class="detail-strip">
        <span class="section-label">Import status</span>
        <p-tag
          [value]="activeSource.statusLabel"
          [severity]="activeSource.statusSeverity"
        ></p-tag>
      </div>

      <p class="detail-note">{{ activeSource.description }}</p>

      <div class="evidence-placeholder">
        <h3>Evidence panel stays quiet in Phase 1</h3>
        <p>
          Import status and source metadata are real now. Retrieved evidence snippets appear after
          the ask flow is wired in Phase 2.
        </p>
      </div>
    } @else {
      <p class="panel-empty">
        No active source is loaded yet. Import a source or wait for the initial catalog request to
        finish.
      </p>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class EvidencePanelComponent {
  @Input() activeSource: ActiveSourceViewModel | null = null;
}
