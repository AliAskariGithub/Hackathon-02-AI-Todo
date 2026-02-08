# Implementation Plan: Interactive Chat Experience

**Branch**: `008-todo-interactive-chat` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-todo-interactive-chat/spec.md`

## Summary

Enhance the existing AI chatbot interface with advanced interaction features including Focus Mode (distraction-free full-screen chat), keyboard shortcuts (CMD+K, Enter), dynamic task links (clickable buttons to task details), JSON/Human response toggle for debugging, and simple language responses (grade 6-8 reading level). The implementation leverages Framer Motion for smooth animations, Shadcn UI for components, and React Context/Zustand for global state management.

## Technical Context

**Language/Version**: TypeScript 5.x with Next.js 16.1.2 (App Router)
**Primary Dependencies**:
- React 18+
- Framer Motion (animations)
- Shadcn UI (components: Button, KBD)
- react-syntax-highlighter (JSON formatting)
- Zustand or React Context (Focus Mode state)
- Tailwind CSS (styling)

**Storage**: N/A (UI-only feature, leverages existing chat state)
**Testing**: Jest + React Testing Library for component tests, Playwright for E2E keyboard/focus tests
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge - latest 2 versions)
**Project Type**: Web application (frontend enhancement)
**Performance Goals**:
- Focus Mode transitions < 500ms
- Display mode toggle < 200ms
- Keyboard shortcut response < 100ms
- JSON formatting without lag for responses up to 10KB

**Constraints**:
- Must respect prefers-reduced-motion for accessibility
- Must not conflict with browser keyboard shortcuts
- Must maintain Neon Green (#0FFF50) accent color
- Must work on both desktop and mobile (responsive)

**Scale/Scope**:
- 5 new React components/hooks
- 2 global state managers (Focus Mode, Display Mode)
- 3 keyboard event listeners
- 1 utility function (task link generator)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Agentic Autonomy
**Status**: PASS
**Rationale**: All code will be generated via Spec-Kit Plus workflow following `/sp.plan` → `/sp.tasks` → `/sp.implement` pattern.

### ✅ Live Documentation
**Status**: PASS
**Rationale**: Will use Context7 MCP Server to fetch:
- Next.js 16.1.2 App Router patterns
- Framer Motion AnimatePresence best practices
- Shadcn UI component usage (Button, KBD)
- React Context/Zustand state management patterns

### ✅ Secure by Default
**Status**: PASS
**Rationale**:
- Task links will validate user permissions before navigation (FR-018)
- JSON mode will not expose sensitive system information (Security Considerations)
- No new authentication requirements (UI-only feature)

### ✅ Modernity
**Status**: PASS
**Rationale**:
- Uses Next.js 16 App Router (latest)
- Leverages Shadcn UI components
- Implements modern React patterns (hooks, context)
- Uses Framer Motion for smooth animations

### ✅ Tech Stack Compliance
**Status**: PASS
**Rationale**:
- Next.js 16.1.2 (pinned version)
- Shadcn UI components
- Tailwind CSS styling
- No deviations from approved stack

### ✅ Auth Protocol
**Status**: PASS
**Rationale**:
- Feature leverages existing Better Auth JWT implementation
- Task link navigation will use existing auth context
- No changes to authentication flow

### ✅ API Design Standards
**Status**: PASS
**Rationale**:
- No new API endpoints required
- Leverages existing chat API
- Task links use existing task detail routes

### ✅ UI/UX Standards
**Status**: PASS
**Rationale**:
- Responsive design with mobile-first approach
- Shadcn UI components ensure consistency
- Accessibility requirements (ARIA labels, keyboard nav, reduced motion)
- Maintains Neon Green (#0FFF50) accent color

### ✅ Data Integrity Requirements
**Status**: PASS
**Rationale**:
- No database changes required
- UI-only feature using existing data
- No transaction requirements

### ✅ Version Control Policy
**Status**: PASS
**Rationale**: Next.js 16.1.2 pinned, all dependencies version-locked

### ✅ Security Enforcement
**Status**: PASS
**Rationale**:
- Task links validate permissions before navigation
- JSON mode filters sensitive data
- No security bypass mechanisms

### ✅ Architecture Boundaries
**Status**: PASS
**Rationale**:
- Frontend-only feature
- No backend changes required
- Uses existing REST API communication

### ✅ Environment Management
**Status**: PASS
**Rationale**: No new secrets or environment variables required

**GATE RESULT**: ✅ ALL CHECKS PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/008-todo-interactive-chat/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx          # Main chat component (existing)
│   │   │   ├── ChatMessage.tsx            # Message display (existing)
│   │   │   ├── ChatInput.tsx              # Input field (existing)
│   │   │   ├── FocusModeToggle.tsx        # NEW: Focus mode button
│   │   │   ├── DisplayModeToggle.tsx      # NEW: JSON/Human toggle
│   │   │   ├── JsonMessageView.tsx        # NEW: JSON formatter
│   │   │   ├── TaskLinkButton.tsx         # NEW: Task link component
│   │   │   └── KeyboardShortcutHint.tsx   # NEW: KBD indicator
│   │   └── ui/                            # Shadcn UI components
│   │       ├── button.tsx                 # Existing
│   │       └── kbd.tsx                    # NEW: Keyboard indicator
│   ├── hooks/
│   │   ├── useFocusMode.ts                # NEW: Focus mode state hook
│   │   ├── useDisplayMode.ts              # NEW: Display mode state hook
│   │   └── useKeyboardShortcuts.ts        # NEW: Global keyboard listeners
│   ├── lib/
│   │   └── utils/
│   │       └── taskLinkGenerator.ts       # NEW: Task link utility
│   ├── contexts/
│   │   └── ChatContext.tsx                # NEW: Chat-specific context
│   └── app/
│       └── chat/
│           └── page.tsx                   # Chat page (existing, will enhance)
└── tests/
    ├── components/
    │   └── chat/
    │       ├── FocusModeToggle.test.tsx
    │       ├── DisplayModeToggle.test.tsx
    │       ├── JsonMessageView.test.tsx
    │       └── TaskLinkButton.test.tsx
    └── e2e/
        └── chat-interactions.spec.ts      # Keyboard shortcuts, focus mode E2E
```

