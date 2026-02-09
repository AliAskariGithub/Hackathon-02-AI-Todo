# Data Model: Interactive Chat Experience

**Feature**: 008-todo-interactive-chat
**Date**: 2026-02-08
**Type**: Frontend UI State (No Database Changes)

## Overview

This feature introduces UI state management and component data structures for the Interactive Chat Experience. No backend or database changes are required.

---

## 1. UI State Entities

### 1.1 Focus Mode State

**Purpose**: Manages the full-screen focus mode toggle state.

**Structure**:
```typescript
interface FocusModeState {
  isFocusMode: boolean
  prefersReducedMotion: boolean
}
```

**Fields**:
- `isFocusMode`: Boolean indicating if focus mode is active
- `prefersReducedMotion`: Boolean from OS-level preference

**Storage**: Zustand store (in-memory, resets on page refresh)

**Lifecycle**:
- Created: On app initialization
- Updated: Via keyboard shortcut (CMD+K) or toggle button click
- Destroyed: On page unload

---

### 1.2 Display Mode State

**Purpose**: Manages JSON vs Human-readable response display preference.

**Structure**:
```typescript
type DisplayMode = 'json' | 'human'

interface DisplayModeState {
  displayMode: DisplayMode
}
```

**Fields**:
- `displayMode`: Enum with values 'json' or 'human'

**Storage**:
- Primary: Zustand store (in-memory)
- Persistence: localStorage (key: 'chat-display-mode')

**Lifecycle**:
- Created: On app initialization, reads from localStorage
- Updated: Via toggle button in chat header
- Persisted: On every change to localStorage
- Destroyed: Never (persists across sessions)

---

### 1.3 Chat Message

**Purpose**: Represents a single message in the chat conversation.

**Structure**:
```typescript
interface ChatMessage {
  id: string
  sender: 'user' | 'bot'
  content: string | object
  timestamp: Date
  taskReferences?: TaskReference[]
  metadata?: {
    model?: string
    tokens?: number
    processingTime?: number
  }
}
```

**Fields**:
- `id`: Unique identifier for the message
- `sender`: Who sent the message (user or bot)
- `content`: Message content (string for human, object for JSON)
- `timestamp`: When the message was sent
- `taskReferences`: Optional array of task references found in the message
- `metadata`: Optional metadata about the response (for JSON mode)

**Storage**: React state or existing chat state management

**Lifecycle**:
- Created: When user sends message or bot responds
- Updated: Never (immutable)
- Destroyed: On chat session end or page refresh

---

### 1.4 Task Reference

**Purpose**: Represents a clickable task link within a chat message.

**Structure**:
```typescript
interface TaskReference {
  taskId: string
  taskTitle: string
  position: {
    start: number
    end: number
  }
  url: string
}
```

**Fields**:
- `taskId`: ID of the referenced task
- `taskTitle`: Display name of the task
- `position`: Character position in message content (for highlighting)
- `url`: Navigation URL (e.g., `/tasks/123?source=chat`)

**Storage**: Embedded within ChatMessage

**Lifecycle**:
- Created: When parsing bot response for task references
- Updated: Never (immutable)
- Destroyed: With parent ChatMessage

---

### 1.5 Keyboard Shortcut

**Purpose**: Configuration for keyboard shortcuts.

**Structure**:
```typescript
interface KeyboardShortcut {
  key: string
  modifiers: ('ctrl' | 'meta' | 'shift' | 'alt')[]
  action: string
  description: string
  enabled: boolean
}
```

**Fields**:
- `key`: The key to press (e.g., 'k', 'Enter')
- `modifiers`: Required modifier keys (CMD/CTRL, Shift, Alt)
- `action`: Action identifier (e.g., 'focus-mode', 'send-message')
- `description`: Human-readable description for UI hints
- `enabled`: Whether the shortcut is currently active

**Storage**: Static configuration (constants file)

