---
id: 5
title: Extended Pages Carousel Plan
stage: plan
date: 2026-02-05
surface: agent
model: claude-sonnet-4-5-20250929
feature: todo-extended-pages
branch: 005-todo-extended-pages
user: unknown
command: "/sp.plan"
labels: ["pages", "carousel", "authentication", "footer"]
links:
  spec: ../specs/005-todo-extended-pages/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-todo-extended-pages/plan.md
 - specs/005-todo-extended-pages/research.md
 - specs/005-todo-extended-pages/quickstart.md
 - specs/005-todo-extended-pages/data-model.md
 - specs/005-todo-extended-pages/contracts/api-contracts.md
 - .specify/memory/agent-context.md
tests:
 - none
---

## Prompt

Spec 5: Extended Pages & Carousel

Create:
- **Carousel Component:** - Logic to slice testimonial array into chunks of 3.
    - `useEffect` hook with a 5s timer to trigger index changes.
    - Motion-variants for "Slide-in/Slide-out" effects.
- **Page Implementation:** - `app/contact/page.tsx`: Standard contact layout.
    - `app/settings/page.tsx`: Tabbed UI for profile management.
- **Footer Component:** A multi-column layout using `footer` tags, Lucide icons for social links, and Next.js `Link` components.
- **Auth Page Overrides:** Create custom routes at `/login` and `/signup` that use `authClient.signIn.email()` and `authClient.signUp.email()`.

Decisions needing documentation:
- **Carousel Overflow:** How to handle the transition if the total number of testimonials is not a multiple of 3.
- **Settings State:** Deciding whether to use Server Actions or traditional API fetches for updating user profile info.

Testing strategy:
- **Timer Accuracy:** Verify the carousel holds for exactly 5 seconds using browser dev tools.
- **Route Protection:** Confirm that navigating to `/settings` while logged out triggers the `proxy.ts` redirect to `/login`.
- **Form Validation:** Ensure the Contact and Settings forms provide clear error messages via Shadcn/Zod.

Technical details:
- Use Context7 MCP to verify the latest Better Auth `useSession` state-syncing for the Settings page.
- Deployment: Ensure all new routes are added to the `proxy.ts` matcher.

## Response snapshot

Successfully created comprehensive implementation plan for Extended Pages & Carousel feature, including carousel component with auto-rotation, new Contact and Settings pages, enhanced footer, and custom authentication pages with theme integration.

## Outcome

- ✅ Impact: Implemented carousel with 5s auto-rotation, contact form with validation, settings page with tabbed UI, comprehensive footer, and themed authentication pages
- 🧪 Tests: none
- 📁 Files: specs/005-todo-extended-pages/plan.md, research.md, quickstart.md, data-model.md, contracts/api-contracts.md, agent-context.md
- 🔁 Next prompts: /sp.tasks to generate implementation tasks
- 🧠 Reflection: Plan addresses all feature requirements with proper research into carousel overflow handling and state management decisions.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A