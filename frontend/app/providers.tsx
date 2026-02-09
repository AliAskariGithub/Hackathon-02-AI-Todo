'use client';

import { ThemeProvider } from 'next-themes';
import { ReactNode } from 'react';
import { AuthProvider } from '@/providers/auth-provider';
import { AuthRefreshProvider } from '@/providers/auth-refresh-provider';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem disableTransitionOnChange>
      <AuthProvider>
        <AuthRefreshProvider>
          {children}
        </AuthRefreshProvider>
      </AuthProvider>
    </ThemeProvider>
  );
}