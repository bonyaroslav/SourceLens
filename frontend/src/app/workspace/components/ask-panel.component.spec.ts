import { TestBed } from '@angular/core/testing';

import { AskResultViewModel } from '../workspace.models';
import { AskPanelComponent } from './ask-panel.component';

const TEST_RESULT: AskResultViewModel = {
  sourceId: 'source-1',
  question: 'What changed?',
  answer: 'Grounded answer from the selected source.',
  groundingStatus: 'grounded',
  groundingLabel: 'Grounded',
  groundingSeverity: 'success',
};

describe('AskPanelComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AskPanelComponent],
    }).compileComponents();
  });

  it('enables submit for completed sources with non-empty trimmed questions', () => {
    const fixture = TestBed.createComponent(AskPanelComponent);
    fixture.componentRef.setInput('activeSourceName', 'plan.md');
    fixture.componentRef.setInput('canAsk', true);
    fixture.componentRef.setInput(
      'disabledReason',
      'This source is ready. Ask a focused question to retrieve a grounded answer and visible evidence.',
    );
    fixture.detectChanges();

    const emitted: string[] = [];
    fixture.componentInstance.submitAsk.subscribe((question) => emitted.push(question));

    const textarea = fixture.nativeElement.querySelector('#question-box') as HTMLTextAreaElement;
    textarea.value = '  What changed?  ';
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('button') as HTMLButtonElement;
    expect(button.disabled).toBe(false);

    button.click();

    expect(emitted).toEqual(['What changed?']);
  });

  it('renders the grounded answer when a result is present', () => {
    const fixture = TestBed.createComponent(AskPanelComponent);
    fixture.componentRef.setInput('activeSourceName', 'plan.md');
    fixture.componentRef.setInput('canAsk', true);
    fixture.componentRef.setInput('disabledReason', 'Ready');
    fixture.componentRef.setInput('result', TEST_RESULT);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Grounded');
    expect(compiled.textContent).toContain('What changed?');
    expect(compiled.textContent).toContain('Grounded answer from the selected source.');
  });
});
