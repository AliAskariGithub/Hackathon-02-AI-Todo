# Research Findings: Interactive Chat Experience

**Feature**: 008-todo-interactive-chat
**Date**: 2026-02-08
**Status**: Complete

## Overview

This document consolidates research findings for implementing the Interactive Chat Experience feature, including Focus Mode, keyboard shortcuts, JSON formatting, and dynamic task links.

---

## 1. State Management: Zustand vs React Context

### Decision
**Use Zustand** for managing Focus Mode and Display Mode state.

### Rationale
- **Better performance**: Selective subscriptions prevent unnecessary re-renders automatically
- **Less boilerplate**: No provider wrapping, cleaner code
- **Scalability**: Easy to add more UI state without refactoring
- **Minimal overhead**: Only 3KB gzipped
- **Better DX**: Simpler API, easier testing

### Implementation Pattern

```typescript
// stores/ui-store.ts
'use client'

import { create } from 'zustand'

interface UIState {
  focusMode: boolean
  displayMode: 'json' | 'human'
  toggleFocusMode: () => void
  toggleDisplayMode: () => void
  setFocusMode: (value: boolean) => void
  setDisplayMode: (mode: 'json' | 'human') => void
}

export const useUIStore = create<UIState>((set) => ({
  focusMode: false,
  displayMode: 'human',
  toggleFocusMode: () => set((state) => ({ focusMode: !state.focusMode })),
  toggleDisplayMode: () => set((state) => ({
    displayMode: state.displayMode === 'json' ? 'human' : 'json'
  })),
  setFocusMode: (value) => set({ focusMode: value }),
  setDisplayMode: (mode) => set({ displayMode: mode }),
}))
```

### Usage in Components

```typescript
// Only subscribes to focusMode - won't re-render when displayMode changes
const focusMode = useUIStore((state) => state.focusMode)
const toggleFocusMode = useUIStore((state) => state.toggleFocusMode)
```

### Alternatives Considered
- **React Context**: Requires provider wrapping, more boilerplate, all consumers re-render on any change
- **Redux**: Too heavy for simple boolean state
- **Jotai/Recoil**: Similar to Zustand but less established

---

## 2. Framer Motion AnimatePresence for Focus Mode

### Decision
Use **AnimatePresence with transform/opacity animations** and respect reduced motion preferences.

### Rationale
- Hardware-accelerated animations (transform, opacity only)
- Transitions complete in ~300ms (well under 500ms requirement)
- Existing patterns in codebase (Dialog, PageWrapper components)
- Built-in accessibility with useReducedMotion hook

### Implementation Pattern

```typescript
// hooks/useFocusMode.ts
'use client'

import { useState, useEffect } from 'react'
import { useReducedMotion } from '@/hooks/useReducedMotion'

export function useFocusMode() {
  const [isFocusMode, setIsFocusMode] = useState(false)
  const prefersReducedMotion = useReducedMotion()

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setIsFocusMode(prev => !prev)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  return { isFocusMode, setIsFocusMode, prefersReducedMotion }
}
```

### Animation Variants

```typescript
const overlayVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.3, ease: 'easeInOut' }
  },
}

const contentVariants = {
  normal: {
    scale: 1,
    y: 0,
    transition: { type: 'spring', stiffness: 100, damping: 15 }
  },
  focused: {
    scale: 1.05,
    y: 0,
    transition: { type: 'spring', stiffness: 100, damping: 15 }
  },
}
```

### Performance Notes
- ✅ Uses transform and opacity only (hardware-accelerated)
- ✅ Transition duration: 300ms (under 500ms requirement)
- ✅ Spring animations match existing patterns
- ⚠️ backdrop-blur-sm may impact low-end devices

### Accessibility
- ✅ Respects prefers-reduced-motion via useReducedMotion hook
- ✅ Keyboard shortcut (CMD+K) for toggle
- ⚠️ Need to add: Escape key handler, focus trap, ARIA attributes

---

