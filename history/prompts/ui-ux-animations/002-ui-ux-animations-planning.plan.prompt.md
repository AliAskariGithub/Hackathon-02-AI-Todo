---
id: 2
title: UI UX Animations Planning
stage: plan
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: ui-ux-animations
branch: 004-todo-ui-ux-animations
user: unknown
command: "/sp.plan"
labels: ["ui-ux", "animations", "planning", "architecture"]
links:
  spec: ../specs/004-todo-ui-ux-animations/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-todo-ui-ux-animations/plan.md
 - specs/004-todo-ui-ux-animations/research.md
 - specs/004-todo-ui-ux-animations/data-model.md
 - specs/004-todo-ui-ux-animations/quickstart.md
 - specs/004-todo-ui-ux-animations/contracts/ui-contracts.md
 - .specify/memory/agent-context.md
tests:
 - none
---

## Prompt

Spec 4: Advanced UI/UX & Animations

Create:
- **Theme Engine:** Set up `next-themes` provider with the custom color palette (#0FFF50, #161616, etc.).
- **Font Integration:** Configure `next/font/google` for Boldonse and Montserrat.
- **Animation Wrappers:** Create a `PageWrapper` component using `framer-motion` for consistent entry/exit animations.
- **Dashboard Redesign:** - Build the "Stats" row with 3 animated cards.
    - Implement the 'Create Task' Dialog using Shadcn's `Dialog` component.
- **Loading System:** Map out specific `skeleton.tsx` files for the Dashboard and Task list.

Decisions needing documentation:
- **Animation Weights:** Choosing between `spring` vs `tween` transitions (Recommended: `spring` for UI elements to feel "organic").
- **Theme Persistence:** Using local storage via `next-themes` to remember user preference.

Testing strategy:
- **Visual Regression:** Check that "Boldonse" headings are correctly rendering in Uppercase.
- **Motion Test:** Ensure Dialog popups don't cause scroll-bar flickering.
- **Theme Contrast:** Verify that the primary green (#0FFF50) is legible in both Light and Dark modes.

Technical details:
- Use Context7 MCP for Framer Motion + Next.js 16.1.2 "App Router" compatibility notes.
- Ensure all Shadcn components are updated to the latest version to support the theme variables.

## Response snapshot

Completed comprehensive planning for the Advanced UI/UX & Animations feature, including architecture decisions, research findings, data models, contracts, and quickstart guide.

## Outcome

- ✅ Impact: Created complete implementation plan for UI/UX animations with theme engine, font integration, animation wrappers, dashboard redesign, and loading system
- 🧪 Tests: none
- 📁 Files: specs/004-todo-ui-ux-animations/plan.md, research.md, data-model.md, quickstart.md, contracts/ui-contracts.md, .specify/memory/agent-context.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Thorough planning phase ensures smooth implementation with proper research into font availability and animation best practices.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A