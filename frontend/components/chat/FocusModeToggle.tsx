'use client'

import { Maximize2, Minimize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Kbd } from '@/components/ui/kbd'
import { useUIStore } from '@/stores/ui-store'
import { cn } from '@/lib/utils'

interface FocusModeToggleProps {
  className?: string
}

/**
 * Toggle button for Focus Mode
 * Displays current state and keyboard shortcut hint
 */
export function FocusModeToggle({ className }: FocusModeToggleProps) {
  const { focusMode, toggleFocusMode } = useUIStore()

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={toggleFocusMode}
      className={cn('gap-2', className)}
      aria-label={focusMode ? 'Exit focus mode' : 'Enter focus mode'}
      aria-pressed={focusMode}
    >
      {focusMode ? (
        <>
          <Minimize2 className="h-4 w-4" />
          <span className="hidden sm:inline">Exit Focus</span>
        </>
      ) : (
        <>
          <Maximize2 className="h-4 w-4" />
          <span className="hidden sm:inline">Focus Mode</span>
        </>
      )}
      <Kbd className="hidden md:inline-flex">Esc</Kbd>
    </Button>
  )
}
