import { useState, useEffect } from 'react';

/**
 * Custom hook that detects user's preference for reduced motion
 * Returns true if the user has requested reduced motion, false otherwise
 */
export function useReducedMotion(): boolean {
  const [matches, setMatches] = useState<boolean>(() => {
    // Check if window is available (client-side only)
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    }
    return false; // Default to false on server
  });

  useEffect(() => {
    // Check if window is available (client-side only)
    if (typeof window !== 'undefined') {
      // Create a media query list for reduced motion
      const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

      // Add listener for changes
      const handleChange = () => setMatches(mediaQuery.matches);
      mediaQuery.addEventListener('change', handleChange);

      // Cleanup listener on unmount
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, []);

  return matches;
}