import { useQuery } from '@tanstack/react-query';
import { fetchSources } from '../api/sourcesApi';

export function useSources() {
  return useQuery({
    queryKey: ['sources'],
    queryFn: fetchSources,
  });
}
