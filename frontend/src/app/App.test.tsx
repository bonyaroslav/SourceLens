import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { RootLayout } from './routes/RootLayout';
import { WorkspaceRoute } from '../features/workspace/routes/WorkspaceRoute';

const MOCK_SOURCES = [
  {
    id: 'abc-123',
    name: 'Test Source',
    description: 'A test source',
    source_type: 'file',
    import_status: 'completed',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

function renderApp(initialEntry = '/workspace') {
  const router = createMemoryRouter(
    [
      {
        path: '/',
        element: <RootLayout />,
        children: [
          {
            path: 'workspace',
            children: [
              {
                index: true,
                element: <WorkspaceRoute />,
              },
              {
                path: ':sourceId',
                element: <WorkspaceRoute />,
              },
            ],
          },
        ],
      },
    ],
    { initialEntries: [initialEntry] },
  );

  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <RouterProvider router={router} />
    </QueryClientProvider>,
  );
}

describe('workspace', () => {
  beforeEach(() => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(MOCK_SOURCES),
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('shows loading state then renders source list', async () => {
    renderApp();

    expect(screen.getByLabelText('Loading sources')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Test Source')).toBeInTheDocument();
    });
  });

  it('shows empty selection prompt with no sourceId', async () => {
    renderApp();

    await waitFor(() => {
      expect(screen.getByText('Select a source')).toBeInTheDocument();
    });
  });

  it('shows source detail when sourceId is in the URL', async () => {
    renderApp('/workspace/abc-123');

    await waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Test Source' })).toBeInTheDocument();
    });

    expect(screen.getByText('Selected source')).toBeInTheDocument();
  });

  it('shows error state when fetch fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
      }),
    );

    renderApp();

    await waitFor(() => {
      expect(screen.getByText('Could not load sources.')).toBeInTheDocument();
    });
  });
});
