import { useParams } from 'react-router-dom';
import { SourceList } from '../components/SourceList';
import { useSources } from '../hooks/useSources';

function SourceDetail({ sourceId }: { sourceId: string }) {
  const { data: sources } = useSources();
  const source = sources?.find((s) => s.id === sourceId);

  return (
    <div className="workspace-content">
      <p className="workspace-content__eyebrow">Selected source</p>
      <h2 className="workspace-content__title">{source?.name ?? sourceId}</h2>
      {source && (
        <dl className="workspace-content__meta">
          <div>
            <dt>Status</dt>
            <dd>{source.import_status}</dd>
          </div>
          <div>
            <dt>Type</dt>
            <dd>{source.source_type}</dd>
          </div>
          {source.description && (
            <div>
              <dt>Description</dt>
              <dd>{source.description}</dd>
            </div>
          )}
        </dl>
      )}
      <div className="workspace-content__ask-placeholder">
        Ask flow coming in issue #19
      </div>
    </div>
  );
}

function EmptySelection() {
  return (
    <div className="workspace-content workspace-content--empty">
      <p className="workspace-content__eyebrow">Source Lens</p>
      <h2 className="workspace-content__title">Select a source</h2>
      <p className="workspace-content__hint">
        Choose a source from the list to start asking questions.
      </p>
    </div>
  );
}

export function WorkspaceRoute() {
  const { sourceId } = useParams<{ sourceId: string }>();

  return (
    <div className="workspace">
      <aside className="workspace__sidebar">
        <SourceList />
      </aside>
      <main className="workspace__content">
        {sourceId ? <SourceDetail sourceId={sourceId} /> : <EmptySelection />}
      </main>
    </div>
  );
}
