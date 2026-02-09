# Component Contracts: Interactive Chat Experience

**Feature**: 008-todo-interactive-chat
**Date**: 2026-02-08
**Type**: Frontend Component Interfaces

## Overview

This document defines the contracts (props, events, and behaviors) for all components in the Interactive Chat Experience feature.

---

## 1. FocusModeToggle Component

**Purpose**: Button to toggle Focus Mode on/off.

**Contract**:
```typescript
interface FocusModeToggleProps {
  /** Optional custom class name */
  className?: string
  /** Optional custom icon */
  icon?: React.ReactNode
  /** Optional label text (default: "Focus Mode") */
  label?: string
  /** Optional callback when focus mode changes */
  onToggle?: (isFocusMode: boolean) => void
}

export function FocusModeToggle(props: FocusModeToggleProps): JSX.Element
```

**Behavior**:
- Reads `focusMode` state from Zustand store
- Calls `toggleFocusMode()` on click
- Shows active state when focus mode is on
- Displays keyboard shortcut hint (⌘K or Ctrl+K)
- Emits `onToggle` callback if provided

**Accessibility**:
- `role="button"`
- `aria-label="Toggle Focus Mode"`
- `aria-pressed={isFocusMode}`
- Keyboard accessible (Enter/Space)

**Styling**:
- Uses Neon Green (#0FFF50) accent when active
- Shadcn Button component as base
- Responsive sizing

---

## 2. DisplayModeToggle Component

**Purpose**: Button to toggle between JSON and Human display modes.

**Contract**:
```typescript
interface DisplayModeToggleProps {
  /** Optional custom class name */
  className?: string
  /** Optional callback when display mode changes */
  onToggle?: (mode: 'json' | 'human') => void
}

export function DisplayModeToggle(props: DisplayModeToggleProps): JSX.Element
```

**Behavior**:
- Reads `displayMode` state from Zustand store
- Calls `toggleDisplayMode()` on click
- Shows current mode in button text
- Persists preference to localStorage
- Emits `onToggle` callback if provided

**Accessibility**:
- `role="button"`
- `aria-label="Toggle Display Mode"`
- `aria-pressed={displayMode === 'json'}`
- Keyboard accessible

**Styling**:
- Toggle-style button (two states)
- Clear visual indication of current mode
- Shadcn Button variant

---

## 3. JsonMessageView Component

**Purpose**: Renders chat message content as formatted JSON.

**Contract**:
```typescript
interface JsonMessageViewProps {
  /** The data to display as JSON */
  data: any
  /** Initial collapse depth (default: 1) */
  collapsed?: number | boolean
  /** Optional theme (default: 'monokai') */
  theme?: 'monokai' | 'rjv-default'
  /** Optional custom class name */
  className?: string
}

export function JsonMessageView(props: JsonMessageViewProps): JSX.Element
```

**Behavior**:
- Renders JSON with syntax highlighting
- Supports expand/collapse of nested objects
- Provides copy-to-clipboard functionality
- Handles large JSON (up to 10KB) efficiently
- Dynamic import to reduce bundle size

**Accessibility**:
- `role="region"`
- `aria-label="JSON Data View"`
- Keyboard navigation for expand/collapse

**Performance**:
- Lazy loaded (dynamic import)
- Memoized to prevent unnecessary re-renders
- Collapsed by default to reduce DOM size

---

## 4. TaskLinkButton Component

**Purpose**: Clickable button that navigates to a task detail page.

**Contract**:
```typescript
interface TaskLinkButtonProps {
  /** Task ID to navigate to */
  taskId: string
  /** Display text for the button */
  taskTitle: string
  /** Optional source context (default: 'chat') */
  source?: string
  /** Optional custom class name */
  className?: string
  /** Optional callback before navigation */
  onNavigate?: (taskId: string) => void
}

export function TaskLinkButton(props: TaskLinkButtonProps): JSX.Element
```

**Behavior**:
- Navigates to `/tasks/{taskId}?source={source}` on click
- Uses `useRouter().push` for client-side navigation
- Validates task existence before navigation
- Shows loading state during validation
- Handles deleted/inaccessible tasks gracefully
- Emits `onNavigate` callback if provided

**Accessibility**:
- `role="link"` (semantic link behavior)
- `aria-label="View task: {taskTitle}"`
- Keyboard accessible (Enter)

**Styling**:
- Shadcn Button with link variant
- Neon Green (#0FFF50) accent on hover
- Distinct from regular text

**Error Handling**:
- Shows error toast if task doesn't exist
- Disables button if validation fails
- Provides helpful error message

---

## 5. KeyboardShortcutHint Component

**Purpose**: Visual indicator showing available keyboard shortcuts.

**Contract**:
```typescript
interface KeyboardShortcutHintProps {
  /** The key to display (e.g., 'K', 'Enter') */
  keys: string[]
  /** Optional description text */
  description?: string
  /** Optional custom class name */
  className?: string
}

export function KeyboardShortcutHint(props: KeyboardShortcutHintProps): JSX.Element
```

**Behavior**:
- Renders keyboard keys using KBD component
- Shows platform-specific modifiers (⌘ on Mac, Ctrl on Windows)
- Displays description text if provided
- Responsive layout

**Accessibility**:
- `role="note"`
- `aria-label="Keyboard shortcut: {description}"`

**Styling**:
- Uses custom KBD component
- Monospace font for keys
- Subtle border and shadow

**Example Usage**:
```tsx
<KeyboardShortcutHint
  keys={['⌘', 'K']}
  description="Focus Mode"
/>
```

---

## 6. FocusModeWrapper Component

**Purpose**: Wrapper that applies Focus Mode layout and animations.

**Contract**:
```typescript
interface FocusModeWrapperProps {
  /** Content to display (chat interface) */
  children: React.ReactNode
  /** Optional navbar to hide in focus mode */
  navbar?: React.ReactNode
  /** Optional footer to hide in focus mode */
  footer?: React.ReactNode
  /** Optional custom class name */
  className?: string
}

export function FocusModeWrapper(props: FocusModeWrapperProps): JSX.Element
```

**Behavior**:
- Reads `focusMode` state from Zustand store
- Applies full-screen overlay when active
- Fades out navbar and footer
- Centers chat interface
- Respects reduced motion preferences
- Adds dark backdrop with blur

**Accessibility**:
- `role="dialog"` when focus mode active
- `aria-modal="true"` when focus mode active
- Traps focus within chat interface
- Escape key exits focus mode

**Performance**:
- Uses Framer Motion for animations
- Hardware-accelerated transforms
- Transitions complete in <500ms

---

## 7. ChatInterface Component (Enhanced)

**Purpose**: Main chat interface with all interactive features.

**Contract**:
```typescript
interface ChatInterfaceProps {
  /** Initial messages to display */
  initialMessages?: ChatMessage[]
  /** Optional callback when message is sent */
  onSendMessage?: (message: string) => Promise<void>
  /** Optional callback when task link is clicked */
  onTaskLinkClick?: (taskId: string) => void
  /** Optional custom class name */
  className?: string
}

export function ChatInterface(props: ChatInterfaceProps): JSX.Element
```

**Behavior**:
- Manages message list state
- Handles user input and message sending
- Parses task references from bot responses
- Renders messages based on display mode
- Integrates keyboard shortcuts
- Supports Focus Mode

**Accessibility**:
- `role="region"`
- `aria-label="Chat Interface"`
- Keyboard navigation for all features
- Screen reader announcements for new messages

**Performance**:
- Virtualizes message list for long conversations
- Memoizes message components
- Debounces input handling

---

## 8. Hooks

### 8.1 useFocusMode Hook

**Contract**:
```typescript
interface UseFocusModeReturn {
  isFocusMode: boolean
  setFocusMode: (value: boolean) => void
  toggleFocusMode: () => void
  prefersReducedMotion: boolean
}

export function useFocusMode(): UseFocusModeReturn
```

**Behavior**:
- Returns focus mode state and controls
- Sets up keyboard listener for CMD+K
- Detects reduced motion preference
- Cleans up listeners on unmount

---

### 8.2 useDisplayMode Hook

**Contract**:
```typescript
interface UseDisplayModeReturn {
  displayMode: 'json' | 'human'
  setDisplayMode: (mode: 'json' | 'human') => void
  toggleDisplayMode: () => void
}

export function useDisplayMode(): UseDisplayModeReturn
```

**Behavior**:
- Returns display mode state and controls
- Syncs with localStorage
- Updates all messages when mode changes

---

### 8.3 useKeyboardShortcuts Hook

**Contract**:
```typescript
interface KeyboardShortcutHandlers {
  onFocusMode?: () => void
  onSendMessage?: () => void
  onEscape?: () => void
}

export function useKeyboardShortcuts(
  handlers: KeyboardShortcutHandlers
): void
```

**Behavior**:
- Sets up global keyboard event listeners
- Handles CMD+K, Enter, Escape
- Checks for conflicts with browser shortcuts
- Cleans up listeners on unmount

---

### 8.4 useTaskLinkGenerator Hook

**Contract**:
```typescript
interface UseTaskLinkGeneratorReturn {
  parseTaskReferences: (content: string) => TaskReference[]
  generateTaskLink: (taskId: string, source?: string) => string
  validateTask: (taskId: string) => Promise<boolean>
}

export function useTaskLinkGenerator(): UseTaskLinkGeneratorReturn
```

**Behavior**:
- Parses task references from text
- Generates navigation URLs
- Validates task existence
- Caches validation results

---

## 9. Utility Functions

### 9.1 taskLinkGenerator

**Contract**:
```typescript
/**
 * Generates a task detail URL with source context
 */
export function generateTaskLink(
  taskId: string,
  source?: string
): string

/**
 * Parses task references from message content
 */
export function parseTaskReferences(
  content: string
): TaskReference[]

/**
 * Validates if a task exists and is accessible
 */
export async function validateTaskAccess(
  taskId: string
): Promise<boolean>
```

---

## 10. Store Contracts

### 10.1 UI Store (Zustand)

**Contract**:
```typescript
interface UIStore {
  // State
  focusMode: boolean
  displayMode: 'json' | 'human'

  // Actions
  toggleFocusMode: () => void
  toggleDisplayMode: () => void
  setFocusMode: (value: boolean) => void
  setDisplayMode: (mode: 'json' | 'human') => void
}

export const useUIStore: UseBoundStore<StoreApi<UIStore>>
```

**Behavior**:
- Persists displayMode to localStorage
- Provides selective subscriptions
- No provider wrapping required

---

## 11. Event Contracts

### 11.1 Focus Mode Events

```typescript
// Emitted when focus mode is toggled
interface FocusModeToggleEvent {
  type: 'focus-mode-toggle'
  isFocusMode: boolean
  timestamp: Date
}

// Emitted when focus mode animation completes
interface FocusModeTransitionCompleteEvent {
  type: 'focus-mode-transition-complete'
  isFocusMode: boolean
  duration: number
}
```

---

### 11.2 Display Mode Events

```typescript
// Emitted when display mode is toggled
interface DisplayModeToggleEvent {
  type: 'display-mode-toggle'
  displayMode: 'json' | 'human'
  timestamp: Date
}
```

---

### 11.3 Task Link Events

```typescript
// Emitted when task link is clicked
interface TaskLinkClickEvent {
  type: 'task-link-click'
  taskId: string
  source: string
  timestamp: Date
}

// Emitted when task validation fails
interface TaskValidationErrorEvent {
  type: 'task-validation-error'
  taskId: string
  error: string
  timestamp: Date
}
```

---

## 12. Error Handling Contracts

### 12.1 Task Link Errors

```typescript
type TaskLinkError =
  | { type: 'not-found'; taskId: string }
  | { type: 'permission-denied'; taskId: string }
  | { type: 'network-error'; message: string }

interface TaskLinkErrorHandler {
  (error: TaskLinkError): void
}
```

---

### 12.2 Keyboard Shortcut Errors

```typescript
type KeyboardShortcutError =
  | { type: 'conflict'; shortcut: string }
  | { type: 'disabled'; reason: string }

interface KeyboardShortcutErrorHandler {
  (error: KeyboardShortcutError): void
}
```

---

## 13. Testing Contracts

### 13.1 Component Test Props

```typescript
// Props for testing components in isolation
interface TestableComponentProps {
  'data-testid'?: string
  'aria-label'?: string
}

// All components should accept these props
```

---

### 13.2 Mock Data

```typescript
// Mock chat message for testing
export const mockChatMessage: ChatMessage = {
  id: 'test-msg-001',
  sender: 'bot',
  content: 'I created Task #123 for you.',
  timestamp: new Date('2026-02-08T10:00:00Z'),
  taskReferences: [
    {
      taskId: '123',
      taskTitle: 'Test Task',
      position: { start: 10, end: 19 },
      url: '/tasks/123?source=chat',
    },
  ],
}
```

---

## 14. Performance Contracts

### 14.1 Render Performance

```typescript
// Components must meet these performance targets
interface PerformanceTargets {
  focusModeTransition: 500 // ms
  displayModeToggle: 200 // ms
  keyboardShortcutResponse: 100 // ms
  messageRender: 50 // ms per message
  taskLinkParse: 50 // ms per message
}
```

---

## 15. Versioning

**Contract Version**: 1.0.0
**Breaking Changes**: None (initial version)
**Deprecations**: None

**Compatibility**:
- Next.js: 16.1.2+
- React: 18.0.0+
- TypeScript: 5.0.0+
