# Interactive Chat Experience - Testing Guide

**Feature ID**: 008-todo-interactive-chat
**Status**: Ready for Testing
**Date**: 2026-02-08

## Prerequisites

Before testing, ensure both frontend and backend are running:

```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -m uvicorn src.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Access the application at: `http://localhost:3000`

## Test Scenarios

### User Story 1: Basic Chat Interaction with Readable Responses

**Test ID**: T015
**Goal**: Verify AI responds in simple, grade 6-8 reading level language

**Steps**:
1. Navigate to `/chat`
2. Send message: "show me my tasks"
3. Observe the AI response

**Expected Results**:
- ✓ Response uses simple, clear English
- ✓ No technical jargon or complex vocabulary
- ✓ Short sentences (15-20 words max)
- ✓ Friendly, conversational tone

**Example Good Response**:
> "Here are your tasks. You have 3 tasks to do. Would you like me to show you the details?"

**Example Bad Response**:
> "I have retrieved your task collection from the database. The query returned 3 entities with pending status. Would you like me to enumerate the comprehensive details?"

---

### User Story 2: Keyboard-Driven Chat Navigation

**Test ID**: T052
**Goal**: Verify all keyboard shortcuts work without conflicts

**Keyboard Shortcuts to Test**:

| Shortcut | Action | Expected Behavior |
|----------|--------|-------------------|
| `Cmd/Ctrl + K` | Focus chat input | Input field receives focus with ring animation (300ms) |
| `Enter` | Send message | Message sends (without Shift key) |
| `Shift + Enter` | New line | Adds line break in message |
| `Esc` | Exit focus mode | Exits focus mode if active, otherwise blurs input |

**Steps**:
1. Navigate to `/chat`
2. Test each keyboard shortcut
3. Verify visual feedback appears
4. Check keyboard shortcut hints are visible below input

**Expected Results**:
- ✓ All shortcuts work as described
- ✓ Visual feedback appears (ring animation on focus)
- ✓ Keyboard shortcut hints visible on desktop (hidden on mobile)
- ✓ No conflicts with browser shortcuts

**Cross-Browser Testing** (T052):
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

---

### User Story 3: Focus Mode for Distraction-Free Chat

**Test ID**: T028
**Goal**: Verify focus mode transitions meet <500ms performance target

**Steps**:
1. Navigate to `/chat`
2. Open browser DevTools (F12)
3. Go to Performance tab
4. Start recording
5. Click "Focus Mode" button
6. Stop recording after animation completes
7. Measure transition duration

**Expected Results**:
- ✓ Focus mode activates smoothly
- ✓ Background fades with backdrop blur
- ✓ Chat centers with expanded width
- ✓ Transition completes in <500ms
- ✓ Escape key exits focus mode
- ✓ Body scroll prevented when active

**Performance Measurement**:
```
Target: <500ms
Overlay fade: 300ms
Content scale: 300ms (with 100ms delay)
Total: ~400ms ✓
```

**Accessibility Testing** (T053):
1. Enable "Reduce Motion" in OS settings
2. Toggle focus mode
3. Verify animations are disabled or simplified

**ARIA Testing** (T054, T055):
- [ ] Focus mode has `role="dialog"`
- [ ] Focus mode has `aria-modal="true"`
- [ ] Screen reader announces "Focus mode" when activated
- [ ] Keyboard navigation works correctly

---

### User Story 4: Direct Task Navigation from Chat

**Test ID**: T036
**Goal**: Test task link navigation with existing and non-existent task IDs

**Setup**:
1. Create a test task via the dashboard (note the task ID)
2. Navigate to `/chat`

**Test Cases**:

#### Case 1: Existing Task
**Steps**:
1. Send message: "show me task #[TASK_ID]" (replace with actual ID)
2. Wait for AI response
3. Click the task link in the response