**Predefined Shortcuts**:
```typescript
const KEYBOARD_SHORTCUTS: KeyboardShortcut[] = [
  {
    key: 'k',
    modifiers: ['meta', 'ctrl'], // CMD on Mac, CTRL on Windows
    action: 'toggle-focus-mode',
    description: 'Toggle Focus Mode',
    enabled: true,
  },
  {
    key: 'Enter',
    modifiers: [],
    action: 'send-message',
    description: 'Send Message',
    enabled: true,
  },
  {
    key: 'Escape',
    modifiers: [],
    action: 'exit-focus-mode',
    description: 'Exit Focus Mode',
    enabled: true,
  },
]
```

---

## 2. Component State

### 2.1 Chat Interface State

**Purpose**: Local state for the chat interface component.

**Structure**:
```typescript
interface ChatInterfaceState {
  messages: ChatMessage[]
  inputValue: string
  isLoading: boolean
  error: string | null
}
```

**Fields**:
- `messages`: Array of chat messages
- `inputValue`: Current value of the input field
- `isLoading`: Whether a response is being generated
- `error`: Error message if something went wrong

**Storage**: React useState

---

### 2.2 JSON View State

**Purpose**: Local state for JSON message viewer.

**Structure**:
```typescript
interface JsonViewState {
  collapsed: number | boolean
  theme: 'monokai' | 'rjv-default'
  showDataTypes: boolean
  showObjectSize: boolean
}
```

**Fields**:
- `collapsed`: Depth level to collapse (1 = collapse all, false = expand all)
- `theme`: Color theme for syntax highlighting
- `showDataTypes`: Whether to show data types
- `showObjectSize`: Whether to show object/array sizes

**Storage**: React useState with localStorage persistence

---

## 3. Data Transformations

### 3.1 Message Parsing

**Input**: Raw bot response (string)
**Output**: ChatMessage with TaskReferences

**Process**:
1. Parse response text for task patterns (e.g., `#task-123`, `Task #123`)
2. Extract task IDs and positions
3. Fetch task titles from existing task data
4. Generate TaskReference objects
5. Embed in ChatMessage

**Example**:
```typescript
function parseTaskReferences(content: string): TaskReference[] {
  const taskPattern = /#task-(\d+)|Task #(\d+)/gi
  const matches = [...content.matchAll(taskPattern)]

  return matches.map(match => ({
    taskId: match[1] || match[2],
    taskTitle: `Task ${match[1] || match[2]}`, // Fetch from API
    position: {
      start: match.index!,
      end: match.index! + match[0].length,
    },
    url: `/tasks/${match[1] || match[2]}?source=chat`,
  }))
}
```

---

### 3.2 Display Mode Transformation

**Input**: ChatMessage
**Output**: Rendered content (string or JSX)

**Process**:
- **Human Mode**: Render as plain text with task links as buttons
- **JSON Mode**: Render as formatted JSON with syntax highlighting

**Example**:
```typescript
function renderMessage(message: ChatMessage, displayMode: DisplayMode) {
  if (displayMode === 'json') {
    return <JsonMessageView data={message} />
  }

  return <HumanMessageView message={message} />
}
```

---

## 4. Validation Rules

### 4.1 Task Reference Validation

**Rules**:
- Task ID must be a valid integer
- Task must exist in the system
- User must have permission to view the task

**Validation**:
```typescript
async function validateTaskReference(taskId: string): Promise<boolean> {
  try {
    const response = await fetch(`/api/tasks/${taskId}`)
    return response.ok
  } catch {
    return false
  }
}
```

---

### 4.2 Keyboard Shortcut Validation

**Rules**:
- Key must not conflict with browser shortcuts
- Modifier combinations must be valid
- Action must be registered

**Validation**:
```typescript
function isValidShortcut(shortcut: KeyboardShortcut): boolean {
  // Check for browser conflicts
  const browserShortcuts = ['ctrl+t', 'ctrl+w', 'ctrl+n']
  const shortcutString = `${shortcut.modifiers.join('+')}+${shortcut.key}`

  return !browserShortcuts.includes(shortcutString.toLowerCase())
}
```

