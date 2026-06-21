import { useMutation } from '@tanstack/react-query';
import { askSource } from '../api/askApi';

export function useAsk(sourceId: string) {
  return useMutation({
    mutationFn: (question: string) => askSource(sourceId, question),
  });
}
