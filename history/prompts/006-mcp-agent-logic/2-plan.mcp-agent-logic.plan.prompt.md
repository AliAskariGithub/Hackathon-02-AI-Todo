---
id: 2
title: mcp-agent-logic-plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: mcp-agent-logic
branch: 006-mcp-agent-logic
user: Claude User
command: /sp.plan "Spec 6: MCP & Agent Logic..."
labels: ["plan", "mcp", "agent", "ai", "architecture"]
links:
  spec: ../../specs/006-mcp-agent-logic/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-mcp-agent-logic/plan.md
  - specs/006-mcp-agent-logic/research.md
  - specs/006-mcp-agent-logic/data-model.md
  - specs/006-mcp-agent-logic/contracts/mcp-tools-openapi.yaml
  - specs/006-mcp-agent-logic/quickstart.md
  - .specify/memory/agent-context.md
tests:
  - specs/006-mcp-agent-logic/research.md
  - specs/006-mcp-agent-logic/contracts/mcp-tools-openapi.yaml
---

## Prompt

Spec 6: MCP & Agent Logic

Create:
- **MCP Server:** Initialize `mcp = FastMCP("TodoServer")` and register the 5 task tools.
- **Agent Definition:** Create a `todo_agent = Agent(...)` with instructions for task management.
- **Runner Logic:** A utility function `run_task_agent(user_query, user_id)` that initializes the OpenAI Runner with access to the MCP tools.

Decisions needing documentation:
- **Tool Authentication:** Deciding to pass `user_id` as a hidden tool argument vs. a global context variable.
- **Error Mapping:** Standardizing MCP error codes so the Agent can explain *why* a task couldn't be deleted.

Testing strategy:
- Use the **MCP Inspector** tool to manually trigger `list_tasks` and verify Neon DB connectivity.
- Mock the LLM to verify that the correct Python function is called for specific natural language strings.

## Response snapshot

Successfully created comprehensive implementation plan for MCP & Agent Logic feature. Key deliverables include:

- **plan.md**: Complete architecture plan with technical context, constitution check, gates, and phased approach
- **research.md**: Detailed research findings resolving all unknowns about MCP SDK integration, OpenAI Agent configuration, JWT processing, and SQLModel integration
- **data-model.md**: Extended data model incorporating MCP tool context and task operation requests
- **contracts/mcp-tools-openapi.yaml**: Complete OpenAPI specification for all 5 MCP tools with security schemes and error responses
- **quickstart.md**: Developer quickstart guide with architecture overview and key patterns
- **agent-context.md**: Updated agent context with MCP-specific information

The plan addresses the key decisions:
- Chose explicit parameter approach for tool authentication (passing user_id as parameter)
- Defined standardized error codes for consistent error mapping
- Designed comprehensive API contracts with proper authentication context
- Planned testing strategy using MCP Inspector and natural language validation

## Outcome

- ✅ Impact: Comprehensive implementation plan created with all architectural decisions documented
- 🧪 Tests: Testing strategy defined with MCP Inspector and LLM mocking approaches
- 📁 Files: All planned artifacts created (plan, research, data model, contracts, quickstart, agent context)
- 🔁 Next prompts: Ready for /sp.tasks to generate development tasks or /sp.adr for architectural decisions
- 🧠 Reflection: Plan addresses all requirements with proper security context and standardized error handling

## Evaluation notes (flywheel)

- Failure modes observed: None - all architectural requirements met with proper security controls
- Graders run and results (PASS/FAIL): PASS - plan aligns with constitution and project requirements
- Prompt variant (if applicable): Original prompt implemented as specified
- Next experiment (smallest change to try): Generate development tasks from the plan