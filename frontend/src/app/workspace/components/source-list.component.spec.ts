import { TestBed } from '@angular/core/testing';

import { SourceListItemViewModel } from '../workspace.models';
import { SourceListComponent } from './source-list.component';

const TEST_SOURCES: SourceListItemViewModel[] = [
  {
    id: 'source-1',
    name: 'plan.md',
    description: 'Locked scope',
    typeLabel: 'Local file',
    statusLabel: 'Ready',
    statusSeverity: 'success',
    updatedLabel: 'Updated Apr 12, 2026, 10:05 AM',
  },
];

describe('SourceListComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SourceListComponent],
    }).compileComponents();
  });

  it('renders the loading state while the source catalog request is in flight', () => {
    const fixture = TestBed.createComponent(SourceListComponent);
    fixture.componentRef.setInput('loading', true);
    fixture.detectChanges();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain(
      'Loading sources from the backend...',
    );
  });

  it('renders the empty state when the backend returns no sources', () => {
    const fixture = TestBed.createComponent(SourceListComponent);
    fixture.componentRef.setInput('sources', []);
    fixture.detectChanges();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain(
      'No imported sources yet.',
    );
  });

  it('renders the request error when loading sources fails', () => {
    const fixture = TestBed.createComponent(SourceListComponent);
    fixture.componentRef.setInput('error', 'Catalog request failed.');
    fixture.detectChanges();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain('Catalog request failed.');
  });

  it('emits the selected source id for click interaction', () => {
    const fixture = TestBed.createComponent(SourceListComponent);
    fixture.componentRef.setInput('sources', TEST_SOURCES);
    fixture.detectChanges();

    const emitted: string[] = [];
    fixture.componentInstance.selectSource.subscribe((sourceId) => emitted.push(sourceId));

    (fixture.nativeElement.querySelector('.source-row') as HTMLElement).click();

    expect(emitted).toEqual(['source-1']);
  });
});
