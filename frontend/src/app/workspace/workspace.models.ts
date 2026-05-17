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

export interface AskResultViewModel {
  sourceId: string;
  question: string;
  answer: string;
  groundingStatus: string;
  groundingLabel: string;
  groundingSeverity: TagSeverity;
}

export interface EvidenceItemViewModel {
  chunkId: string;
  chunkIndex: number;
  text: string;
  score: number;
  relativePath: string | null;
}
