'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import apiClient from '@/services/api-client';
import { getApiBaseUrl } from '@/lib/api-config';

interface User {
  id: string;
  email: string;
  name?: string;
  user_name?: string;
}

interface AuthContextType {
  session: {
    user: { id: string; email: string; name?: string };
    token?: string;
  } | null;
  isLoading: boolean;
  login: (userData: User, token?: string) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<{
    user: { id: string; email: string; name?: string };
    token?: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize session by checking with backend
    const initializeSession = async () => {
      try {
        // Check for token in localStorage (for cross-domain auth)
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');

        // Prepare headers with token if available
        const headers: HeadersInit = {
          'Content-Type': 'application/json'
        };

        if (token) {
          headers['Authorization'] = `Bearer ${token}`;
        }

        // Try to fetch current user info
        const response = await fetch(`${getApiBaseUrl()}/api/users/me`, {
          credentials: 'include', // Still include cookies for local development
          headers
        });

        if (response.ok) {
          const userData = await response.json();
          const effectiveToken = userData.access_token || token || undefined;
          if (effectiveToken) {
            localStorage.setItem('access_token', effectiveToken);
            localStorage.setItem('token', effectiveToken);
          }
          setSession({
            user: {
              id: userData.id,
              email: userData.email,
              name: userData.user_name || userData.name
            },
            token: effectiveToken
          });
        } else {
          // No valid session - clear any stale token
          localStorage.removeItem('access_token');
          localStorage.removeItem('token');
          setSession(null);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        localStorage.removeItem('access_token');
        localStorage.removeItem('token');
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []);

  const login = (userData: User, token?: string) => {
    if (token) {
      localStorage.setItem('access_token', token);
      localStorage.setItem('token', token);
    }
    // Update session state with user data from login response
    // Cookies are already set by the backend
    setSession({
      user: {
        id: userData.id,
        email: userData.email,
        name: userData.user_name || userData.name
      },
      token: token || undefined
    });
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint to clear cookies
      await apiClient.post('/api/auth/logout', {});
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
      // Clear token from localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('token');
      // Clear session state regardless of API call result
      setSession(null);
    }
  };

  return (
    <AuthContext.Provider value={{ session, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}