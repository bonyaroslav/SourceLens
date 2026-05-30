const defaultApiBaseUrl = 'http://127.0.0.1:8000';

export const sourceLensApiBaseUrl =
  import.meta.env.VITE_SOURCE_LENS_API_BASE_URL?.trim() || defaultApiBaseUrl;
