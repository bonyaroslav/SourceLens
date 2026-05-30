import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { RootLayout } from './routes/RootLayout';
import { WorkspaceRoute } from '../features/workspace/routes/WorkspaceRoute';

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

describe('workspace shell', () => {
  it('renders the React workspace route', () => {
    renderApp();

    expect(
      screen.getByRole('heading', {
        name: 'React workspace shell',
      }),
    ).toBeInTheDocument();
    expect(screen.getByText('Backend seam')).toBeInTheDocument();
  });

  it('keeps the source-aware route when a source id is present', () => {
    renderApp('/workspace/source-123');

    expect(screen.getByText('Current route')).toBeInTheDocument();
    expect(screen.getByText('/workspace/source-123')).toBeInTheDocument();
  });
});
