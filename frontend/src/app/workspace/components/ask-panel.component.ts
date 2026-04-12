import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TextareaModule } from 'primeng/textarea';

@Component({
  selector: 'app-ask-panel',
  imports: [ButtonModule, TextareaModule],
  template: `
    <div class="panel-heading">
      <div>
        <span class="panel-kicker">Question + answer</span>
        <h2>Ask the active source</h2>
      </div>
      <span class="panel-meta">{{ activeSourceName }}</span>
    </div>

    <div class="question-shell">
      <label class="section-label" for="question-box">Question</label>
      <textarea
        id="question-box"
        pTextarea
        autoResize
        rows="5"
        [disabled]="true"
        placeholder="Phase 2 wires question answering and evidence retrieval."
      ></textarea>

      <div class="question-shell__footer">
        <p>{{ disabledReason }}</p>

        <button
          pButton
          type="button"
          label="Ask source"
          icon="pi pi-send"
          iconPos="right"
          severity="primary"
          [disabled]="true"
        ></button>
      </div>
    </div>

    <div class="answer-shell">
      <div class="answer-shell__header">
        <div>
          <span class="section-label">Answer</span>
          <h2>Phase 2 answer surface</h2>
        </div>
        <span class="panel-meta">{{ canAsk ? 'Ready next' : 'Waiting on import' }}</span>
      </div>

      <p class="answer-body">
        This panel keeps the final layout visible now, but grounded answer generation is still out
        of scope for Phase 1.
      </p>

      <ul class="answer-points">
        <li>NgRx already owns the active source and import readiness state.</li>
        <li>The ask request and evidence list will plug into this panel in Phase 2.</li>
        <li>The current disabled state prevents the UI from implying backend behavior that is not wired yet.</li>
      </ul>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AskPanelComponent {
  @Input() activeSourceName = 'No active source';
  @Input() canAsk = false;
  @Input({ required: true }) disabledReason!: string;
}
