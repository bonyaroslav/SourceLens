import { Navigate, createBrowserRouter } from 'react-router-dom';
import { RootLayout } from './routes/RootLayout';
import { WorkspaceRoute } from '../features/workspace/routes/WorkspaceRoute';

export const appRouter = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <Navigate to="/workspace" replace />,
      },
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
]);
