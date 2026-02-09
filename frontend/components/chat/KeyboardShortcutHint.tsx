'use client'

import { Kbd } from '@/components/ui/kbd'
import { cn } from '@/lib/utils'

interface KeyboardShortcutHintProps {
  keys: string[]
  description: string
  className?: string
}

/**
 * Component to display keyboard shortcut hints with visual indicators
 * Uses the Kbd component to show keyboard keys in a styled format
 */
export function KeyboardShortcutHint({
  keys,
  description,
  className,
}: KeyboardShortcutHintProps) {
  return (
    <div
      className={cn(
        'hidden sm:flex items-center gap-2 text-xs text-muted-foreground',
        className
      )}
    >
      <span>{description}</span>
      <div className="flex items-center gap-1">
        {keys.map((key, index) => (
          <span key={index} className="flex items-center gap-1">
            <Kbd>{key}</Kbd>
            {index < keys.length - 1 && (
              <span className="text-muted-foreground">+</span>
            )}
          </span>
        ))}
      </div>
    </div>
  )
}

/**
 * Preset keyboard shortcut hints for common actions
 */
export const KeyboardShortcuts = {
  FocusChat: () => (
    <KeyboardShortcutHint
      keys={[navigator.platform.includes('Mac') ? '⌘' : 'Ctrl', 'K']}
      description="Focus chat"
    />
  ),
  SendMessage: () => (
    <KeyboardShortcutHint keys={['Enter']} description="Send message" />
  ),
  NewLine: () => (
    <KeyboardShortcutHint
      keys={['Shift', 'Enter']}
      description="New line"
    />
  ),
  ExitFocus: () => (
    <KeyboardShortcutHint keys={['Esc']} description="Exit focus mode" />
  ),
}
