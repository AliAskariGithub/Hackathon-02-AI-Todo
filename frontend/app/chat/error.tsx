'use client'

import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Home, RefreshCw } from 'lucide-react'
import { Button } from '@/components/ui/button'

/**
 * Error boundary for chat page
 * Catches and displays errors gracefully with animations
 */
export default function ChatError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('Chat error:', error)
  }, [error])

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 sm:p-6 md:p-8">
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="flex flex-col items-center text-center max-w-md w-full"
      >
        {/* Error Icon */}
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
          className="mb-6"
        >
          <div className="relative">
            <motion.div
              animate={{ 
                scale: [1, 1.2, 1],
                opacity: [0.5, 0.2, 0.5]
              }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute inset-0 bg-destructive/20 rounded-full blur-xl"
            />
            <div className="relative bg-destructive/10 p-4 sm:p-5 rounded-full">
              <AlertCircle className="h-12 w-12 sm:h-14 sm:w-14 md:h-16 md:w-16 text-destructive" />
            </div>
          </div>
        </motion.div>

        {/* Error Message */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="space-y-2 sm:space-y-3 mb-6 sm:mb-8"
        >
          <h2 className="text-xl sm:text-2xl md:text-3xl font-semibold bg-gradient-to-r from-foreground to-foreground/60 bg-clip-text text-transparent">
            Something went wrong
          </h2>
          <p className="text-sm sm:text-base text-muted-foreground px-4">
            The chat interface encountered an error. Please try again or return to the dashboard.
          </p>
          
          {/* Error Details (for development) */}
          {process.env.NODE_ENV === 'development' && error.message && (
            <motion.details
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-4 text-left"
            >
              <summary className="cursor-pointer text-xs sm:text-sm text-muted-foreground hover:text-foreground transition-colors">
                Technical details
              </summary>
              <div className="mt-2 p-3 sm:p-4 bg-muted/50 rounded-lg border text-xs font-mono overflow-auto max-h-32">
                {error.message}
              </div>
            </motion.details>
          )}
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex flex-col sm:flex-row gap-3 w-full px-4 sm:px-0"
        >
          <Button 
            onClick={reset}
            size="lg"
            className="flex-1 gap-2 h-11 sm:h-12 text-sm sm:text-base"
          >
            <RefreshCw className="h-4 w-4" />
            Try Again
          </Button>
          <Button 
            variant="outline" 
            onClick={() => window.location.href = '/dashboard'}
            size="lg"
            className="flex-1 gap-2 h-11 sm:h-12 text-sm sm:text-base"
          >
            <Home className="h-4 w-4" />
            Go to Dashboard
          </Button>
        </motion.div>

        {/* Help Text */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-6 sm:mt-8 text-xs sm:text-sm text-muted-foreground"
        >
          If the problem persists, please contact support
        </motion.p>
      </motion.div>
    </div>
  )
}