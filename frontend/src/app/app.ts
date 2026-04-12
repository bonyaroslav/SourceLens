import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CheckboxModule } from 'primeng/checkbox';
import { TagModule } from 'primeng/tag';
import { TextareaModule } from 'primeng/textarea';

type SourceStatus = 'ready' | 'processing' | 'warning' | 'failed';
type TagSeverity =
  | 'success'
  | 'secondary'
  | 'info'
  | 'warn'
  | 'danger'
  | 'contrast'
  | null
  | undefined;

interface EvidenceSnippet {
  id: string;
  title: string;
  location: string;
  matchLabel: string;
  preview: string;
}

interface SourceItem {
  id: string;
  name: string;
  type: string;
  status: SourceStatus;
  updatedLabel: string;
  sizeLabel: string;
  detail: string;
  answerSeed: string;
  highlights: string[];
  snippets: EvidenceSnippet[];
}

interface AnswerState {
  sourceId: string;
  heading: string;
  body: string;
  takeaways: string[];
  snippets: EvidenceSnippet[];
  lastAskedLabel: string;
}

interface StatusMeta {
  label: string;
  severity: TagSeverity;
}

const DEFAULT_QUESTION = 'What has already been locked for the Source Lens MVP?';

const STATUS_META: Record<SourceStatus, StatusMeta> = {
  ready: { label: 'Ready', severity: 'success' },
  processing: { label: 'Indexing', severity: 'info' },
  warning: { label: 'Needs review', severity: 'warn' },
  failed: { label: 'Failed', severity: 'danger' }
};

