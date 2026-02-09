# Quickstart Guide: Interactive Chat Experience

**Feature**: 008-todo-interactive-chat
**Date**: 2026-02-08
**Estimated Implementation Time**: 3-5 days

## Overview

This guide provides step-by-step instructions for implementing the Interactive Chat Experience feature, including Focus Mode, keyboard shortcuts, JSON formatting, and dynamic task links.

---

## Prerequisites

### Required Knowledge
- Next.js 16 App Router
- React 18+ (hooks, context)
- TypeScript
- Framer Motion
- Tailwind CSS
- Shadcn UI components

### Required Tools
- Node.js 18+
- npm or yarn
- Git

### Existing Codebase Requirements
- Working chat interface
- Task management system with detail pages
- Authentication system (Better Auth)

---

## Installation

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install new dependencies
npm install zustand react-json-view

# Verify existing dependencies
npm list framer-motion next react tailwindcss
```

**Expected versions**:
- `zustand`: ^4.5.0
- `react-json-view`: ^1.21.3
- `framer-motion`: ^11.0.0+ (should already be installed)
- `next`: 16.1.2 (pinned)

---

## Implementation Steps

### Phase 1: State Management Setup (Day 1)

#### Step 1.1: Create UI Store

Create `frontend/src/stores/ui-store.ts`:

```typescript
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
```

**Test**:
```bash
npm run dev
# Open browser console and test:
# import { useUIStore } from '@/stores/ui-store'
# useUIStore.getState().toggleFocusMode()
```

---

### Phase 2: Keyboard Shortcuts (Day 1)

#### Step 2.1: Create Keyboard Shortcuts Hook

Create `frontend/src/hooks/useKeyboardShortcuts.ts`:

```typescript
'use client'

import { useEffect } from 'react'

interface KeyboardShortcutHandlers {
  onFocusMode?: () => void
  onSendMessage?: () => void
  onEscape?: () => void
}

export function useKeyboardShortcuts(handlers: KeyboardShortcutHandlers) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check if event was already handled
      if (e.defaultPrevented) return

      // Ignore if user is typing in an input (except for Enter in chat input)
      const target = e.target as HTMLElement
      const isInput = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA'

      // CMD+K or CTRL+K for focus mode
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        handlers.onFocusMode?.()
        return
      }

      // Escape to exit focus mode
      if (e.key === 'Escape') {
        handlers.onEscape?.()
        return
      }

      // Enter to send message (only in chat input)
      if (e.key === 'Enter' && !e.shiftKey && isInput) {
        const isChatInput = target.getAttribute('data-chat-input') === 'true'
        if (isChatInput) {
          e.preventDefault()
          handlers.onSendMessage?.()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handlers])
}
```

**Test**:
- Press CMD+K (Mac) or CTRL+K (Windows) - should trigger focus mode
- Press Escape - should exit focus mode
- Press Enter in chat input - should send message

---

### Phase 3: KBD Component (Day 1)

#### Step 3.1: Create KBD Component

Create `frontend/src/components/ui/kbd.tsx`:

```typescript
import { cn } from '@/lib/utils'

interface KbdProps extends React.HTMLAttributes<HTMLElement> {
  children: React.ReactNode
}