## 3. Task Link Navigation Pattern

### Decision
Use **useRouter().push** for programmatic navigation with URL parameters for context.

### Rationale
- Better for dynamic content (task IDs parsed from chat messages)
- Allows passing context via URL params (e.g., `?source=chat`)
- Can manually prefetch common destinations
- More control over navigation behavior

### Implementation Pattern

```typescript
'use client'

import { useRouter } from 'next/navigation'

export function ChatInterface() {
  const router = useRouter()

  const handleTaskLinkClick = (taskId: string) => {
    router.push(`/tasks/${taskId}?source=chat`)
  }

  // Prefetch common destinations
  useEffect(() => {
    router.prefetch('/tasks')
  }, [router])

  return (
    <button onClick={() => handleTaskLinkClick('123')}>
      View Task #123
    </button>
  )
}
```

### State Passing
- **URL Search Parameters**: `?source=chat&messageId=xyz`
- **Dynamic Route Parameters**: `/tasks/[id]`
- On destination page, read params to show "Back to Chat" if source=chat

### Alternatives Considered
- **Link Component**: Better for static links, automatic prefetching, but less flexible for dynamic content
- **New Tab**: Breaks user flow, not recommended for seamless UX

---

## 4. Reduced Motion Accessibility

### Decision
Use **MotionConfig with reducedMotion="user"** at app root + useReducedMotion hook for fine-grained control.

### Rationale
- Automatic handling of reduced motion preferences
- Real-time response to system preference changes
- Preserves safe animations (opacity, color)
- Disables motion-heavy animations (transform, scale)

### Implementation Pattern

```typescript
// app/layout.tsx
import { MotionConfig } from 'framer-motion'

export default function RootLayout({ children }) {
  return (
    <MotionConfig reducedMotion="user">
      {children}
    </MotionConfig>
  )
}
```

### Conditional Animations

```typescript
const shouldReduceMotion = useReducedMotion()

const variants = shouldReduceMotion
  ? {
      hidden: { opacity: 0 },
      visible: { opacity: 1 },
    }
  : {
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 },
    }
```

### Fallback Behavior
- **Disabled**: Transform animations (x, y, scale, rotate)
- **Preserved**: Opacity and backgroundColor (considered safe)
- **Reduced**: Animation durations (0.5s → 0.2s)

---

## 5. Keyboard Event Handling

### Decision
Use **custom hook with global event listeners** attached in useEffect.

### Rationale
- Centralized keyboard logic
- Easy to add/remove shortcuts
- Works from anywhere on the page
- Proper cleanup on unmount

### Implementation Pattern

```typescript
// hooks/useKeyboardShortcuts.ts
'use client'

import { useEffect } from 'react'

export function useKeyboardShortcuts(handlers: {
  onFocusMode?: () => void
  onSendMessage?: () => void
}) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if event was already handled
      if (e.defaultPrevented) return

      // CMD+K or CTRL+K for focus mode
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        handlers.onFocusMode?.()
      }

      // Enter for send message (only if chat input is focused)
      if (e.key === 'Enter' && !e.shiftKey) {
        const target = e.target as HTMLElement
        if (target.tagName === 'TEXTAREA' || target.tagName === 'INPUT') {
          handlers.onSendMessage?.()
        }
      }

      // Escape to exit focus mode
      if (e.key === 'Escape') {
        handlers.onFocusMode?.()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlers])
}
```

### Conflict Handling
- Check `event.defaultPrevented` before handling
- Use `preventDefault()` to stop browser default behavior
- Document known conflicts (CMD+K opens browser search in some browsers)

### Alternatives Considered
- **Layout.tsx listeners**: Less modular, harder to test
- **Context-based**: More complex, unnecessary for simple shortcuts

---

## 6. Shadcn UI KBD Component

### Decision
**Create custom KBD component** using Tailwind CSS utilities.

### Rationale
- Shadcn UI doesn't have built-in KBD component
- Simple to implement with Tailwind
- Matches existing Shadcn UI design patterns
- Full control over styling

