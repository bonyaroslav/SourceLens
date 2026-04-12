export type TagSeverity =
  | 'success'
  | 'secondary'
  | 'info'
  | 'warn'
  | 'danger'
  | 'contrast'
  | null
  | undefined;

export interface SourceListItemViewModel {
  id: string;
  name: string;
  description: string;
  typeLabel: string;
  statusLabel: string;
  statusSeverity: TagSeverity;
  updatedLabel: string;
}

export interface ActiveSourceViewModel {
  id: string;
  name: string;
  description: string;
  typeLabel: string;
  statusLabel: string;
  statusSeverity: TagSeverity;
  createdLabel: string;
  updatedLabel: string;
  isAskable: boolean;
}

export interface ImportPanelViewModel {
  pending: boolean;
  error: string | null;
  statusLabel: string | null;
  statusSeverity: TagSeverity;
  statusDetail: string | null;
  jobId: string | null;
  sourceId: string | null;
}