const INITIAL_SOURCES: SourceItem[] = [
  {
    id: 'plan-md',
    name: 'plan.md',
    type: 'Markdown',
    status: 'ready',
    updatedLabel: 'Updated 6 min ago',
    sizeLabel: '11 KB',
    detail:
      'Locked architecture, MVP scope, storage boundaries, and the single-source ask rule live here.',
    answerSeed:
      'the MVP stays deliberately narrow around one selected source, local import, grounded answers, and visible evidence rather than broader connector or agent scope.',
    highlights: [
      'One highlighted source drives the current ask path.',
      'Grounded answers and inspectable evidence stay paired in the same workspace.',
      'Storage decisions remain local-first instead of remote-service heavy.'
    ],
    snippets: [
      {
        id: 'plan-1',
        title: 'Locked Product Scope',
        location: 'plan.md · MVP scope',
        matchLabel: 'High match',
        preview:
          'The current slice keeps one selected source at a time and returns answers with visible supporting evidence.'
      },
      {
        id: 'plan-2',
        title: 'Storage boundary',
        location: 'plan.md · architecture',
        matchLabel: 'Focused',
        preview:
          'Vectors stay in Qdrant local mode while metadata stays behind a SQLite repository boundary.'
      },
      {
        id: 'plan-3',
        title: 'Deferred work',
        location: 'plan.md · out of scope',
        matchLabel: 'Support',
        preview:
          'Multi-source querying, connector sprawl, and agent workflows are postponed until after the narrow vertical slice.'
      }
    ]
  },
  {
    id: 'readme-md',
    name: 'README.md',
    type: 'Markdown',
    status: 'ready',
    updatedLabel: 'Updated 18 min ago',
    sizeLabel: '10 KB',
    detail:
      'Product positioning and user-facing language for Source Lens live here, including how evidence improves trust.',
    answerSeed:
      'Source Lens is positioned as a knowledge workspace instead of generic chat, with source-aware questioning and a visible evidence panel doing most of the product work.',
    highlights: [
      'The product promise is operational, not marketing-heavy.',
      'Evidence visibility is treated as a trust feature, not a secondary detail.',
      'The current screen should feel like a workspace, not a homepage.'
    ],
    snippets: [
      {
        id: 'readme-1',
        title: 'Knowledge workspace positioning',
        location: 'README.md · why this exists',
        matchLabel: 'High match',
        preview:
          'The product is framed as a workspace for importing private knowledge and asking grounded questions against it.'
      },
      {
        id: 'readme-2',
        title: 'Evidence panel value',
        location: 'README.md · what makes it powerful',
        matchLabel: 'Focused',
        preview:
          'Supporting snippets are surfaced so the user can validate why an answer was produced.'
      },
      {
        id: 'readme-3',
        title: 'Local-first runtime',
        location: 'README.md · core experience',
        matchLabel: 'Support',
        preview:
          'Inference and retrieval stay close to the data through local infrastructure and a privacy-first posture.'
      }
    ]
  },
  {
    id: 'research-pdf',
    name: 'enterprise-feedback-digest.pdf',
    type: 'PDF',
    status: 'processing',
    updatedLabel: 'Imported 2 min ago',
    sizeLabel: '2.4 MB',
    detail:
      'A customer research digest that is still fake-indexing in this prototype, useful for showing non-ready status.',
    answerSeed:
      'operators care most about immediate clarity: what source is active, what status it is in, and where the answer is drawing support from.',
    highlights: [
      'Readable status handling matters as much as the answer box itself.',
      'A narrow question area is easier to scan than a feature-heavy composer.',
      'Source list density should support quick triage rather than decoration.'
    ],
    snippets: [
      {
        id: 'research-1',
        title: 'Operator preference',
        location: 'feedback digest · summary',
        matchLabel: 'Preview',
        preview:
          'Teams preferred a layout that showed import state, answer state, and evidence state without moving between views.'
      },
      {
        id: 'research-2',
        title: 'Trust signal',
        location: 'feedback digest · findings',
        matchLabel: 'Preview',
        preview:
          'Evidence placement on the right was easier to validate than hiding support below the answer.'
      },
      {
        id: 'research-3',
        title: 'Density note',
        location: 'feedback digest · findings',
        matchLabel: 'Preview',
        preview:
          'Compact layouts were preferred when spacing tightened without collapsing the source metadata into noise.'
      }
    ]
  },
  {
    id: 'legacy-html',
    name: 'legacy-import-notes.html',
    type: 'HTML',
    status: 'warning',
    updatedLabel: 'Updated yesterday',
    sizeLabel: '44 KB',
    detail:
      'Legacy notes imported with weak structure; useful for a review-needed status without breaking the single-screen flow.',
    answerSeed:
      'older notes still add context, but the workspace should visually signal when a source may need human review before it becomes the main ask target.',
    highlights: [
      'Status cues need to be obvious without taking over the layout.',
      'The active highlight should remain stronger than secondary warning labels.',
      'Evidence snippets can soften uncertainty by showing exactly what was captured.'
    ],
    snippets: [
      {
        id: 'legacy-1',
        title: 'Imported structure',
        location: 'legacy notes · capture preview',
        matchLabel: 'Support',
        preview:
          'The imported HTML preserved headings and body text, but some sections still need cleanup before they become reliable evidence.'
      },
      {
        id: 'legacy-2',
        title: 'Review recommendation',
        location: 'legacy notes · footer',
        matchLabel: 'Support',
        preview:
          'Marking uncertain sources for review keeps the UI honest without hiding them from the source list.'
      },
      {
        id: 'legacy-3',
        title: 'Source detail',
        location: 'legacy notes · metadata',
        matchLabel: 'Support',
        preview:
          'Users still wanted to see the source in context even when it was not the most trustworthy source to ask.'
      }
    ]
  }
];

function inferSourceType(fileName: string): string {
  const extension = fileName.split('.').pop()?.toLowerCase() ?? '';

  switch (extension) {
    case 'md':
      return 'Markdown';
    case 'pdf':
      return 'PDF';
    case 'html':
    case 'htm':
      return 'HTML';
    case 'txt':
      return 'Text';
    default:
      return 'Document';
  }
}

function formatBytes(size: number): string {
  if (!size) {
    return '0 B';
  }

  const units = ['B', 'KB', 'MB', 'GB'];
  const exponent = Math.min(Math.floor(Math.log(size) / Math.log(1024)), units.length - 1);
  const value = size / 1024 ** exponent;
  const precision = exponent === 0 ? 0 : 1;

  return `${value.toFixed(precision)} ${units[exponent]}`;
}

