import { sourceLensApiBaseUrl } from '../../../shared/config/api';
import type { Source } from './types';

export async function fetchSources(): Promise<Source[]> {
  const response = await fetch(`${sourceLensApiBaseUrl}/sources`);
  if (!response.ok) throw new Error(`GET /sources failed: ${response.status}`);
  return response.json();
}