---

## 5. State Transitions

### 5.1 Focus Mode State Machine

```
[Normal Mode] --CMD+K--> [Focus Mode]
[Focus Mode] --CMD+K--> [Normal Mode]
[Focus Mode] --ESC--> [Normal Mode]
[Focus Mode] --Click Toggle--> [Normal Mode]
[Normal Mode] --Click Toggle--> [Focus Mode]
```

**Constraints**:
- Cannot enter focus mode if chat is not loaded
- Cannot exit focus mode while message is being sent
- Mobile devices may have modified behavior

---

### 5.2 Display Mode State Machine

```
[Human Mode] --Click Toggle--> [JSON Mode]
[JSON Mode] --Click Toggle--> [Human Mode]
```

**Constraints**:
- Mode persists across page refreshes (localStorage)
- All messages update when mode changes
- Mode is per-user, not per-session

---

## 6. Performance Considerations

### 6.1 Message Rendering

**Optimization**:
- Use React.memo for message components
- Virtualize message list for long conversations (>100 messages)
- Lazy load JSON viewer component

**Metrics**:
- Target: <200ms to toggle display mode
- Target: <500ms to render 50 messages

---

### 6.2 Task Reference Parsing

**Optimization**:
- Parse task references on message receive (not on render)
- Cache task titles to avoid repeated API calls
- Debounce task validation requests

**Metrics**:
- Target: <50ms to parse task references per message
- Target: <100ms to validate task existence

---

## 7. Data Flow Diagram

```
User Input
    ↓
[Chat Interface]
    ↓
Parse Task References
    ↓
[ChatMessage with TaskReferences]
    ↓
Display Mode Check
    ↓
[Human Mode] → Render with Task Buttons
    ↓
[JSON Mode] → Render with Syntax Highlighting
    ↓
User Clicks Task Link
    ↓
Navigate to Task Detail
```

---

## 8. Storage Summary

| Entity | Storage Type | Persistence | Size Estimate |
|--------|-------------|-------------|---------------|
| Focus Mode State | Zustand (memory) | Session only | <1KB |
| Display Mode | Zustand + localStorage | Permanent | <1KB |
| Chat Messages | React state | Session only | ~1KB per message |
| Task References | Embedded in messages | Session only | ~100B per reference |
| Keyboard Shortcuts | Static config | N/A | <1KB |

---

## 9. Migration Notes

**No database migrations required** - This is a frontend-only feature.

**Existing data compatibility**:
- Works with existing chat message format
- No changes to task data structure
- No changes to user preferences schema

---

## 10. Testing Data

### Sample Chat Message (Human Mode)
```typescript
{
  id: 'msg-001',
  sender: 'bot',
  content: 'I created Task #123 for you. You can also check Task #456.',
  timestamp: new Date('2026-02-08T10:30:00Z'),
  taskReferences: [
    {
      taskId: '123',
      taskTitle: 'Buy groceries',
      position: { start: 10, end: 19 },
      url: '/tasks/123?source=chat',
    },
    {
      taskId: '456',
      taskTitle: 'Call dentist',
      position: { start: 45, end: 54 },
      url: '/tasks/456?source=chat',
    },
  ],
}
```

### Sample Chat Message (JSON Mode)
```typescript
{
  id: 'msg-002',
  sender: 'bot',
  content: {
    action: 'task_created',
    task: {
      id: 123,
      title: 'Buy groceries',
      status: 'pending',
      created_at: '2026-02-08T10:30:00Z',
    },
    message: 'Task created successfully',
  },
  timestamp: new Date('2026-02-08T10:30:00Z'),
  metadata: {
    model: 'gpt-4',
    tokens: 150,
    processingTime: 1200,
  },
}
```
