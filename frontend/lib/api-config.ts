/**
 * Automatically resolves the backend API URL.
 * - On localhost: uses http://localhost:8000 (or NEXT_PUBLIC_API_BASE_LOCAL_URL)
 * - In production (e.g. Vercel): uses process.env.NEXT_PUBLIC_API_BASE_URL if set,
 *   or automatically defaults to https://aliaskariface-backend-todo-app.hf.space
 */
export function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_LOCAL_URL;

  // Browser-side resolution
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    const isLocalhost = hostname === 'localhost' || hostname === '127.0.0.1';

    // If running in browser on localhost
    if (isLocalhost) {
      return envUrl || 'http://localhost:8000';
    }

    // If running on a production domain (e.g. ai-y-todo.vercel.app)
    // If envUrl is not configured OR it was inlined with a localhost address, fall back to production Hugging Face
    if (!envUrl || envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
      return 'https://aliaskariface-backend-todo-app.hf.space';
    }

    return envUrl;
  }

  // Server-side (SSR / API routes)
  if (process.env.NODE_ENV === 'production') {
    if (!envUrl || envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
      return 'https://aliaskariface-backend-todo-app.hf.space';
    }
  }

  return envUrl || 'http://localhost:8000';
}
