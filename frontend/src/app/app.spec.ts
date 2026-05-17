import { provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

import { App } from './app';
import { appConfig } from './app.config';
import { WorkspaceApiService } from './core/api/workspace-api.service';
import {
  AskResponseDto,
  ImportJobDto,
  ImportSubmissionDto,
  SourceDto,
} from './core/api/workspace-api.types';

const TEST_SOURCES: SourceDto[] = [
  {
    id: 'source-1',
    name: 'plan.md',
    description: 'Locked product scope.',
    source_type: 'local_file',
    import_status: 'completed',
    created_at: '2026-04-12T10:00:00Z',
    updated_at: '2026-04-12T10:05:00Z',
  },
  {
    id: 'source-2',
    name: 'guide',
    description: 'Folder-backed source.',
    source_type: 'local_folder',
    import_status: 'completed',
    created_at: '2026-04-12T09:00:00Z',
    updated_at: '2026-04-12T10:10:00Z',
  },
];

const TEST_SUBMISSION: ImportSubmissionDto = {
  source_id: 'source-1',
  job_id: 'job-1',
  status: 'queued',
};

const TEST_JOB: ImportJobDto = {
  job_id: 'job-1',
  source_id: 'source-1',
  status: 'completed',
  started_at: '2026-04-12T10:00:00Z',
  finished_at: '2026-04-12T10:05:00Z',
  error_message: null,
};

const TEST_ASK_RESPONSE: AskResponseDto = {
  source_id: 'source-1',
  question: 'What changed?',
  answer: 'Grounded answer from the active source.',
  grounding_status: 'grounded',
  evidence: [
    {
      chunk_id: 'chunk-1',
      chunk_index: 0,
      text: 'Alpha paragraph.',
      score: 0.92,
      relative_path: 'docs/plan.md',
    },
  ],
};

describe('App', () => {
  const workspaceApi: {
    listSources: typeof WorkspaceApiService.prototype.listSources;
    getSource: typeof WorkspaceApiService.prototype.getSource;
    submitImport: typeof WorkspaceApiService.prototype.submitImport;
    getImportJob: typeof WorkspaceApiService.prototype.getImportJob;
    askSource: typeof WorkspaceApiService.prototype.askSource;
  } = {
    listSources: () => of(TEST_SOURCES),
    getSource: () => of(TEST_SOURCES[0]),
    submitImport: () => of(TEST_SUBMISSION),
    getImportJob: () => of(TEST_JOB),
    askSource: () => of(TEST_ASK_RESPONSE),
  };

  beforeEach(async () => {
    workspaceApi.listSources = () => of(TEST_SOURCES);
    workspaceApi.getSource = () => of(TEST_SOURCES[0]);
    workspaceApi.submitImport = () => of(TEST_SUBMISSION);
    workspaceApi.getImportJob = () => of(TEST_JOB);
    workspaceApi.askSource = () => of(TEST_ASK_RESPONSE);

    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        ...appConfig.providers,
        provideHttpClientTesting(),
        {
          provide: WorkspaceApiService,
          useValue: workspaceApi,
        },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render the grounded answer workspace heading', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Grounded answer workspace');
  });

  it('should load a real active source from the store-backed catalog', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('plan.md');
    expect(compiled.textContent).toContain('Ready');
  });

  it('should enable the ask action when a completed source has a non-empty question', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('#question-box') as HTMLTextAreaElement;
    textarea.value = '  What changed?  ';
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const buttons = Array.from(
      fixture.nativeElement.querySelectorAll('button'),
    ) as HTMLButtonElement[];
    const askButton = buttons.find((button) => button.textContent?.includes('Ask source'));

    expect(askButton?.disabled).toBe(false);
  });

  it('should let the user select one source, ask it, and render the answer with evidence', async () => {
    let requestedSourceId: string | null = null;
    let requestedQuestion: string | null = null;
    const expectedResponse: AskResponseDto = {
      source_id: 'source-2',
      question: 'What does the guide say?',
      answer: 'The guide explains the current MVP wiring.',
      grounding_status: 'grounded',
      evidence: [
        {
          chunk_id: 'chunk-2',
          chunk_index: 4,
          text: 'The Angular workspace now loads sources and renders evidence.',
          score: 0.88,
          relative_path: 'guide/beta.txt',
        },
      ],
    };

    workspaceApi.askSource = (sourceId: string, request: { question: string }) => {
      requestedSourceId = sourceId;
      requestedQuestion = request.question;
      return of(expectedResponse);
    };

    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const sourceRows = Array.from(
      fixture.nativeElement.querySelectorAll('.source-row'),
    ) as HTMLElement[];
    sourceRows[1].click();
    fixture.detectChanges();

    const textarea = fixture.nativeElement.querySelector('#question-box') as HTMLTextAreaElement;
    textarea.value = '  What does the guide say?  ';
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const askButton = (
      Array.from(fixture.nativeElement.querySelectorAll('button')) as HTMLButtonElement[]
    ).find((button) => button.textContent?.includes('Ask source'));
    expect(askButton).toBeTruthy();
    askButton!.click();

    await fixture.whenStable();
    fixture.detectChanges();

    const compiled = fixture.nativeElement as HTMLElement;
    expect(requestedSourceId).toBe('source-2');
    expect(requestedQuestion).toBe('What does the guide say?');
    expect(compiled.textContent).toContain('The guide explains the current MVP wiring.');
    expect(compiled.textContent).toContain(
      'The Angular workspace now loads sources and renders evidence.',
    );
    expect(compiled.textContent).toContain('guide/beta.txt');
  });
});
