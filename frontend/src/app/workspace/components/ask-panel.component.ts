import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { TextareaModule } from 'primeng/textarea';

import { AskResultViewModel } from '../workspace.models';

@Component({
  selector: 'app-ask-panel',
  imports: [ButtonModule, TagModule, TextareaModule],
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
        [disabled]="!canAsk || submitting"
        [value]="question"
        placeholder="Ask what this source says, what it implies, or what evidence supports a claim."
        (input)="onQuestionInput($event)"
      ></textarea>

      <div class="question-shell__footer">
        <p>{{ statusCopy }}</p>

        <button
          pButton
          type="button"
          label="Ask source"
          icon="pi pi-send"
          iconPos="right"
          severity="primary"
          [loading]="submitting"
          [disabled]="!canSubmit"
          (click)="onSubmit()"
        ></button>
      </div>
    </div>

    <div class="answer-shell">
      <div class="answer-shell__header">
        <div>
          <span class="section-label">Answer</span>
          <h2>Latest response</h2>
        </div>
        <span class="panel-meta">{{ answerMeta }}</span>
      </div>

      @if (result) {
        <div class="answer-shell__status">
          <span class="section-label">Grounding status</span>
          <p-tag [value]="result.groundingLabel" [severity]="result.groundingSeverity"></p-tag>
        </div>

        <div class="answer-context">
          <span class="section-label">Question</span>
          <p class="answer-question">{{ result.question }}</p>
        </div>

        <p class="answer-body">{{ result.answer }}</p>
      } @else if (error) {
        <p class="answer-body answer-body--error">{{ error }}</p>
      } @else if (submitting) {
        <p class="answer-body answer-body--muted">
          Retrieving evidence from the active source and generating a grounded answer.
        </p>
      } @else if (canAsk) {
        <p class="answer-body answer-body--muted">
          This source is ready. Submit a focused question to render the latest answer here.
        </p>
      } @else {
        <p class="answer-body answer-body--muted">{{ disabledReason }}</p>
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AskPanelComponent {
  @Input() activeSourceName = 'No active source';
  @Input() canAsk = false;
  @Input({ required: true }) disabledReason!: string;
  @Input() submitting = false;
  @Input() error: string | null = null;
  @Input() result: AskResultViewModel | null = null;
  @Output() readonly submitAsk = new EventEmitter<string>();

  question = '';

  get canSubmit(): boolean {
    return this.canAsk && !this.submitting && this.question.trim().length > 0;
  }

  get statusCopy(): string {
    if (!this.canAsk) {
      return this.disabledReason;
    }

    if (this.submitting) {
      return 'The latest question is in flight. Duplicate submissions stay blocked until it completes.';
    }

    if (this.result?.groundingStatus === 'insufficient_evidence') {
      return 'The last request completed, but the source did not contain enough evidence to support the answer.';
    }

    if (this.result) {
      return 'The latest response completed successfully. Ask another question to replace it.';
    }

    return 'This source is ready. The latest successful response will replace any previous answer.';
  }

  get answerMeta(): string {
    if (this.submitting) {
      return 'Submitting';
    }

    if (this.result) {
      return this.result.groundingLabel;
    }

    return this.canAsk ? 'Ready' : 'Blocked';
  }

  onQuestionInput(event: Event): void {
    this.question = (event.target as HTMLTextAreaElement).value;
  }

  onSubmit(): void {
    const question = this.question.trim();

    if (!this.canAsk || this.submitting || question.length === 0) {
      return;
    }

    this.submitAsk.emit(question);
  }
}
