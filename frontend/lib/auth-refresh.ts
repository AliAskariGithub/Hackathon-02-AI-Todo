/**
 * Automatic Token Refresh
 *
 * This module handles automatic refresh of access tokens before they expire.
 * Access tokens expire in 15 minutes, so we refresh every 14 minutes to ensure
 * continuous authentication without interrupting the user experience.
 */

let refreshInterval: NodeJS.Timeout | null = null;

/**
 * Check if we're using localStorage tokens (production) vs cookies (local dev)
 */
function isUsingLocalStorageAuth(): boolean {
  if (typeof window === 'undefined') return false;
  return localStorage.getItem('access_token') !== null;
}

/**
 * Refresh the access token by calling the backend refresh endpoint
 * The backend will set a new access_token cookie
 *
 * NOTE: This only works for cookie-based auth (local development).
 * In production with localStorage tokens, refresh is not supported yet.
 */
async function refreshAccessToken(): Promise<boolean> {
  try {
    // Skip refresh if using localStorage tokens (production cross-domain setup)
    if (isUsingLocalStorageAuth()) {
      console.log('[Auth Refresh] Using localStorage tokens, skipping cookie-based refresh');
      return true; // Return true to prevent logout
    }

    const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

    console.log('[Auth Refresh] Attempting to refresh access token...');

    const response = await fetch(`${apiBaseUrl}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include', // Send cookies with request
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (response.ok) {
      console.log('[Auth Refresh] Access token refreshed successfully');
      return true;
    } else {
      console.error('[Auth Refresh] Failed to refresh token:', response.status);
      return false;
    }
  } catch (error) {
    console.error('[Auth Refresh] Error refreshing token:', error);
    return false;
  }
}

/**
 * Handle refresh failure by redirecting to login
 */
function handleRefreshFailure() {
  console.warn('[Auth Refresh] Refresh failed, redirecting to login...');

  // Clear any existing interval
  if (refreshInterval) {
    clearInterval(refreshInterval);
    refreshInterval = null;
  }

  // Redirect to login page
  if (typeof window !== 'undefined') {
    window.location.href = '/login';
  }
}

/**
 * Setup automatic token refresh
 * Refreshes every 14 minutes (access token expires in 15 minutes)
 */
export function setupTokenRefresh() {
  // Don't setup if already running
  if (refreshInterval) {
    console.log('[Auth Refresh] Refresh already setup, skipping...');
    return;
  }

  // Don't setup on server-side
  if (typeof window === 'undefined') {
    return;
  }

  console.log('[Auth Refresh] Setting up automatic token refresh (every 14 minutes)');

  // Refresh every 14 minutes (840,000 milliseconds)
  const REFRESH_INTERVAL = 14 * 60 * 1000;

  refreshInterval = setInterval(async () => {
    const success = await refreshAccessToken();

    if (!success) {
      handleRefreshFailure();
    }
  }, REFRESH_INTERVAL);

  // Also do an initial refresh after 1 minute to ensure token is fresh
  setTimeout(async () => {
    console.log('[Auth Refresh] Performing initial token refresh...');
    await refreshAccessToken();
  }, 60 * 1000);
}

/**
 * Stop automatic token refresh
 * Call this when user logs out or component unmounts
 */
export function stopTokenRefresh() {
  if (refreshInterval) {
    console.log('[Auth Refresh] Stopping automatic token refresh');
    clearInterval(refreshInterval);
    refreshInterval = null;
  }
}

/**
 * Manually trigger a token refresh
 * Useful for testing or when you know the token is about to expire
 */
export async function manualRefresh(): Promise<boolean> {
  console.log('[Auth Refresh] Manual refresh triggered');
  return await refreshAccessToken();
}
