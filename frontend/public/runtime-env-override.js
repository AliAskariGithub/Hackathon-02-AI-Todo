// Runtime environment override for Docker deployment
// This script overrides Next.js build-time environment variables at runtime
(function() {
  // Store original fetch
  const originalFetch = window.fetch;
  
  // Override fetch to replace Docker internal DNS with localhost
  window.fetch = function(url, options) {
    if (typeof url === 'string') {
      // Replace Docker internal DNS with localhost for browser access
      url = url.replace('http://localhost:8000', 'http://localhost:8000');
    } else if (url instanceof Request) {
      // Handle Request objects
      const originalUrl = url.url;
      const newUrl = originalUrl.replace('http://localhost:8000', 'http://localhost:8000');
      if (newUrl !== originalUrl) {
        url = new Request(newUrl, url);
      }
    }
    return originalFetch.call(this, url, options);
  };
  
  console.log('[Runtime Override] API calls will be redirected from http://localhost:8000 to http://localhost:8000');
})();