**Expected Results**:
- ✓ Task reference parsed correctly
- ✓ Task link button appears with Neon Green color (#0FFF50)
- ✓ Clicking link shows loading state
- ✓ Navigates to `/dashboard/tasks/[TASK_ID]?source=chat`
- ✓ Task detail page loads successfully

#### Case 2: Non-Existent Task
**Steps**:
1. Send message: "show me task #99999"
2. Wait for AI response
3. Click the task link in the response

**Expected Results**:
- ✓ Task link button appears
- ✓ Clicking link shows loading state
- ✓ Toast notification appears: "Task not found"
- ✓ Error message: "Task #99999 does not exist or you don't have access to it."
- ✓ No navigation occurs

#### Case 3: Task Reference Parsing
**Test Patterns**:
- "task #123" → Should parse ✓
- "task 123" → Should parse ✓
- "Task #456" → Should parse ✓ (case insensitive)
- "#789" (without "task") → Should NOT parse ✗

---

### User Story 5: Structured Data Viewing with JSON Toggle

**Test ID**: T044, T045
**Goal**: Verify display mode toggle performance and JSON rendering

#### Performance Test (T044)
**Steps**:
1. Navigate to `/chat`
2. Send a message and wait for response
3. Open browser DevTools Performance tab
4. Start recording
5. Click "JSON" button to toggle display mode
6. Stop recording
7. Measure toggle duration

**Expected Results**:
- ✓ Display mode toggles instantly
- ✓ Transition completes in <200ms
- ✓ Preference persists to localStorage
- ✓ All messages re-render in new mode

**Performance Measurement**:
```
Target: <200ms
State update: ~50ms
Re-render: ~100ms
Total: ~150ms ✓
```

#### Large Response Test (T045)
**Steps**:
1. Send message: "list all my tasks with full details"
2. Wait for response (should be >1KB)
3. Toggle to JSON mode
4. Observe rendering performance

**Expected Results**:
- ✓ JSON renders without lag
- ✓ Syntax highlighting applied (monokai theme)
- ✓ Objects collapsed at level 1
- ✓ Copy to clipboard works
- ✓ No performance degradation with 10KB+ responses

**JSON Display Features**:
- [ ] Monokai theme applied
- [ ] Objects collapsed at level 1
- [ ] Data types hidden
- [ ] Object sizes shown
- [ ] Clipboard copy enabled
- [ ] Tool calls included in JSON

---

## Cross-Cutting Concerns Testing

### Responsive Design (T058)

**Mobile Testing**:
1. Open DevTools and toggle device toolbar
2. Test on various screen sizes:
   - iPhone SE (375px)
   - iPhone 12 Pro (390px)
   - iPad (768px)
   - Desktop (1920px)

**Expected Results**:
- ✓ Keyboard shortcut hints hidden on mobile
- ✓ Focus mode adjusts margins (mx-2 on mobile, mx-4 on desktop)
- ✓ Focus mode height adjusts (h-[90vh] on mobile, h-[85vh] on desktop)
- ✓ All buttons remain accessible
- ✓ Text remains readable

**Physical Device Testing**:
- [ ] iOS device (iPhone/iPad)
- [ ] Android device (phone/tablet)

### Color Contrast (T054)

**WCAG AA Compliance**:
1. Use browser extension (e.g., axe DevTools)
2. Check contrast ratios for:
   - Task link buttons (#0FFF50 on background)
   - Keyboard shortcut hints
   - Focus mode overlay
   - JSON display text

**Required Ratios**:
- Normal text: 4.5:1 minimum
- Large text: 3:1 minimum
- UI components: 3:1 minimum

### Screen Reader Testing (T055)

**Tools**:
- Windows: NVDA or JAWS
- macOS: VoiceOver (Cmd + F5)
- Linux: Orca

**Test Scenarios**:
1. Navigate to chat page
2. Activate screen reader
3. Tab through interface
4. Activate focus mode
5. Toggle display mode
6. Click task link

**Expected Announcements**:
- "Focus Mode button, not pressed"
- "JSON button, not pressed"
- "Task link, Task #123"
- "Focus mode dialog"
- "Chat input, edit text"

---

## Integration Testing (T059)

**Goal**: Verify all user stories work together without conflicts

**Comprehensive Test Flow**:
1. Navigate to `/chat`
2. Press `Cmd/Ctrl + K` to focus input (US2)
3. Type: "show me my tasks" (US1)
4. Press `Enter` to send (US2)
5. Verify simple language response (US1)
6. Click task link in response (US4)
7. Navigate back to chat
8. Click "Focus Mode" button (US3)
9. Verify focus mode active
10. Click "JSON" button (US5)
11. Verify JSON display
12. Press `Esc` to exit focus mode (US3)
13. Verify all features still work

**Expected Results**:
- ✓ No conflicts between features
- ✓ State persists correctly
- ✓ Animations don't interfere
- ✓ Keyboard shortcuts work in all modes
- ✓ Display mode persists after focus mode toggle

---

## Performance Audit (T056)

**Metrics to Measure**:

| Feature | Target | Measurement Method |
|---------|--------|-------------------|
| Focus Mode Transition | <500ms | DevTools Performance tab |
| Display Mode Toggle | <200ms | DevTools Performance tab |
| Keyboard Shortcut Response | <100ms | DevTools Performance tab |
| Task Link Validation | <1000ms | Network tab |
| JSON Rendering (10KB) | <500ms | DevTools Performance tab |

**Steps**:
1. Open DevTools Performance tab
2. Start recording
3. Perform action
4. Stop recording
5. Analyze timeline
6. Verify meets target

**Performance Tips**:
- Use Chrome DevTools Lighthouse for overall score
- Check for layout shifts (CLS)
- Verify no memory leaks
- Monitor bundle size impact

---

## Error Handling Testing

**Scenarios to Test**:

1. **Network Error**:
   - Disconnect network
   - Send chat message
   - Verify error message appears

2. **Task Link Error**:
   - Click non-existent task link
   - Verify toast notification

3. **Component Error**:
   - Trigger error in chat component
   - Verify error boundary catches it
   - Verify "Try Again" button works

4. **Rate Limit Error**:
   - Trigger rate limit (if applicable)
   - Verify countdown timer appears
   - Verify input disabled during rate limit

---

## Checklist Summary

### Functional Testing
- [ ] T015: Simple language responses verified
- [ ] T028: Focus mode performance <500ms
- [ ] T036: Task link navigation (existing and non-existent)
- [ ] T044: Display mode toggle performance <200ms
- [ ] T045: JSON rendering with large responses

### Cross-Browser Testing (T052, T057)
- [ ] Chrome (latest 2 versions)
- [ ] Firefox (latest 2 versions)
- [ ] Safari (latest 2 versions)
- [ ] Edge (latest 2 versions)

### Accessibility Testing (T053, T054, T055)
- [ ] Reduced motion preferences respected
- [ ] WCAG AA color contrast verified
- [ ] Screen reader testing completed
- [ ] Keyboard navigation verified

### Responsive Testing (T058)
- [ ] Mobile devices (iOS and Android)
- [ ] Tablet devices
- [ ] Desktop browsers
- [ ] Various screen sizes

### Integration Testing (T059)
- [ ] All features work together
- [ ] No conflicts between user stories
- [ ] State management works correctly

### Performance Testing (T056)
- [ ] Focus mode <500ms
- [ ] Display toggle <200ms
- [ ] Keyboard shortcuts <100ms
- [ ] Overall performance acceptable

### Documentation (T060)
- [x] README updated with keyboard shortcuts
- [x] IMPLEMENTATION_SUMMARY.md created
- [x] TESTING_GUIDE.md created (this file)

---

## Reporting Issues

When reporting issues, include:
1. Test ID (e.g., T015)
2. Browser and version
3. Steps to reproduce
4. Expected vs actual behavior
5. Screenshots or video if applicable
6. Console errors (if any)

**Issue Template**:
```
Test ID: T015
Browser: Chrome 120.0.6099.109
OS: Windows 11

Steps:
1. Navigate to /chat
2. Send message: "show me my tasks"
3. Observe response

Expected: Simple language response
Actual: Technical jargon used

Console Errors: None
Screenshot: [attach]
```

---

## Success Criteria

All tests must pass before marking the feature as complete:
- ✓ All functional tests pass (T015, T028, T036, T044, T045)
- ✓ Cross-browser compatibility verified (T052, T057)
- ✓ Accessibility requirements met (T053, T054, T055)
- ✓ Responsive design works on all devices (T058)
- ✓ Integration testing successful (T059)
- ✓ Performance targets met (T056)
- ✓ Documentation complete (T060)

**Current Status**: Implementation Complete - Ready for Testing Phase
