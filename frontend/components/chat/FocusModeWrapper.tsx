'use client'

import { ReactNode, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useUIStore } from '@/stores/ui-store'
import { focusModeOverlay, focusModeContent } from '@/lib/animations'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { cn } from '@/lib/utils'

interface FocusModeWrapperProps {
  children: ReactNode
}

/**
 * Wrapper component that handles Focus Mode layout and animations
 * When active, centers content and fades out background elements
 */
export function FocusModeWrapper({
  children,
}: FocusModeWrapperProps) {
  const { focusMode } = useUIStore()
  const prefersReducedMotion = useReducedMotion()

  // Prevent body scroll when focus mode is active
  useEffect(() => {
    if (focusMode) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }

    return () => {
      document.body.style.overflow = ''
    }
  }, [focusMode])

  if (!focusMode) {
    return <>{children}</>
  }

  return (
    <AnimatePresence mode="wait">
      {focusMode && (
        <motion.div
          role="dialog"
          aria-modal="true"
          aria-label="Focus mode"
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={prefersReducedMotion ? false : 'hidden'}
          animate="visible"
          exit="hidden"
        >
          {/* Backdrop overlay */}
          <motion.div
            variants={prefersReducedMotion ? undefined : focusModeOverlay}
            className="absolute inset-0 bg-background/95 backdrop-blur-sm"
            aria-hidden="true"
          />

          {/* Centered content */}
          <motion.div
            variants={prefersReducedMotion ? undefined : focusModeContent}
            className={cn(
              'relative z-10 w-full max-w-5xl',
              'h-[90vh] sm:h-[85vh]',
              'mx-2 sm:mx-4 rounded-lg border bg-background shadow-2xl',
              'flex flex-col overflow-hidden'
            )}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
