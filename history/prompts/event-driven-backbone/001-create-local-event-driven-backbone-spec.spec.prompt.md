---
id: 001
title: Create Local Event-Driven Backbone Spec
stage: spec
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: event-driven-backbone
branch: 001-event-driven-backbone
user: user
command: /sp.specify
labels: ["specification", "event-driven", "kafka", "dapr", "microservices", "real-time", "websocket"]
links:
  spec: specs/001-event-driven-backbone/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-event-driven-backbone/spec.md
  - specs/001-event-driven-backbone/checklists/requirements.md
tests:
  - None (specification phase)
---

## Prompt

/sp.specify Todo Full-Stack Web Application - Spec 11: Local Event-Driven Backbone

Target functionality:
- **Local Kafka Infrastructure:** Deploy and manage a Kafka Cluster on Minikube using the **Strimzi Operator** (KRaft mode for resource efficiency).
- **Dapr-Integrated Microservices:**
  - **Notification Service:** Consumer that listens to the `reminders` topic via Dapr Pub/Sub and logs "triggered" notifications.
  - **Recurring Task Service:** Consumer that listens for `task-completed` events, calculates the next date, and uses Dapr Service Invocation to create the new task.
  - **Audit Service:** A dedicated sink that captures every system event into a chronological activity log.
- **Next.js 16+ Real-time UI:** Implement a WebSocket or Server-Sent Events (SSE) bridge in the frontend to reflect Kafka `task-updates` in the UI without page refreshes.

Focus:
- **Local Orchestration:** Use **Helm v3** to package the entire local ecosystem (Dapr components, Strimzi Kafka, and the microservices).
- **Strict Decoupling:** Services must not share databases; all inter-service synchronization must happen via Kafka topics abstracted by Dapr.
- **Up-to-Date Documentation:** Utilize the **context7 MCP server** for the latest **Dapr 1.15+** pub/sub schemas and **Next.js 16.1+** streaming patterns.

Success criteria:
- Completing a task in the UI triggers a "Task Completed" event that the Recurring Service successfully processes.
- The Notification service logs a reminder at the exact second specified by the Dapr Jobs API callback.
- Multiple browser tabs stay in sync automatically when a task is updated in one of them.
- `kagent "analyze cluster health"` confirms all Kafka brokers and Dapr sidecars are operational on Minikube.

Constraints:
- **Environment:** Strictly Local (Minikube).
- **Tooling:** Strimzi Kafka, Dapr CLI, Next.js 16+, FastAPI.
- **Resources:** Configure Kafka and Zookeeper/KRaft to run within a 4GB RAM / 2-CPU Minikube limit.

Not building:
- Cloud-hosted Kafka (Redpanda/Confluent).
- Production CI/CD pipelines or Cloud Kubernetes provisioning.
- Real SMTP/Push notification integration (logging only).

## Response snapshot

Successfully created comprehensive specification for Local Event-Driven Backbone feature:

**Branch Created**: `001-event-driven-backbone`

**Specification Structure**:
- 4 prioritized user stories (P1-P4) with independent test criteria
- 10 functional requirements (FR-001 to FR-010)
- 12 event-driven requirements (EDR-001 to EDR-012)
- 10 measurable success criteria (SC-001 to SC-010)
- 6 edge cases covering failure scenarios and resource constraints
- 4 key entities (Task Event, Reminder Event, Audit Log Entry, WebSocket Connection)
- Comprehensive assumptions, constraints, and out-of-scope items

**User Stories**:
1. **P1 - Real-Time Task Synchronization**: Core user-facing value - automatic sync across browser tabs within 2 seconds
2. **P2 - Automatic Recurring Task Generation**: Automates task recreation for recurring activities
3. **P3 - Timely Task Reminder Notifications**: Proactive alerts at exact scheduled times
4. **P4 - System Activity Audit Trail**: Operational observability and debugging

**Key Requirements**:
- Kafka cluster deployment using Strimzi Operator in KRaft mode
- Three microservices with Dapr sidecar integration (Notification, Recurring Task, Audit)
- Real-time UI communication via WebSocket/SSE
- Strict service decoupling via Kafka topics
- Helm v3 packaging for reproducible deployments
- Resource constraints: 4GB RAM / 2-CPU Minikube

**Validation Results**:
✅ All checklist items passed
✅ No [NEEDS CLARIFICATION] markers
✅ Requirements are testable and unambiguous
✅ Success criteria are measurable and technology-agnostic
✅ Feature is ready for planning phase

**Files Created**:
- `specs/001-event-driven-backbone/spec.md` (173 lines)
- `specs/001-event-driven-backbone/checklists/requirements.md` (validation checklist)

## Outcome

- ✅ Impact: Created comprehensive, testable specification for event-driven architecture with Kafka, Dapr, and real-time UI. All requirements are measurable and technology-agnostic. Feature is ready for `/sp.plan` phase.
- 🧪 Tests: No tests at specification phase. Acceptance scenarios defined for each user story (16 total scenarios).
- 📁 Files: 2 files created (spec.md, requirements.md checklist)
- 🔁 Next prompts: `/sp.plan` to create implementation plan, or `/sp.clarify` if additional requirements clarification needed
- 🧠 Reflection: Specification successfully balances technical infrastructure requirements (Kafka, Dapr, Helm) with user-facing value (real-time sync, automatic recurrence, notifications). Event-driven requirements are comprehensive and specific. Resource constraints (4GB RAM / 2-CPU) are clearly documented.

## Evaluation notes (flywheel)

- Failure modes observed: None. Specification creation completed successfully with all validation checks passing.
- Graders run and results (PASS/FAIL):
  - Content Quality: PASS (no implementation details, focused on user value)
  - Requirement Completeness: PASS (all requirements testable, no clarifications needed)
  - Feature Readiness: PASS (ready for planning phase)
- Prompt variant (if applicable): Standard /sp.specify workflow
- Next experiment (smallest change to try): Consider adding performance benchmarks for event processing latency in success criteria (currently SC-009 specifies <500ms for 95% of events)
