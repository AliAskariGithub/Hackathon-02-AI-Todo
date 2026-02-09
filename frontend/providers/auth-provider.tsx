'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import apiClient from '@/services/api-client';

interface User {
  id: string;
  email: string;
  name?: string;
  user_name?: string;
}

interface AuthContextType {
  session: {
    user: { id: string; email: string; name?: string };
  } | null;
  isLoading: boolean;
  login: (userData: User) => void;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<{
    user: { id: string; email: string; name?: string };
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize session by checking with backend
    // Cookies are automatically sent with the request
    const initializeSession = async () => {
      try {
        // Try to fetch current user info (will use cookie for auth)
        // If cookie is valid, backend will return user info
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/users/me`, {
          credentials: 'include'
        });

        if (response.ok) {
          const userData = await response.json();
          setSession({
            user: {
              id: userData.id,
              email: userData.email,
              name: userData.user_name || userData.name
            }
          });
        } else {
          // No valid session
          setSession(null);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        setSession(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeSession();
  }, []);

  const login = (userData: User) => {
    // Update session state with user data from login response
    // Cookies are already set by the backend
    setSession({
      user: {
        id: userData.id,
        email: userData.email,
        name: userData.user_name || userData.name
      }
    });
  };

  const logout = async () => {
    try {
      // Call backend logout endpoint to clear cookies
      await apiClient.post('/api/auth/logout', {});
    } catch (error) {
      console.error('Error during logout:', error);
    } finally {
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