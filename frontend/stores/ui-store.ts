'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  focusMode: boolean
  displayMode: 'json' | 'human'
  toggleFocusMode: () => void
  toggleDisplayMode: () => void
  setFocusMode: (value: boolean) => void
  setDisplayMode: (mode: 'json' | 'human') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      focusMode: false,
      displayMode: 'human',
      toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),
      toggleDisplayMode: () => set((state) => ({
        displayMode: state.displayMode === 'json' ? 'human' : 'json'
      })),
      setFocusMode: (value) => set({ focusMode: value }),
      setDisplayMode: (mode) => set({ displayMode: mode }),
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({ displayMode: state.displayMode }), // Only persist displayMode
    }
  )
)