export function Kbd({ children, className, ...props }: KbdProps) {
  return (
    <kbd
      className={cn(
        'pointer-events-none inline-flex h-5 select-none items-center gap-1',
        'rounded border border-border bg-muted px-1.5',
        'font-mono text-[10px] font-medium text-muted-foreground',
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

**Test**:
```tsx
<div className="flex items-center gap-2">
  <span>Press</span>
  <Kbd>⌘</Kbd>
  <Kbd>K</Kbd>
  <span>to focus</span>
</div>
```

---

### Phase 4: Focus Mode Components (Day 2)

#### Step 4.1: Create Focus Mode Toggle

Create `frontend/src/components/chat/FocusModeToggle.tsx`:

```typescript
'use client'

import { Maximize2, Minimize2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Kbd } from '@/components/ui/kbd'
import { useUIStore } from '@/stores/ui-store'

export function FocusModeToggle() {
  const focusMode = useUIStore((state) => state.focusMode)
  const toggleFocusMode = useUIStore((state) => state.toggleFocusMode)

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleFocusMode}
      className="gap-2"
      aria-label="Toggle Focus Mode"
      aria-pressed={focusMode}
    >
      {focusMode ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
      <span className="hidden sm:inline">Focus</span>
      <div className="hidden md:flex items-center gap-1">
        <Kbd>⌘</Kbd>
        <Kbd>K</Kbd>
      </div>
    </Button>
  )
}
```

#### Step 4.2: Create Focus Mode Wrapper

Create `frontend/src/components/chat/FocusModeWrapper.tsx`:

```typescript
'use client'

import { motion, AnimatePresence } from 'framer-motion'
import { useUIStore } from '@/stores/ui-store'
import { useReducedMotion } from '@/hooks/useReducedMotion'
import { ReactNode } from 'react'

interface FocusModeWrapperProps {
  children: ReactNode
  navbar?: ReactNode
  footer?: ReactNode
}

export function FocusModeWrapper({ children, navbar, footer }: FocusModeWrapperProps) {
  const focusMode = useUIStore((state) => state.focusMode)
  const prefersReducedMotion = useReducedMotion()

  const overlayVariants = prefersReducedMotion
    ? { hidden: { opacity: 0 }, visible: { opacity: 1 } }
    : {
        hidden: { opacity: 0 },
        visible: { opacity: 1, transition: { duration: 0.3 } },
      }

  const fadeVariants = prefersReducedMotion
    ? { visible: { opacity: 1 }, hidden: { opacity: 1 } }
    : {
        visible: { opacity: 1, transition: { duration: 0.2 } },
        hidden: { opacity: 0, transition: { duration: 0.2 } },
      }

  return (
    <>
      {/* Navbar - fade out in focus mode */}
      <AnimatePresence>
        {!focusMode && navbar && (
          <motion.div
            initial="visible"
            animate="visible"
            exit="hidden"
            variants={fadeVariants}
          >
            {navbar}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className={focusMode ? 'fixed inset-0 z-50 flex items-center justify-center p-4' : ''}>
        {/* Dark overlay in focus mode */}
        <AnimatePresence>
          {focusMode && (
            <motion.div
              initial="hidden"
              animate="visible"
              exit="hidden"
              variants={overlayVariants}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm -z-10"
            />
          )}
        </AnimatePresence>

        {/* Chat interface */}
        <div className={focusMode ? 'w-full max-w-4xl h-[90vh] bg-background rounded-lg shadow-2xl' : 'w-full'}>
          {children}
        </div>
      </div>

      {/* Footer - fade out in focus mode */}
      <AnimatePresence>
        {!focusMode && footer && (
          <motion.div
            initial="visible"
            animate="visible"
            exit="hidden"
            variants={fadeVariants}
          >
            {footer}
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
```

**Test**:
- Click Focus Mode toggle - chat should center and background should fade
- Press CMD+K - same behavior
- Press Escape - should exit focus mode
- Verify animations are smooth (<500ms)

---

### Phase 5: Display Mode Toggle (Day 2)

#### Step 5.1: Create Display Mode Toggle

Create `frontend/src/components/chat/DisplayModeToggle.tsx`:

```typescript
'use client'

import { Code2, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useUIStore } from '@/stores/ui-store'

export function DisplayModeToggle() {
  const displayMode = useUIStore((state) => state.displayMode)
  const toggleDisplayMode = useUIStore((state) => state.toggleDisplayMode)

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={toggleDisplayMode}
      className="gap-2"
      aria-label="Toggle Display Mode"
      aria-pressed={displayMode === 'json'}
    >
      {displayMode === 'json' ? (
        <>
          <Code2 className="h-4 w-4" />
          <span className="hidden sm:inline">JSON</span>
        </>
      ) : (
        <>
          <MessageSquare className="h-4 w-4" />
          <span className="hidden sm:inline">Human</span>
        </>
      )}
    </Button>
  )
}
```

**Test**:
- Click toggle - should switch between JSON and Human modes
- Verify preference persists after page refresh (localStorage)

---

### Phase 6: JSON Message View (Day 3)

#### Step 6.1: Create JSON Message View

Create `frontend/src/components/chat/JsonMessageView.tsx`:

```typescript
'use client'

import dynamic from 'next/dynamic'
import { memo } from 'react'

const ReactJson = dynamic(() => import('react-json-view'), { ssr: false })

interface JsonMessageViewProps {
  data: any
  collapsed?: number | boolean
}

export const JsonMessageView = memo(function JsonMessageView({
  data,
  collapsed = 1,
}: JsonMessageViewProps) {
  return (
    <div className="rounded-lg border border-border bg-muted p-4 overflow-auto max-h-96">
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
})
```

**Test**:
- Toggle to JSON mode
- Verify JSON is syntax-highlighted
- Test expand/collapse functionality
- Test copy-to-clipboard

---

### Phase 7: Task Link Components (Day 3-4)

#### Step 7.1: Create Task Link Utility

Create `frontend/src/lib/utils/taskLinkGenerator.ts`:

```typescript
export interface TaskReference {
  taskId: string
  taskTitle: string
  position: { start: number; end: number }
  url: string
}

export function parseTaskReferences(content: string): TaskReference[] {
  const taskPattern = /#task-(\d+)|Task #(\d+)/gi
  const matches = [...content.matchAll(taskPattern)]

  return matches.map(match => ({
    taskId: match[1] || match[2],
    taskTitle: `Task ${match[1] || match[2]}`,
    position: {
      start: match.index!,
      end: match.index! + match[0].length,
    },
    url: `/tasks/${match[1] || match[2]}?source=chat`,
  }))
}

export function generateTaskLink(taskId: string, source = 'chat'): string {
  return `/tasks/${taskId}?source=${source}`
}

export async function validateTaskAccess(taskId: string): Promise<boolean> {
  try {
    const response = await fetch(`/api/tasks/${taskId}`, { method: 'HEAD' })
    return response.ok
  } catch {
    return false
  }
}
```

#### Step 7.2: Create Task Link Button

Create `frontend/src/components/chat/TaskLinkButton.tsx`:

```typescript
'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ExternalLink } from 'lucide-react'

interface TaskLinkButtonProps {
  taskId: string
  taskTitle: string
  source?: string
}

export function TaskLinkButton({ taskId, taskTitle, source = 'chat' }: TaskLinkButtonProps) {
  const router = useRouter()

  const handleClick = () => {
    router.push(`/tasks/${taskId}?source=${source}`)
  }

  return (
    <Button
      variant="link"
      size="sm"
      onClick={handleClick}
      className="gap-1 text-[#0FFF50] hover:text-[#0FFF50]/80"
      aria-label={`View task: ${taskTitle}`}
    >
      {taskTitle}
      <ExternalLink className="h-3 w-3" />
    </Button>
  )
}
```

**Test**:
- Click task link - should navigate to task detail page
- Verify URL includes `?source=chat` parameter
- Test with non-existent task ID

---

### Phase 8: Integration (Day 4-5)

#### Step 8.1: Update Chat Page

Update `frontend/src/app/chat/page.tsx`:

```typescript
'use client'

import { FocusModeWrapper } from '@/components/chat/FocusModeWrapper'
import { FocusModeToggle } from '@/components/chat/FocusModeToggle'
import { DisplayModeToggle } from '@/components/chat/DisplayModeToggle'
import { useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useUIStore } from '@/stores/ui-store'
import { Navbar } from '@/components/layout/Navbar'
import { Footer } from '@/components/layout/Footer'

export default function ChatPage() {
  const toggleFocusMode = useUIStore((state) => state.toggleFocusMode)

  useKeyboardShortcuts({
    onFocusMode: toggleFocusMode,
    onEscape: () => useUIStore.getState().setFocusMode(false),
  })

  return (
    <FocusModeWrapper
      navbar={<Navbar />}
      footer={<Footer />}
    >
      <div className="flex flex-col h-full">
        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h1 className="text-xl font-semibold">AI Assistant</h1>
          <div className="flex items-center gap-2">
            <DisplayModeToggle />
            <FocusModeToggle />
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-auto p-4">
          {/* Your existing chat messages */}
        </div>

        {/* Chat Input */}
        <div className="p-4 border-t">
          {/* Your existing chat input */}
        </div>
      </div>
    </FocusModeWrapper>
  )
}
```

#### Step 8.2: Add MotionConfig to Root Layout

Update `frontend/src/app/layout.tsx`:

```typescript
import { MotionConfig } from 'framer-motion'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <MotionConfig reducedMotion="user">
          {children}
        </MotionConfig>
      </body>
    </html>
  )
}
```

---

## Testing Checklist

### Manual Testing

- [ ] **Focus Mode**
  - [ ] Click toggle button - chat centers, background fades
  - [ ] Press CMD+K (Mac) or CTRL+K (Windows) - same behavior
  - [ ] Press Escape - exits focus mode
  - [ ] Transitions complete in <500ms
  - [ ] Works on mobile (responsive)

- [ ] **Display Mode**
  - [ ] Click toggle - switches between JSON and Human
  - [ ] Preference persists after page refresh
  - [ ] All messages update when mode changes
  - [ ] JSON is syntax-highlighted and collapsible

- [ ] **Keyboard Shortcuts**
  - [ ] CMD+K / CTRL+K triggers focus mode
  - [ ] Enter sends message (in chat input only)
  - [ ] Escape exits focus mode
  - [ ] Visual indicators (KBD) are visible

- [ ] **Task Links**
  - [ ] Task references are parsed correctly
  - [ ] Clicking link navigates to task detail
  - [ ] URL includes `?source=chat` parameter
  - [ ] Handles non-existent tasks gracefully

- [ ] **Accessibility**
  - [ ] All features work with keyboard only
  - [ ] Screen reader announces state changes
  - [ ] Reduced motion is respected
  - [ ] Color contrast meets WCAG AA

### Automated Testing

```bash
# Run unit tests
npm test

# Run E2E tests
npm run test:e2e

# Run accessibility tests
npm run test:a11y
```

---

## Troubleshooting

### Issue: Focus Mode doesn't work

**Solution**:
- Check if Zustand store is properly initialized
- Verify Framer Motion is installed
- Check browser console for errors

### Issue: Keyboard shortcuts conflict with browser

**Solution**:
- Document known conflicts (CMD+K opens browser search)
- Consider alternative shortcuts
- Add option to disable shortcuts

### Issue: JSON rendering is slow

**Solution**:
- Verify dynamic import is working
- Check JSON size (should be <10KB)
- Increase collapse depth

### Issue: Task links don't navigate

**Solution**:
- Verify useRouter is from 'next/navigation' (not 'next/router')
- Check task detail route exists
- Verify authentication is working

---

## Performance Optimization

### Bundle Size
- Use dynamic imports for heavy components (react-json-view)
- Tree-shake unused Framer Motion features
- Lazy load task validation

### Runtime Performance
- Memoize message components
- Virtualize long message lists
- Debounce keyboard event handlers

### Monitoring
```typescript
// Add performance monitoring
useEffect(() => {
  const start = performance.now()
  // ... operation
  const end = performance.now()
  console.log(`Operation took ${end - start}ms`)
}, [])
```

---

## Next Steps

After completing implementation:

1. **Run `/sp.tasks`** to generate detailed task breakdown
2. **Create tests** for all components
3. **Document keyboard shortcuts** in user guide
4. **Add analytics** for feature usage
5. **Consider ADRs** for architectural decisions

---

## Support

- **Documentation**: See `specs/008-todo-interactive-chat/`
- **Issues**: Create GitHub issue with `[chat-experience]` tag
- **Questions**: Ask in team chat or create discussion

---

## Estimated Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | 1 day | State management, keyboard shortcuts, KBD component |
| Phase 2 | 1 day | Focus mode components and animations |
| Phase 3 | 1 day | Display mode toggle and JSON view |
| Phase 4 | 1-2 days | Task link parsing and navigation |
| Phase 5 | 1 day | Integration and testing |
| **Total** | **5 days** | Full feature implementation |

---

## Success Criteria

✅ Focus Mode centers chat and fades background in <500ms
✅ Keyboard shortcuts (CMD+K, Enter, Escape) work reliably
✅ Display mode toggle updates all messages in <200ms
✅ Task links navigate correctly 100% of the time
✅ All features respect reduced motion preferences
✅ Accessibility requirements met (WCAG AA)
