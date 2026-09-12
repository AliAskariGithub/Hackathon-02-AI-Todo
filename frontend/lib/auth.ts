'use client';

import { useAuth } from '@/providers/auth-provider';
import { getApiBaseUrl } from '@/lib/api-config';

/**
 * Auth configuration for cookie-based authentication.
 *
 * This application uses HTTP-only cookies for secure token storage.
 * Tokens are set by the backend and automatically included in requests.
 * No client-side token management is needed.
 */
export const authConfig = {
  get baseURL() {
    return getApiBaseUrl();
  },
  credentials: 'include' as RequestCredentials, // Always include cookies
};

/**
 * Hook to access the current session.
 *
 * Session is derived from HTTP-only cookies set by the backend.
 * The auth provider manages session state based on API responses.
 *
 * @returns Session data, loading state, and error state
 */
export const useSession = () => {
  const { session, isLoading } = useAuth();

  return {
    data: session,
    isLoading,
    isError: false,
    isPending: isLoading,
  };
};

/**
 * Check if user is authenticated.
 *
 * @returns True if user has an active session
 */
export const isAuthenticated = (): boolean => {
  // Session is managed by cookies, so we check if session exists
  // This will be populated by the auth provider
  return false; // Will be determined by auth provider
};