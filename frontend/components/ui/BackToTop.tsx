'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUp } from 'lucide-react';
import { useReducedMotion } from '@/hooks/useReducedMotion';

/**
 * BackToTop component - floating button that appears after scrolling
 * and smoothly scrolls to the top when clicked
 */
export function BackToTop() {
    const [isVisible, setIsVisible] = useState(false);
    const prefersReducedMotion = useReducedMotion();

    useEffect(() => {
        const toggleVisibility = () => {
            // Show button when page is scrolled past 50% of viewport height
            const scrolled = window.scrollY;
            const threshold = window.innerHeight * 0.5;
            setIsVisible(scrolled > threshold);
        };

        // Initial check
        toggleVisibility();

        // Throttled scroll handler
        let ticking = false;
        const handleScroll = () => {
            if (!ticking) {
                window.requestAnimationFrame(() => {
                    toggleVisibility();
                    ticking = false;
                });
                ticking = true;
            }
        };

        window.addEventListener('scroll', handleScroll, { passive: true });
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: prefersReducedMotion ? 'auto' : 'smooth',
        });
    };

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.button
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    transition={{ duration: prefersReducedMotion ? 0 : 0.3 }}
                    onClick={scrollToTop}
                    className="back-to-top"
                    aria-label="Back to top"
                >
                    <ArrowUp className="h-5 w-5" />
                </motion.button>
            )}
        </AnimatePresence>
    );
}
