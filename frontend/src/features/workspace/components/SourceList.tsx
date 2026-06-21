import { NavLink } from 'react-router-dom';
import { useSources } from '../hooks/useSources';
import type { Source } from '../api/types';

const STATUS_LABELS: Record<string, string> = {
  completed: 'Ready',
  failed: 'Failed',
  pending: 'Pending',
  processing: 'Processing',
};

function statusLabel(status: string): string {
  return STATUS_LABELS[status] ?? status;
}

function SourceItem({ source }: { source: Source }) {
  return (
    <NavLink
      to={`/workspace/${source.id}`}
      className={({ isActive }) =>
        ['source-item', isActive ? 'source-item--selected' : ''].filter(Boolean).join(' ')
      }
    >
      <span className="source-item__name">{source.name}</span>
      <span className={`source-item__status source-item__status--${source.import_status}`}>
        {statusLabel(source.import_status)}
      </span>
    </NavLink>
  );
}

export function SourceList() {
  const { data: sources, isLoading, isError, error } = useSources();

  return (
    <div className="source-list">
      <div className="source-list__header">
        <p className="source-list__eyebrow">Sources</p>
      </div>

      {isLoading && (
        <div className="source-list__state">
          <span className="source-list__spinner" aria-label="Loading sources" />
          <p>Loading sources…</p>
        </div>
      )}

      {isError && (
        <div className="source-list__state source-list__state--error">
          <p>Could not load sources.</p>
          <p className="source-list__error-detail">
            {error instanceof Error ? error.message : 'Unknown error'}
          </p>
        </div>
      )}

      {!isLoading && !isError && sources?.length === 0 && (
        <div className="source-list__state">
          <p>No sources yet.</p>
          <p className="source-list__hint">Import a source to get started.</p>
        </div>
      )}

      {sources && sources.length > 0 && (
        <ul className="source-list__items">
          {sources.map((source) => (
            <li key={source.id}>
              <SourceItem source={source} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