### Implementation Pattern

```typescript
// components/ui/kbd.tsx
import { cn } from '@/lib/utils'

interface KbdProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode
}

export function Kbd({ children, className, ...props }: KbdProps) {
  return (
    <kbd
      className={cn(
        'pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100',
        'shadow-sm',
        className
      )}
      {...props}
    >
      {children}
    </kbd>
  )
}
```

### Usage

```typescript
<div className="flex items-center gap-2">
  <span>Press</span>
  <Kbd>⌘</Kbd>
  <Kbd>K</Kbd>
  <span>to focus</span>
</div>
```

### Styling Notes
- Uses Tailwind ring and shadow utilities
- Matches Shadcn UI design tokens (border, muted, etc.)
- Responsive sizing with font-mono

---

## 7. JSON Rendering and Formatting

### Decision
Use **react-json-view** for collapsible JSON with syntax highlighting.

### Rationale
- Built-in collapsibility (expand/collapse)
- Syntax highlighting included
- Handles large JSON (10KB+) efficiently
- Copy-to-clipboard functionality
- Theme support

### Implementation Pattern

```typescript
// components/chat/JsonMessageView.tsx
'use client'

import dynamic from 'next/dynamic'

// Dynamic import to reduce bundle size
const ReactJson = dynamic(() => import('react-json-view'), { ssr: false })

interface JsonMessageViewProps {
  data: any
  collapsed?: boolean
}

export function JsonMessageView({ data, collapsed = 1 }: JsonMessageViewProps) {
  return (
    <div className="rounded-lg border border-border bg-muted p-4">
      <ReactJson
        src={data}
        theme="monokai"
        collapsed={collapsed}
        displayDataTypes={false}
        displayObjectSize={true}
        enableClipboard={true}
        style={{
          backgroundColor: 'transparent',
          fontSize: '12px',
        }}
      />
    </div>
  )
}
```

### Performance Notes
- ✅ Handles 10KB JSON without lag
- ✅ Dynamic import reduces initial bundle size
- ✅ Collapsible sections prevent DOM bloat
- ⚠️ Very large JSON (>100KB) may need virtualization

### Alternatives Considered
- **react-syntax-highlighter**: No built-in collapsibility, requires custom accordion
- **Custom solution**: Too much work for limited benefit
- **prism-react-renderer**: Good for code blocks, not ideal for interactive JSON

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| State Management | Zustand | Better performance, less boilerplate |
| Focus Mode Animation | AnimatePresence + transform/opacity | Hardware-accelerated, <500ms |
| Task Navigation | useRouter().push | Dynamic content, URL params |
| Reduced Motion | MotionConfig + useReducedMotion | Automatic + fine-grained control |
| Keyboard Events | Custom hook with global listeners | Centralized, easy cleanup |
| KBD Component | Custom with Tailwind | No built-in, simple to implement |
| JSON Rendering | react-json-view | Collapsible, performant, feature-rich |

---

## Next Steps

1. ✅ Phase 0 Research - Complete
2. ⏭️ Phase 1: Design & Contracts
   - Create data-model.md
   - Define component contracts
   - Generate quickstart.md
   - Update agent context
3. ⏭️ Phase 2: Tasks (via /sp.tasks command)

---

## Dependencies to Install

```bash
# State management
npm install zustand

# JSON rendering
npm install react-json-view

# Already installed (verify):
# - framer-motion
# - next (16.1.2)
# - react
# - tailwindcss
```

---

## Open Questions Resolved

1. ✅ **Link Navigation**: Client-side with useRouter (not new tab)
2. ✅ **Display Mode Persistence**: localStorage (not database)
3. ✅ **Focus Mode Mobile**: Full-screen overlay with responsive adjustments
4. ✅ **Keyboard Conflicts**: Check defaultPrevented, document conflicts
5. ✅ **JSON Collapsibility**: react-json-view library