function buildImportedSource(file: File, index: number): SourceItem {
  const sourceType = inferSourceType(file.name);

  return {
    id: `imported-${index}`,
    name: file.name,
    type: sourceType,
    status: 'ready',
    updatedLabel: 'Imported just now',
    sizeLabel: formatBytes(file.size),
    detail:
      'This file was added locally in the browser only. The UI updates immediately, but parsing and backend import are still mocked.',
    answerSeed:
      'the imported file now behaves like the active ask target in this static MVP screen, even though retrieval and indexing are still represented with fake data.',
    highlights: [
      'Import updates the left rail immediately and keeps the flow visible.',
      'The newly imported file becomes the active source for asking.',
      'Evidence remains mocked until backend wiring is added later.'
    ],
    snippets: [
      {
        id: `imported-${index}-1`,
        title: 'Detected file type',
        location: `${file.name} · local preview`,
        matchLabel: 'Preview',
        preview: `${sourceType} detected from the selected file name so the row can surface a source type immediately.`
      },
      {
        id: `imported-${index}-2`,
        title: 'UI-only import state',
        location: `${file.name} · workflow note`,
        matchLabel: 'Preview',
        preview:
          'This stage only mutates fake client-side state, which keeps the prototype simple and avoids premature backend coupling.'
      },
      {
        id: `imported-${index}-3`,
        title: 'Single-source ask',
        location: `${file.name} · ask flow`,
        matchLabel: 'Preview',
        preview:
          'After import, the file is highlighted as the active ask source so the center panel stays scoped to one source.'
      }
    ]
  };
}

function buildMockAnswer(source: SourceItem, question: string): AnswerState {
  const cleanedQuestion = question.trim() || DEFAULT_QUESTION;
  const statusContext =
    source.status === 'processing'
      ? 'The status still reads as indexing, so this is intentionally presented as a preview rather than a final answer.'
      : source.status === 'warning'
        ? 'The source is flagged for review, so the wording stays a little more cautious even in the static mock.'
        : source.status === 'failed'
          ? 'The source is marked failed, so the panel is showing a placeholder explanation instead of pretending the answer is trustworthy.'
          : 'The highlighted source is treated as the only ask target, which keeps the MVP flow easy to read.';

  return {
    sourceId: source.id,
    heading: `Mock answer from ${source.name}`,
    body: `For "${cleanedQuestion}", the clearest read is that ${source.answerSeed} ${statusContext}`,
    takeaways: source.highlights,
    snippets: source.snippets,
    lastAskedLabel: `Mocked at ${new Intl.DateTimeFormat([], {
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date())}`
  };
}

@Component({
  selector: 'app-root',
  imports: [FormsModule, ButtonModule, CheckboxModule, TagModule, TextareaModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  readonly sources = signal<SourceItem[]>(INITIAL_SOURCES);
  readonly selectedSourceIds = signal<string[]>(['plan-md', 'readme-md']);
  readonly activeSourceId = signal<string>('plan-md');
  readonly question = signal(DEFAULT_QUESTION);
  readonly answer = signal<AnswerState>(buildMockAnswer(INITIAL_SOURCES[0], DEFAULT_QUESTION));
  readonly importCount = signal(0);

  readonly activeSource = computed<SourceItem>(
    () => this.sources().find((source) => source.id === this.activeSourceId()) ?? INITIAL_SOURCES[0]
  );

  readonly selectedCount = computed(() => this.selectedSourceIds().length);

  setActiveSource(sourceId: string): void {
    const source = this.sources().find((candidate) => candidate.id === sourceId);

    if (!source) {
      return;
    }

    this.activeSourceId.set(sourceId);
    this.answer.set(buildMockAnswer(source, this.question()));
  }

  isSelected(sourceId: string): boolean {
    return this.selectedSourceIds().includes(sourceId);
  }

  setSelected(sourceId: string, checked: boolean): void {
    this.selectedSourceIds.update((selectedIds) => {
      if (checked) {
        return selectedIds.includes(sourceId) ? selectedIds : [...selectedIds, sourceId];
      }

      return selectedIds.filter((id) => id !== sourceId);
    });
  }

  askQuestion(): void {
    const source = this.activeSource();

    if (!source) {
      return;
    }

    const currentQuestion = this.question().trim() || DEFAULT_QUESTION;

    this.question.set(currentQuestion);
    this.answer.set(buildMockAnswer(source, currentQuestion));
  }

  importFile(event: Event): void {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files?.[0];

    if (!file) {
      return;
    }

    const nextImportCount = this.importCount() + 1;
    const newSource = buildImportedSource(file, nextImportCount);

    this.importCount.set(nextImportCount);
    this.sources.update((currentSources) => [newSource, ...currentSources]);
    this.selectedSourceIds.update((selectedIds) =>
      selectedIds.includes(newSource.id) ? selectedIds : [newSource.id, ...selectedIds]
    );
    this.activeSourceId.set(newSource.id);
    this.answer.set(buildMockAnswer(newSource, this.question()));

    input.value = '';
  }

  statusMeta(status: SourceStatus): StatusMeta {
    return STATUS_META[status];
  }
}