**Structure Decision**: Web application structure (Option 2) with frontend enhancements. This is a frontend-only feature that extends the existing chat interface without requiring backend changes. All new components follow the established Next.js App Router pattern with components organized by feature (chat/).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

N/A - No constitutional violations. All checks pass.

## Phase 0: Research & Unknowns

### Research Tasks

1. **Framer Motion AnimatePresence for Focus Mode**
   - **Unknown**: Best practices for full-screen overlay transitions in Next.js 16
   - **Research Goal**: Find AnimatePresence patterns for centering content and fading background
   - **Context7 Query**: "Framer Motion AnimatePresence full screen overlay Next.js 16"

2. **Keyboard Event Handling in Next.js App Router**
   - **Unknown**: Optimal pattern for global keyboard listeners in App Router
   - **Research Goal**: Determine if useEffect in layout.tsx or custom hook is better
   - **Context7 Query**: "Next.js 16 App Router global keyboard event listeners"

3. **Shadcn UI KBD Component**
   - **Unknown**: Whether Shadcn UI has a built-in KBD component or needs custom implementation
   - **Research Goal**: Find KBD component implementation or create custom with Tailwind
   - **Context7 Query**: "Shadcn UI keyboard indicator KBD component"

4. **React Syntax Highlighter Performance**
   - **Unknown**: Performance characteristics for large JSON responses
   - **Research Goal**: Determine if react-syntax-highlighter meets <10KB without lag requirement
   - **Context7 Query**: "react-syntax-highlighter performance large JSON"

5. **Zustand vs React Context for Focus Mode**
   - **Unknown**: Which state management approach is better for global UI state
   - **Research Goal**: Compare performance and complexity for simple boolean state
   - **Context7 Query**: "Zustand vs React Context global UI state Next.js"

6. **Reduced Motion Detection**
   - **Unknown**: How to detect and respect prefers-reduced-motion in Framer Motion
   - **Research Goal**: Find pattern for conditional animations based on user preference
   - **Context7 Query**: "Framer Motion prefers-reduced-motion accessibility"

7. **Task Link Navigation Pattern**
   - **Unknown**: Best practice for programmatic navigation in Next.js 16 App Router
   - **Research Goal**: Determine if useRouter().push or Link component is better for dynamic links
   - **Context7 Query**: "Next.js 16 App Router programmatic navigation useRouter"

### Decisions Requiring Documentation

1. **Link Navigation Strategy**
   - **Question**: Should task links open in new tab or perform client-side route change?
   - **Options**:
     - A) Client-side navigation with useRouter (recommended in user input)
     - B) New tab with target="_blank"
   - **Recommendation**: Client-side navigation (Option A) for seamless UX

2. **Display Mode Persistence**
   - **Question**: Where to store JSON/Human preference?
   - **Options**:
     - A) localStorage (persists across sessions)
     - B) Session state only (resets on refresh)
     - C) User settings in database
   - **Recommendation**: localStorage (Option A) for convenience without backend changes

3. **Focus Mode Mobile Behavior**
   - **Question**: How should Focus Mode work on mobile devices?
   - **Options**:
     - A) Full-screen overlay (same as desktop)
     - B) Disabled on mobile (show message)
     - C) Modified behavior (hide nav only)
   - **Recommendation**: Full-screen overlay (Option A) with responsive adjustments

