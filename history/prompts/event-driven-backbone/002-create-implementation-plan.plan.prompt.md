---
id: 002
title: Create Implementation Plan for Event-Driven Backbone
stage: plan
date: 2026-02-13
surface: agent
model: claude-sonnet-4-5-20250929
feature: event-driven-backbone
branch: 001-event-driven-backbone
user: user
command: /sp.plan
labels: ["planning", "event-driven", "kafka", "dapr", "architecture", "microservices", "sse", "helm"]
links:
  spec: specs/001-event-driven-backbone/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-event-driven-backbone/plan.md
tests:
  - None (planning phase)
---

## Prompt

/sp.plan

Additional planning requirements provided:
- Event Flow Diagram: Visualize the flow from user action → FastAPI → Kafka → Dapr Pub/Sub → Microservices
- Service Structure: Organize microservices under `/services` directory (notification, recurring, audit)
- Research Approach: Use context7 MCP server for latest Dapr 1.15+, Next.js 16.1+, Strimzi, and Kafka documentation
- Quality Validation: Ensure idempotency patterns for event processing
- Decisions Needing Documentation:
  1. Topic Partitioning Strategy (how many partitions for task events vs reminders)
  2. Dapr Component Scoping (namespace-scoped vs application-scoped)
  3. UI Sync Strategy (WebSocket vs Server-Sent Events)
- Testing Strategy:
  1. E2E Event Trace: Verify complete flow from UI action to microservice processing
  2. Job Callback Test: Validate Dapr Jobs API triggers notifications at exact scheduled time
  3. State Consistency: Ensure all browser tabs reflect same task state
  4. Idempotency Test: Verify duplicate events are handled correctly
- Technical Details:
  - Phase 0: Research (Strimzi, Dapr, Next.js SSE, Kafka config, distributed tracing)
  - Phase 1: Design (data models, API contracts, quickstart guide)
  - Phase 2: Infrastructure (Helm charts, Dapr components, Kafka topics)
  - Phase 3: Implementation (microservices, SSE bridge, event publishers)

## Response snapshot

Successfully created comprehensive implementation plan for Local Event-Driven Backbone feature:

**Plan Structure**:
- Technical Context: All required fields populated (feature name, branch, dependencies, constitution version)
- Constitution Check: All Phase-V requirements validated and aligned
- Project Structure: Detailed directory layout showing existing structure + new `/services` directory for microservices
- Event-Driven Architecture Decisions:
  - Communication Patterns: Async via Dapr Pub/Sub for events, sync via Dapr Service Invocation for task creation
  - Dapr Components: State Store (PostgreSQL), Pub/Sub (Kafka), Secrets (Kubernetes), Jobs (Scheduler)
  - Event Schema: 6 event types defined (task.created, task.updated, task.completed, task.deleted, reminder.scheduled, audit.logged)
  - Distributed Tracing: OpenTelemetry with Dapr tracing enabled
- Architecture Decisions (3 documented):
  1. **Topic Partitioning Strategy**: 3 partitions for task events (load distribution), 1 partition for reminders (ordering guarantee)
  2. **Dapr Component Scoping**: Application-scoped with explicit subscriptions (better isolation and security)
  3. **UI Sync Strategy**: Server-Sent Events (SSE) chosen over WebSocket (simpler implementation, automatic reconnection, HTTP/2 multiplexing)
- Testing Strategy: 4 test types defined (E2E event trace, job callback, state consistency, idempotency)
- Phase 0 Research Tasks: 5 research items for Strimzi, Dapr, Next.js SSE, Kafka configuration, and distributed tracing
- Phase 1 Design Artifacts: data-model.md, contracts/ directory, quickstart.md

**Key Decisions**:
- **SSE over WebSocket**: Chose Server-Sent Events for UI sync due to simpler implementation, automatic reconnection, and better HTTP/2 support
- **Application-Scoped Dapr Components**: Better isolation and security compared to namespace-scoped
- **3 Partitions for Task Events**: Balances load distribution with resource constraints (4GB RAM / 2-CPU Minikube)

**Research Phase**:
Attempted to use context7 MCP server for Phase 0 research but encountered API key error. Research tasks documented for manual execution:
1. Strimzi Operator KRaft mode configuration
2. Dapr 1.15+ Pub/Sub and Jobs API patterns
3. Next.js 16.1+ Server-Sent Events implementation
4. Kafka topic configuration for resource-constrained environments
5. Distributed tracing with OpenTelemetry and Dapr

**Files Created**:
- `specs/001-event-driven-backbone/plan.md` (506 lines)

## Outcome

- ✅ Impact: Created comprehensive implementation plan with 3 documented architecture decisions (topic partitioning, Dapr scoping, SSE vs WebSocket), detailed event schema design, testing strategy, and phased execution approach. Plan aligns with Constitution v3.0.0 Phase-V Event-Driven Architecture standards.
- 🧪 Tests: No tests at planning phase. Testing strategy defined with 4 test types (E2E event trace, job callback, state consistency, idempotency).
- 📁 Files: 1 file created (plan.md with 506 lines)
- 🔁 Next prompts: Execute Phase 0 research tasks (manual or via context7 when API key resolved), create research.md, then proceed to Phase 1 design artifacts (data-model.md, contracts/, quickstart.md), followed by `/sp.tasks` for task generation
- 🧠 Reflection: Planning phase successfully completed with comprehensive architecture decisions documented. SSE chosen over WebSocket for UI sync provides simpler implementation path while meeting real-time requirements. Application-scoped Dapr components provide better isolation. Topic partitioning strategy (3 for tasks, 1 for reminders) balances performance with resource constraints. Ready for research and design phases.

## Evaluation notes (flywheel)

- Failure modes observed: Context7 MCP server API key error prevented automated research phase. Workaround: documented research tasks for manual execution.
- Graders run and results (PASS/FAIL):
  - Constitution Alignment: PASS (all Phase-V requirements validated)
  - Architecture Decisions: PASS (3 decisions documented with rationale and tradeoffs)
  - Testing Strategy: PASS (4 test types defined with clear acceptance criteria)
  - Phased Approach: PASS (Phase 0 research, Phase 1 design clearly defined)
- Prompt variant (if applicable): Standard /sp.plan workflow with additional planning requirements
- Next experiment (smallest change to try): Resolve context7 API key issue to enable automated research phase, or proceed with manual research using official documentation sources (Dapr docs, Strimzi docs, Next.js docs)
