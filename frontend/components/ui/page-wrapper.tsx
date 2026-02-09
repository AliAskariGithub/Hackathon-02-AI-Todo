'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';
import { useReducedMotion } from '@/hooks/useReducedMotion';
import { pageVariants } from '@/lib/animations';
import { ScrollProgress } from './ScrollProgress';
import { BackToTop } from './BackToTop';

interface PageWrapperProps {
  children: ReactNode;
  className?: string;
}

export function PageWrapper({ children, className }: PageWrapperProps) {
  const pathname = usePathname();
  const prefersReducedMotion = useReducedMotion();

  const variants = prefersReducedMotion
    ? {
      initial: { opacity: 1 },
      in: { opacity: 1 },
      out: { opacity: 1 },
    }
    : pageVariants;

  return (
    <>
      <ScrollProgress />
      <AnimatePresence mode="wait">
        <motion.div
          key={pathname}
          className={className}
          initial="initial"
          animate="in"
          exit="out"
          variants={variants}
          transition={prefersReducedMotion ? {} : undefined}
        >
          {children}
        </motion.div>
      </AnimatePresence>
      <BackToTop />
    </>
  );
}