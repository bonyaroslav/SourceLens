import { useState } from 'react';
import { useAsk } from '../hooks/useAsk';
import type { EvidenceItem } from '../api/askApi';

interface AskPanelProps {
  sourceId: string;
  isReady: boolean;
}

export function AskPanel({ sourceId, isReady }: AskPanelProps) {
  const [question, setQuestion] = useState('');
  const { mutate, data, isPending, isError, error, reset } = useAsk(sourceId);

  if (!isReady) {
    return (
      <div className="ask-panel__not-ready">
        <span className="ask-panel__not-ready-icon">⏳</span>
        <p>This source is not ready. Import must complete before you can ask questions.</p>
      </div>
    );
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;
    reset();
    mutate(q);
  }

  return (
    <div className="ask-panel">
      <form className="ask-panel__form" onSubmit={handleSubmit}>
        <input
          className="ask-panel__input"
          type="text"
          placeholder="Ask a question about this source…"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isPending}
          aria-label="Question"
        />
        <button
          className="ask-panel__submit"
          type="submit"
          disabled={isPending || !question.trim()}
        >
          {isPending ? 'Asking…' : 'Ask'}
        </button>
      </form>

      {isPending && (
        <div className="ask-panel__loading">
          <span className="ask-panel__spinner" />
          <span>Thinking…</span>
        </div>
      )}

      {isError && (
        <div className="ask-panel__error">
          {error?.message === 'source_not_ready'
            ? 'Source is not ready to answer questions yet.'
            : 'Something went wrong. Please try again.'}
        </div>
      )}

      {data && (
        <div className="ask-panel__result">
          <div className="ask-panel__answer">
            <p className="ask-panel__answer-label">Answer</p>
            <p className="ask-panel__answer-text">{data.answer}</p>
            {data.grounding_status !== 'grounded' && (
              <p className="ask-panel__grounding-warning">
                Confidence: {data.grounding_status.replace(/_/g, ' ')}
              </p>
            )}
          </div>

          {data.evidence.length > 0 && (
            <div className="ask-panel__evidence">
              <p className="ask-panel__evidence-label">Evidence</p>
              <ul className="ask-panel__evidence-list">
                {data.evidence.map((item: EvidenceItem) => (
                  <li key={item.chunk_id} className="ask-panel__evidence-item">
                    {item.relative_path && (
                      <span className="ask-panel__evidence-path">{item.relative_path}</span>
                    )}
                    <p className="ask-panel__evidence-text">{item.text}</p>
                    <span className="ask-panel__evidence-score">
                      Score: {item.score.toFixed(3)}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
