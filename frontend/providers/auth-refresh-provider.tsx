'use client';

import { useEffect } from 'react';
import { useAuth } from '@/providers/auth-provider';
import { setupTokenRefresh, stopTokenRefresh } from '@/lib/auth-refresh';

/**
 * AuthRefreshProvider
 *
 * This component initializes automatic token refresh when a user is logged in.
 * It sets up a 14-minute interval to refresh the access token before it expires.
 */
export function AuthRefreshProvider({ children }: { children: React.ReactNode }) {
  const { session, isLoading } = useAuth();

  useEffect(() => {
    // Only setup refresh if user is logged in
    if (!isLoading && session?.user) {
      console.log('[AuthRefreshProvider] User logged in, setting up token refresh');
      setupTokenRefresh();

      // Cleanup on unmount or when user logs out
      return () => {
        console.log('[AuthRefreshProvider] Cleaning up token refresh');
        stopTokenRefresh();
      };
    } else if (!isLoading && !session) {
      // User is not logged in, ensure refresh is stopped
      console.log('[AuthRefreshProvider] No user session, stopping token refresh');
      stopTokenRefresh();
    }
  }, [session, isLoading]);

  return <>{children}</>;
}
