'use client';

import { useState, useEffect, createContext, useContext, ReactNode } from 'react';

interface AuthContextType {
  session: {
    user: { id: string; email: string; name?: string };
    session?: { token: string };
  } | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<{
    user: { id: string; email: string; name?: string };
    session?: { token: string };
  } | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Initialize session from localStorage on mount
    const initializeSession = () => {
      const token = localStorage.getItem('auth-token');

      if (token) {
        try {
          // Decode JWT token to get user info
          const tokenParts = token.split('.');
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            setSession({
              user: {
                id: payload.sub,
                email: payload.email || 'unknown@example.com',
                name: payload.name || payload.email?.split('@')[0] || 'User'
              },
              session: { token } // Include the token in the session object
            });
          }
        } catch (error) {
          console.error('Error decoding token:', error);
        }
      } else {
        setSession(null);
      }
      setIsLoading(false);
    };

    // Initialize on mount
    initializeSession();

    // Listen for storage events (when token is updated in another tab or component)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth-token') {
        initializeSession();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    // Cleanup
    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const login = (token: string) => {
    const previousToken = localStorage.getItem('auth-token');
    localStorage.setItem('auth-token', token);

    try {
      // Decode JWT token to get user info
      const tokenParts = token.split('.');
      if (tokenParts.length === 3) {
        const payload = JSON.parse(atob(tokenParts[1]));
        setSession({
          user: {
            id: payload.sub,
            email: payload.email || 'unknown@example.com',
            name: payload.name || payload.email?.split('@')[0] || 'User'
          },
          session: { token }
        });
      }
    } catch (error) {
      console.error('Error decoding token:', error);
    }

    // Dispatch storage event to notify other tabs/components
    if (previousToken !== token) {
      window.dispatchEvent(new StorageEvent('storage', {
        key: 'auth-token',
        oldValue: previousToken,
        newValue: token,
        url: window.location.href,
        storageArea: localStorage,
      }));
    }
  };

  const logout = () => {
    const previousToken = localStorage.getItem('auth-token');
    localStorage.removeItem('auth-token');
    setSession(null);

    // Dispatch storage event to notify other tabs/components
    if (previousToken !== null) {
      window.dispatchEvent(new StorageEvent('storage', {
        key: 'auth-token',
        oldValue: previousToken,
        newValue: null,
        url: window.location.href,
        storageArea: localStorage,
      }));
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