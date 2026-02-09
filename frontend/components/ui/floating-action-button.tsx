'use client';

import { motion } from 'framer-motion';
import { Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useReducedMotion } from '@/hooks/useReducedMotion';

interface FloatingActionButtonProps {
  onClick: () => void;
  icon?: React.ReactNode;
  label?: string;
  className?: string;
}

export function FloatingActionButton({
  onClick,
  icon,
  label = 'Add',
  className = ''
}: FloatingActionButtonProps) {
  const prefersReducedMotion = useReducedMotion();

  return (
    <motion.div
      initial={{ scale: 0, y: 50 }}
      animate={{ scale: 1, y: 0 }}
      transition={
        prefersReducedMotion
          ? { duration: 0 }
          : {
            type: 'spring',
            stiffness: 300,
            damping: 25,
            mass: 1
          }
      }
      whileHover={prefersReducedMotion ? {} : {
        scale: 1.1,
        transition: { duration: 0.2 }
      }}
      whileTap={prefersReducedMotion ? {} : {
        scale: 0.95,
        transition: { duration: 0.1 }
      }}
      className="fixed bottom-8 right-8 z-50 group"
    >
      {/* Pulse Rings */}
      {!prefersReducedMotion && (
        <>
          <span className="absolute inset-0 rounded-full bg-primary/30 animate-ping-slow pointer-events-none" />
          <span className="absolute inset-0 rounded-full bg-primary/20 animate-pulse pointer-events-none" />
        </>
      )}

      <Button
        onClick={onClick}
        size="lg"
        className={`rounded-full w-14 h-14 p-0 shadow-lg shadow-primary/30 border border-white/20 relative z-10 bg-primary hover:bg-primary/90 ${className}`}
        aria-label={label}
      >
        {icon || <Plus className="h-6 w-6 text-primary-foreground" />}
      </Button>

    </motion.div>
  );
}