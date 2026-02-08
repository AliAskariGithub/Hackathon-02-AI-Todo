'use client'

import { useEffect, useCallback } from 'react'

interface KeyboardShortcutsConfig {
  onFocusChat?: () => void
  onEscape?: () => void
  enabled?: boolean
}

/**
 * Custom hook for managing global keyboard shortcuts in the chat interface
 *
 * Shortcuts:
 * - CMD/Ctrl + K: Focus chat input
 * - Escape: Exit focus mode or blur input
 */
export function useKeyboardShortcuts({
  onFocusChat,
  onEscape,
  enabled = true,
}: KeyboardShortcutsConfig) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return

      // CMD/Ctrl + K: Focus chat input
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault()
        onFocusChat?.()
        return
      }

      // Escape: Exit focus mode or blur input
      if (event.key === 'Escape') {
        event.preventDefault()
        onEscape?.()
        return
      }
    },
    [enabled, onFocusChat, onEscape]
  )

  useEffect(() => {
    if (!enabled) return

    window.addEventListener('keydown', handleKeyDown)

    return () => {
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [enabled, handleKeyDown])
}
