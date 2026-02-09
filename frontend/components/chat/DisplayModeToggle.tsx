'use client'

import { Monitor, Code2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUIStore } from '@/stores/ui-store'
import { cn } from '@/lib/utils'

interface DisplayModeToggleProps {
  className?: string
}

/**
 * Toggle button for switching between Human and JSON display modes
 * Persists preference to localStorage via Zustand store
 */
export function DisplayModeToggle({ className }: DisplayModeToggleProps) {
  const { displayMode, toggleDisplayMode } = useUIStore()

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleDisplayMode}
      className={cn('gap-2', className)}
      aria-label={`Switch to ${displayMode === 'json' ? 'human' : 'JSON'} mode`}
      aria-pressed={displayMode === 'json'}
    >
      {displayMode === 'json' ? (
        <>
          <Monitor className="h-4 w-4" />
          <span className="hidden sm:inline">Human</span>
        </>
      ) : (
        <>
          <Code2 className="h-4 w-4" />
          <span className="hidden sm:inline">JSON</span>
        </>
      )}
    </Button>
  )
}