4. **Keyboard Shortcut Conflicts**
   - **Question**: How to handle conflicts with browser/OS shortcuts?
   - **Options**:
     - A) Check event.defaultPrevented before handling
     - B) Use different shortcuts on conflict
     - C) Allow user to disable shortcuts
   - **Recommendation**: Check defaultPrevented (Option A) and document conflicts

5. **JSON Collapsibility**
   - **Question**: How to implement collapsible JSON sections?
   - **Options**:
     - A) Use react-json-view library
     - B) Custom accordion with react-syntax-highlighter
     - C) Simple expand/collapse button
   - **Recommendation**: react-json-view (Option A) for rich features

## Phase 1: Design & Contracts

✅ **Status**: Complete

### Deliverables

1. **data-model.md** - Complete data model for UI state entities
   - Focus Mode State
   - Display Mode State
   - Chat Message structure
   - Task Reference structure
   - Keyboard Shortcut configuration
   - Component state definitions
   - Data transformations and validation rules

2. **contracts/components.md** - Component contracts and interfaces
   - FocusModeToggle component contract
   - DisplayModeToggle component contract
   - JsonMessageView component contract
   - TaskLinkButton component contract
   - KeyboardShortcutHint component contract
   - FocusModeWrapper component contract
   - Hook contracts (useFocusMode, useDisplayMode, useKeyboardShortcuts)
   - Utility function contracts
   - Store contracts (Zustand)
   - Event contracts
   - Error handling contracts
   - Performance contracts

3. **quickstart.md** - Implementation guide
   - Prerequisites and dependencies
   - Step-by-step implementation instructions
   - Code examples for all components
   - Testing checklist
   - Troubleshooting guide
   - Performance optimization tips
   - Estimated timeline (5 days)

### Key Decisions Finalized

1. **State Management**: Zustand (selected over React Context)
   - Rationale: Better performance, less boilerplate, easier scalability
   - Implementation: Single UI store with selective subscriptions

2. **Task Navigation**: useRouter().push with URL parameters
   - Rationale: Better for dynamic content, allows context passing
   - Implementation: Client-side navigation with source tracking

3. **JSON Rendering**: react-json-view library
   - Rationale: Built-in collapsibility, syntax highlighting, good performance
   - Implementation: Dynamic import to reduce bundle size

4. **Reduced Motion**: MotionConfig + useReducedMotion hook
   - Rationale: Automatic + fine-grained control
   - Implementation: Global config at root layout

5. **Keyboard Events**: Custom hook with global listeners
   - Rationale: Centralized logic, easy cleanup
   - Implementation: useKeyboardShortcuts hook

6. **KBD Component**: Custom implementation with Tailwind
   - Rationale: No built-in Shadcn component, simple to create
   - Implementation: Styled kbd element with design tokens

### Constitution Re-Check

All constitutional requirements remain satisfied after Phase 1 design:
- ✅ Agentic Autonomy: Design follows Spec-Kit Plus workflow
- ✅ Live Documentation: Context7 patterns incorporated
- ✅ Secure by Default: Permission validation included
- ✅ Modernity: Uses latest Next.js 16 patterns
- ✅ Tech Stack Compliance: No deviations
- ✅ All other checks: PASS

### Next Steps

Phase 1 is complete. Ready for Phase 2 (Task Generation):
- Run `/sp.tasks` to generate detailed task breakdown
- Tasks will be based on the design artifacts created in Phase 1
- Implementation can begin after task approval

## Architectural Decisions Requiring ADR

Based on the planning process, the following decisions meet the ADR significance criteria (impact + alternatives + scope):

1. **State Management for Focus Mode and Display Mode**
   - **Impact**: Affects component architecture and performance
   - **Alternatives**: Zustand vs React Context vs Redux
   - **Scope**: Cross-cutting concern affecting multiple components
   - **Recommendation**: Document after Phase 0 research completes

2. **Task Link Navigation Pattern**
   - **Impact**: Affects user experience and routing architecture
   - **Alternatives**: Client-side navigation vs new tab vs modal
   - **Scope**: Influences chat-to-task workflow across application
   - **Recommendation**: Document after decision is finalized

3. **JSON Rendering Library Selection**
   - **Impact**: Affects performance and feature set for debugging
   - **Alternatives**: react-syntax-highlighter vs react-json-view vs custom
   - **Scope**: Determines debugging capabilities for developers
   - **Recommendation**: Document after performance testing

**ADR Suggestion**: After completing Phase 0 research and Phase 1 design, run:
```
/sp.adr "State Management for Chat UI Features"
/sp.adr "Task Link Navigation Strategy"
/sp.adr "JSON Rendering and Formatting Approach"
```
