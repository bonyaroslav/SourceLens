import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { App } from './app';
import { appConfig } from './app.config';
import { WorkspaceApiService } from './core/api/workspace-api.service';
import { ImportJobDto, ImportSubmissionDto, SourceDto } from './core/api/workspace-api.types';

const TEST_SOURCES: SourceDto[] = [
  {
    id: 'source-1',
    name: 'plan.md',
    description: 'Locked product scope.',
    source_type: 'local_file',
    import_status: 'completed',
    created_at: '2026-04-12T10:00:00Z',
    updated_at: '2026-04-12T10:05:00Z'
  }
];

const TEST_SUBMISSION: ImportSubmissionDto = {
  source_id: 'source-1',
  job_id: 'job-1',
  status: 'queued'
};

const TEST_JOB: ImportJobDto = {
  job_id: 'job-1',
  source_id: 'source-1',
  status: 'completed',
  started_at: '2026-04-12T10:00:00Z',
  finished_at: '2026-04-12T10:05:00Z',
  error_message: null
};

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        ...appConfig.providers,
        provideHttpClientTesting(),
        {
          provide: WorkspaceApiService,
          useValue: {
            listSources: () => of(TEST_SOURCES),
            getSource: () => of(TEST_SOURCES[0]),
            submitImport: () => of(TEST_SUBMISSION),
            getImportJob: () => of(TEST_JOB)
          }
        }
      ]
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the balanced workspace heading', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Balanced Canvas workspace');
  });

  it('should load a real active source from the store-backed catalog', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('plan.md');
    expect(compiled.textContent).toContain('Ready');
  });

  it('should keep the ask action disabled during phase 1', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button')
    ) as HTMLButtonElement[];
    const askButton = buttons.find((button) => button.textContent?.includes('Ask source'));

    expect(askButton?.disabled).toBe(true);
  });
});
