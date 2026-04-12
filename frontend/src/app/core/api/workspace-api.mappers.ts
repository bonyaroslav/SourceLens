import { ImportJobDto, ImportSubmissionDto, SourceDto } from './workspace-api.types';
import {
  ActiveSourceViewModel,
  ImportPanelViewModel,
  SourceListItemViewModel,
  TagSeverity
} from '../../workspace/workspace.models';

interface StatusMeta {
  label: string;
  severity: TagSeverity;
}

const SOURCE_TYPE_LABELS: Record<string, string> = {
  local_file: 'Local file',
  local_folder: 'Local folder'
};

const SOURCE_STATUS_META: Record<string, StatusMeta> = {
  queued: { label: 'Queued', severity: 'info' },
  running: { label: 'Indexing', severity: 'info' },
  completed: { label: 'Ready', severity: 'success' },
  failed: { label: 'Failed', severity: 'danger' }
};

export function toSourceListItemViewModel(source: SourceDto): SourceListItemViewModel {
  const status = toSourceStatusMeta(source.import_status);

  return {
    id: source.id,
    name: source.name,
    description: source.description || 'No description provided yet.',
    typeLabel: toSourceTypeLabel(source.source_type),
    statusLabel: status.label,
    statusSeverity: status.severity,
    updatedLabel: `Updated ${formatDateTime(source.updated_at)}`
  };
}

export function toActiveSourceViewModel(source: SourceDto): ActiveSourceViewModel {
  const status = toSourceStatusMeta(source.import_status);

  return {
    id: source.id,
    name: source.name,
    description: source.description || 'No description provided yet.',
    typeLabel: toSourceTypeLabel(source.source_type),
    statusLabel: status.label,
    statusSeverity: status.severity,
    createdLabel: formatDateTime(source.created_at),
    updatedLabel: formatDateTime(source.updated_at),
    isAskable: source.import_status === 'completed'
  };
}

export function toImportPanelViewModel(
  activeSubmission: ImportSubmissionDto | null,
  activeJob: ImportJobDto | null,
  error: string | null,
  pending: boolean
): ImportPanelViewModel {
  const currentStatus = activeJob?.status ?? activeSubmission?.status ?? null;
  const status = currentStatus ? toSourceStatusMeta(currentStatus) : null;
  const statusDetail =
    activeJob !== null
      ? activeJob.error_message ??
        `Job ${activeJob.job_id} started ${formatDateTime(activeJob.started_at)}.`
      : activeSubmission !== null
        ? `Job ${activeSubmission.job_id} accepted for source ${activeSubmission.source_id}.`
        : null;

  return {
    pending,
    error,
    statusLabel: status?.label ?? null,
    statusSeverity: status?.severity ?? null,
    statusDetail,
    jobId: activeJob?.job_id ?? activeSubmission?.job_id ?? null,
    sourceId: activeJob?.source_id ?? activeSubmission?.source_id ?? null
  };
}

export function toSourceTypeLabel(sourceType: string): string {
  return SOURCE_TYPE_LABELS[sourceType] ?? sourceType.replace(/_/g, ' ');
}

export function toSourceStatusMeta(status: string): StatusMeta {
  return SOURCE_STATUS_META[status] ?? { label: status, severity: 'secondary' };
}

export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat([], {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(new Date(value));
}
