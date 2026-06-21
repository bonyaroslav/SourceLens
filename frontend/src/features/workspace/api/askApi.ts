import { sourceLensApiBaseUrl } from '../../../shared/config/api';

export interface EvidenceItem {
  chunk_id: string;
  chunk_index: number;
  text: string;
  score: number;
  relative_path: string | null;
}

export interface AskResponse {
  source_id: string;
  question: string;
  answer: string;
  grounding_status: string;
  evidence: EvidenceItem[];
}

export async function askSource(sourceId: string, question: string): Promise<AskResponse> {
  const response = await fetch(`${sourceLensApiBaseUrl}/sources/${sourceId}/ask`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  });

  if (response.status === 409) throw new Error('source_not_ready');
  if (response.status === 404) throw new Error('source_not_found');
  if (!response.ok) throw new Error(`POST /sources/${sourceId}/ask failed: ${response.status}`);

  return response.json();
}
