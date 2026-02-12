---
id: 003
title: Phase-V Event-Driven Architecture Constitution
stage: constitution
date: 2026-02-11
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: main
user: user
command: /sp.constitution
labels: ["constitution", "phase-v", "event-driven", "dapr", "kafka", "strimzi"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

```text
Project Constitution: Phase-V (Advanced Cloud-Native & Event-Driven)

## 1. Core Mission & Architectural Governance
* **Decoupled Evolution:** The system must transition from direct service-to-service communication to an **Event-Driven Architecture (EDA)**.
* **Infrastructure Abstraction:** Use **Dapr (Distributed Application Runtime)** as the universal interface for all infrastructure building blocks (State, Pub/Sub, Secrets, Jobs).
* **The "Agentic" Standard:** No manual code or YAML. All logic, manifests, and pipelines must be generated via Spec-Driven Development (SDD) using Claude Code, Gordon, kubectl-ai, and Kagent.

---

## 2. Advanced Feature Standards
* **Intelligence & Reliability:** AI responses must be concise (Simple English) but backed by technical JSON data for tool execution accuracy.
* **Scheduling:** Use **Dapr Jobs API** for exact-time reminders. Polling-based cron jobs are prohibited for user notifications.
* **Search & Discovery:** Implement server-side filtering and sorting as the primary method for task retrieval.

---

## 3. Infrastructure & DevOps Standards
### **Distributed Runtime (Dapr)**
* **Sidecar Pattern:** Every microservice pod must be injected with a Dapr sidecar.
* **Portability:** Components (State, Pub/Sub) must be defined in YAML. Code must remain "cloud-agnostic"—swapping Kafka for Redpanda must require zero code changes.

### **Event Streaming (Kafka)**
* **Strimzi Governance:** Local Kafka instances must be managed by the Strimzi Operator.
* **Event Schema:** All events must follow a standardized JSON schema including `event_type`, `payload`, `user_id`, and `timestamp`.

### **Cloud & CI/CD**
* **Provider Neutrality:** While targeting Azure (AKS) or Oracle (OKE), Helm charts must remain generic enough for any CNCF-compliant cluster.
* **Automated Verification:** GitHub Actions must include a "Dapr Validation" step to ensure sidecars and components are healthy before deployment.

---

## 4. AIOps & Agent Responsibilities
* **Claude Code (The Lead):** Orchestrates logic refactors (Spec 10) and CI/CD setup (Spec 12).
* **Gordon (Docker AI):** Optimizes multi-service container builds for the new microservices (Notification, Recurring Task, Audit).
* **kubectl-ai & Kagent:** Responsible for generating complex Dapr/Kafka manifests and performing SRE-level health audits on the distributed mesh.

---

## 5. Technology Stack (Phase-V)
| Layer | Technology |
| :--- | :--- |
| **Runtime** | Dapr (Distributed Application Runtime) |
| **Messaging** | Kafka (Strimzi / Redpanda Cloud) |
| **Orchestration** | Kubernetes (Minikube / AKS / OKE) |
| **Database** | Neon PostgreSQL (via Dapr State Store) |
| **Language** | FastAPI (Backend) & Next.js 16 (Frontend) |
| **CI/CD** | GitHub Actions & Helm v3 |

---

## 6. Security & Observability
* **Secrets:** All credentials must be stored in Kubernetes Secrets or Azure Key Vault, accessed exclusively via the **Dapr Secrets API**.
* **Tracing:** Distributed tracing must be enabled to visualize the flow of a message from the Chatbot, through Kafka, to the Notification service.
```

## Response snapshot

Successfully updated the project constitution from v2.0.0 to v3.0.0 with Phase-V Event-Driven Architecture principles.

**Key Changes:**
1. **Core Mission**: Added Event-Driven Architecture (EDA) mandate and Dapr infrastructure abstraction requirements
2. **Distributed Runtime (Dapr)**: New section mandating Dapr sidecars for all microservices, component portability, and building block usage standards
3. **Event Streaming (Kafka)**: New section with Strimzi governance, standardized event schema, and topic naming conventions
4. **Technology Stack**: Added Dapr v1.14+, Kafka (Strimzi/Redpanda Cloud) to required versions
5. **Security**: Mandated Dapr Secrets API for all credential access (prohibited direct environment variable access)
6. **Operational Standards**: Added distributed tracing requirements and CI/CD Dapr validation steps
7. **AIOps Governance**: Expanded agent responsibilities for Dapr/Kafka manifest generation
8. **Prohibited Patterns**: Polling-based cron jobs for user notifications (replaced with Dapr Jobs API)

**Version Bump Rationale (MAJOR 2.0.0 → 3.0.0):**
Introduces backward-incompatible architectural paradigm shift from direct service communication to Event-Driven Architecture (EDA), mandates Dapr sidecars for all microservices, prohibits previously valid patterns (polling-based cron), and requires fundamental infrastructure changes (Kafka, Dapr components).

**Sync Impact Report:**
- Modified principles: Core Mission, Infrastructure Standards, Technology Stack, AIOps Governance, Security, Operational Standards
- Added sections: Distributed Runtime (Dapr) Standards, Event Streaming (Kafka) Standards, Event Schema Standards, Cloud Provider Neutrality
- Removed sections: None (all Phase-I through Phase-IV principles retained)
- Templates requiring updates: plan-template.md, spec-template.md, tasks-template.md (flagged for validation)

## Outcome

- ✅ Impact: Constitution updated to v3.0.0 with comprehensive Phase-V Event-Driven Architecture principles, Dapr infrastructure abstraction, Kafka event streaming standards, and distributed tracing requirements
- 🧪 Tests: No automated tests (constitution is a governance document)
- 📁 Files: Updated .specify/memory/constitution.md (v2.0.0 → v3.0.0)
- 🔁 Next prompts: Validate and update plan-template.md, spec-template.md, and tasks-template.md to align with new Dapr/Kafka architecture decision sections and event-driven requirements
- 🧠 Reflection: Successfully captured all Phase-V requirements including Dapr sidecar pattern, event schema standardization, Dapr Jobs API mandate, cloud provider neutrality, and distributed tracing. The MAJOR version bump is justified due to the fundamental architectural paradigm shift and prohibition of previously valid patterns.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All placeholders filled, version incremented correctly, sync impact report complete, no unresolved tokens
- Prompt variant (if applicable): Standard constitution update workflow
- Next experiment (smallest change to try): Validate template consistency with new constitution principles, particularly Dapr component and event schema task categories in tasks-template.md
