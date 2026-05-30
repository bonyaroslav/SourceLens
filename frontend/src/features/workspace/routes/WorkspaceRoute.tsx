import { Link, useLocation, useParams } from 'react-router-dom';
import { sourceLensApiBaseUrl } from '../../../shared/config/api';
import { ShellPanel } from '../components/ShellPanel';

const apiContracts = [
  'GET /health',
  'GET /sources',
  'GET /sources/{source_id}',
  'POST /sources/import',
  'GET /import-jobs/{job_id}',
  'POST /sources/{source_id}/ask',
];

export function WorkspaceRoute() {
  const { pathname } = useLocation();
  const { sourceId } = useParams();

  return (
    <main className="workspace-shell">
      <div className="workspace-shell__hero">
        <p className="workspace-shell__eyebrow">Source Lens MVP</p>
        <h1>React workspace shell</h1>
        <p className="workspace-shell__intro">
          This React + Vite workspace is the current frontend foundation for the single-source
          grounded QA flow.
        </p>
        <div className="workspace-shell__actions">
          <Link
            className="workspace-shell__action workspace-shell__action--primary"
            to="/workspace"
          >
            Workspace root
          </Link>
          <Link
            className="workspace-shell__action"
            to={sourceId ? '/workspace' : '/workspace/sample-source'}
          >
            {sourceId ? 'Clear source route' : 'Preview source route'}
          </Link>
        </div>
      </div>

      <div className="workspace-shell__grid">
        <ShellPanel
          eyebrow="Backend seam"
          title="Python API remains the contract"
          body="Follow-on slices wire real source loading and ask behavior through this seam without widening the current MVP."
        >
          <dl className="detail-list">
            <div>
              <dt>API base URL</dt>
              <dd>{sourceLensApiBaseUrl}</dd>
            </div>
            <div>
              <dt>Current route</dt>
              <dd>{pathname}</dd>
            </div>
            <div>
              <dt>Selected source route</dt>
              <dd>{sourceId ?? 'none selected yet'}</dd>
            </div>
          </dl>
        </ShellPanel>

        <ShellPanel
          eyebrow="Feature structure"
          title="Workspace slices now have clear ownership"
          body="The app is organized around the workspace feature so source loading, ask flow, and evidence UI can land as focused vertical slices."
        >
          <ul className="bullet-list">
            <li>`src/app` owns app-wide providers and routing.</li>
            <li>`src/features/workspace` owns the MVP shell and follow-on workspace slices.</li>
            <li>`src/shared` holds stable config shared across features.</li>
          </ul>
        </ShellPanel>

        <ShellPanel
          eyebrow="Route plan"
          title="Small, source-aware route surface"
          body="The shell keeps the route structure intentionally small while leaving room for the selected-source workflow."
        >
          <ul className="bullet-list">
            <li>`/workspace` for the root workspace shell.</li>
            <li>`/workspace/:sourceId` for selected-source context in later slices.</li>
          </ul>
        </ShellPanel>

        <ShellPanel
          eyebrow="Next API wiring"
          title="Ready for source list and ask slices"
          body="React Router and TanStack Query are already in place so the remaining workspace slices can focus on user-visible state instead of platform churn."
        >
          <ul className="contract-list">
            {apiContracts.map((contract) => (
              <li key={contract}>{contract}</li>
            ))}
          </ul>
        </ShellPanel>
      </div>
    </main>
  );
}
