import { TestBed } from '@angular/core/testing';

import { ImportPanelViewModel } from '../workspace.models';
import { ImportFormComponent } from './import-form.component';

const IDLE_IMPORT_STATE: ImportPanelViewModel = {
  pending: false,
  error: null,
  statusLabel: null,
  statusSeverity: null,
  statusDetail: null,
  jobId: null,
  sourceId: null,
};

describe('ImportFormComponent', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportFormComponent],
    }).compileComponents();
  });

  it('rejects whitespace-only paths with MVP path guidance', () => {
    const fixture = TestBed.createComponent(ImportFormComponent);
    fixture.componentRef.setInput('importState', IDLE_IMPORT_STATE);
    fixture.detectChanges();

    const form = fixture.nativeElement.querySelector('form') as HTMLFormElement;
    const pathInput = fixture.nativeElement.querySelector('#source-path') as HTMLInputElement;

    pathInput.value = '   ';
    pathInput.dispatchEvent(new Event('input'));
    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect((fixture.nativeElement as HTMLElement).textContent).toContain(
      'Enter a real local file or folder path before queueing the import.',
    );
  });

  it('emits a trimmed local path request', () => {
    const fixture = TestBed.createComponent(ImportFormComponent);
    fixture.componentRef.setInput('importState', IDLE_IMPORT_STATE);
    fixture.detectChanges();

    const emitted: Array<{ path: string; name?: string | null; description?: string | null }> = [];
    fixture.componentInstance.submitImport.subscribe((request) => emitted.push(request));

    const pathInput = fixture.nativeElement.querySelector('#source-path') as HTMLInputElement;
    pathInput.value = '  C:\\docs\\plan.md  ';
    pathInput.dispatchEvent(new Event('input'));

    const form = fixture.nativeElement.querySelector('form') as HTMLFormElement;
    form.dispatchEvent(new Event('submit'));
    fixture.detectChanges();

    expect(emitted).toEqual([{ path: 'C:\\docs\\plan.md', name: null, description: null }]);
  });
});
