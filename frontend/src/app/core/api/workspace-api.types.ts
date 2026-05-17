export interface SourceDto {
  id: string;
  name: string;
  description: string;
  source_type: string;
  import_status: string;
  created_at: string;
  updated_at: string;
}

export interface ImportSourceRequest {
  path: string;
  name?: string | null;
  description?: string | null;
}

export interface ImportSubmissionDto {
  source_id: string;
  job_id: string;
  status: string;
}

export interface ImportJobDto {
  job_id: string;
  source_id: string;
  status: string;
  started_at: string;
  finished_at: string | null;
  error_message: string | null;
}

export interface AskSourceRequest {
  question: string;
}

export interface EvidenceDto {
  chunk_id: string;
  chunk_index: number;
  text: string;
  score: number;
  relative_path?: string | null;
}

export interface AskResponseDto {
  source_id: string;
  question: string;
  answer: string;
  grounding_status: string;
  evidence: EvidenceDto[];
}
