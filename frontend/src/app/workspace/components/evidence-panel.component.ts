import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { TagModule } from 'primeng/tag';

import {
  ActiveSourceViewModel,
  AskResultViewModel,
  EvidenceItemViewModel,
} from '../workspace.models';

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
        <p-tag [value]="activeSource.statusLabel" [severity]="activeSource.statusSeverity"></p-tag>
      </div>

      <p class="detail-note">{{ activeSource.description }}</p>

      @if (submitting) {
        <div class="evidence-placeholder">
          <h3>Retrieving evidence</h3>
          <p>The latest ask request is in flight for this source.</p>
        </div>
      } @else if (!result) {
        <div class="evidence-placeholder">
          <h3>No answer yet</h3>
          <p>Ask the active source to render evidence snippets in this panel.</p>
        </div>
      } @else if (hasInsufficientEvidence) {
        <div class="evidence-placeholder">
          <h3>Insufficient evidence</h3>
          <p>The ask request completed, but the backend did not return supporting snippets.</p>
        </div>
      } @else if (evidenceItems.length > 0) {
        <div class="evidence-list">
          @for (evidence of evidenceItems; track evidence.chunkId) {
            <article class="evidence-item">
              <div class="evidence-item__meta">
                <div>
                  <h3>Chunk {{ evidence.chunkIndex }}</h3>
                  <p>{{ evidence.relativePath ?? result.groundingLabel }}</p>
                </div>
                <span class="evidence-score">Score {{ evidence.score }}</span>
              </div>

              <p>{{ evidence.text }}</p>
            </article>
          }
        </div>
      } @else {
        <div class="evidence-placeholder">
          <h3>No evidence returned</h3>
          <p>The latest answer completed without evidence snippets.</p>
        </div>
      }
    } @else {
      <p class="panel-empty">
        No active source is loaded yet. Import a source or wait for the initial catalog request to
        finish.
      </p>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EvidencePanelComponent {
  @Input() activeSource: ActiveSourceViewModel | null = null;
  @Input() submitting = false;
  @Input() result: AskResultViewModel | null = null;
  @Input() evidenceItems: EvidenceItemViewModel[] = [];
  @Input() hasInsufficientEvidence = false;
}
