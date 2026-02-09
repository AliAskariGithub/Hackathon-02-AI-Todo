'use client';

import { useScrollProgress } from '@/hooks/useScrollProgress';
import { useReducedMotion } from '@/hooks/useReducedMotion';

/**
 * ScrollProgress component - displays a thin progress bar at the top
 * that fills as the user scrolls down the page
 */
export function ScrollProgress() {
    const progress = useScrollProgress();
    const prefersReducedMotion = useReducedMotion();

    // Don't show for users who prefer reduced motion
    if (prefersReducedMotion) return null;

    return (
        <div
            className="scroll-progress"
            style={{ transform: `scaleX(${progress})` }}
            aria-hidden="true"
        />
    );
}
