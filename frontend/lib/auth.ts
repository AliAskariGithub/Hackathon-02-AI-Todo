'use client';

import { useAuth } from '@/providers/auth-provider';

// Auth configuration that works with our backend JWT system
export const auth = {};

// Export a session hook that properly handles authentication state
export const useSession = () => {
  const { session, isLoading } = useAuth();

  return {
    data: session,
    isLoading,
    isError: false, // We're not handling errors separately in the context
    isPending: isLoading, // Added to match expected interface
  };
};