// Runtime configuration override for Docker deployment
// This allows overriding build-time environment variables
window.__RUNTIME_CONFIG__ = {
  NEXT_PUBLIC_API_BASE_URL: 'http://localhost:8000',
  NEXT_PUBLIC_BACKEND_URL: 'http://localhost:8000',
  NEXT_PUBLIC_SITE_URL: 'http://localhost:3000'
};
