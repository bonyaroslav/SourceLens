import { TestBed } from '@angular/core/testing';

import {
  ActiveSourceViewModel,
  AskResultViewModel,
  EvidenceItemViewModel,
} from '../workspace.models';
import { EvidencePanelComponent } from './evidence-panel.component';

const ACTIVE_SOURCE: ActiveSourceViewModel = {
  id: 'source-1',
  name: 'plan.md',
  description: 'Locked scope',
  typeLabel: 'Local file',
  statusLabel: 'Ready',
  statusSeverity: 'success',
  createdLabel: 'Apr 12, 2026, 10:00 AM',
  updatedLabel: 'Apr 12, 2026, 10:05 AM',
  isAskable: true,
};

const GROUNDED_RESULT: AskResultViewModel = {
  sourceId: 'source-1',
  question: 'What changed?',
  answer: 'Grounded answer.',
  groundingStatus: 'grounded',
  groundingLabel: 'Grounded',
  groundingSeverity: 'success',
};

const EVIDENCE_ITEMS: EvidenceItemViewModel[] = [
  {
    chunkId: 'chunk-1',
    chunkIndex: 2,
    text: 'Beta paragraph two with answer context.',
    score: 0.84,
    relativePath: 'notes/beta.txt',
  },
];

describe('EvidencePanelComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EvidencePanelComponent],
    }).compileComponents();
  });

  it('renders an explicit insufficient-evidence state', () => {
    const fixture = TestBed.createComponent(EvidencePanelComponent);
    fixture.componentRef.setInput('activeSource', ACTIVE_SOURCE);
    fixture.componentRef.setInput('result', {
      ...GROUNDED_RESULT,
      groundingStatus: 'insufficient_evidence',
      groundingLabel: 'Insufficient evidence',
      groundingSeverity: 'warn',
    });
    fixture.componentRef.setInput('hasInsufficientEvidence', true);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Insufficient evidence');
    expect(compiled.textContent).toContain(
      'The ask request completed, but the backend did not return supporting snippets.',
    );
  });

  it('renders chunk index, raw score, and evidence text', () => {
    const fixture = TestBed.createComponent(EvidencePanelComponent);
    fixture.componentRef.setInput('activeSource', ACTIVE_SOURCE);
    fixture.componentRef.setInput('result', GROUNDED_RESULT);
    fixture.componentRef.setInput('evidenceItems', EVIDENCE_ITEMS);
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Chunk 2');
    expect(compiled.textContent).toContain('notes/beta.txt');
    expect(compiled.textContent).toContain('Score 0.84');
    expect(compiled.textContent).toContain('Beta paragraph two with answer context.');
  });
});
