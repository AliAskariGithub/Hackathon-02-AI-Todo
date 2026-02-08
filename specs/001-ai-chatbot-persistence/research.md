# Research & Discovery: AI Chatbot & Persistence

**Feature**: AI Chatbot & Persistence | **Branch**: `001-ai-chatbot-persistence` | **Date**: 2026-02-07

## Research Tasks

### R1: OpenRouter AsyncOpenAI Client Configuration

**Question**: How to configure AsyncOpenAI client to point to OpenRouter's base URL and handle streaming responses?

**Research Approach**:
- Review AsyncOpenAI documentation for custom base_url configuration
- Verify streaming support with OpenRouter API
- Test connection with openai/gpt-oss-120b:free model
- Document authentication header requirements

**Expected Output**: Code pattern for initializing AsyncOpenAI client with OpenRouter configuration

**Status**: Pending

---

### R2: Next.js 16.1.2 Streaming Proxy Pattern

**Question**: What are the correct Response headers and streaming patterns for Next.js 16.1.2 App Router to proxy streaming AI responses?

**Research Approach**:
- Use Context7 MCP to fetch Next.js 16.1.2 Route Handler documentation
- Verify text/event-stream vs application/x-ndjson content types
- Test streaming with ReadableStream and TransformStream
- Document any Next.js 16-specific changes from previous versions

**Expected Output**: Working proxy.ts pattern for streaming OpenRouter responses through Next.js

**Status**: Pending

---

### R3: OpenAI ChatKit Integration

**Question**: How to integrate OpenAI ChatKit with custom backend API and streaming responses?

**Research Approach**:
- Review ChatKit documentation for custom API integration
- Verify compatibility with Next.js 16.1.2 App Router
- Test message rendering and streaming display
- Document configuration options for Shadcn UI styling

**Expected Output**: ChatKit setup pattern with custom API adapter

**Status**: Pending

---

### R4: MCP Tool Function Signatures

**Question**: What is the optimal function signature and docstring format for MCP tools to ensure the AI understands when and how to use them?

**Research Approach**:
- Review existing MCP tool implementations in backend/src/mcp/tools/
- Document best practices for tool descriptions
- Test AI tool selection with different docstring formats
- Verify JSON return format for task data

**Expected Output**: MCP tool template with clear docstrings and type hints

**Status**: Pending

---

### R5: Rate Limiting Implementation Strategy

**Question**: How to implement per-user rate limiting (20/min, 200/hour) in FastAPI with minimal performance overhead?

**Research Approach**:
- Evaluate in-memory vs Redis-based rate limiting
- Consider slowapi library vs custom implementation
- Test performance impact with 100 concurrent users
- Document cleanup strategy for expired rate limit data

**Expected Output**: Rate limiting middleware pattern for FastAPI

**Status**: Pending

---

### R6: Windows DNS Resolution Workaround

**Question**: How to resolve the Windows asyncio DNS resolution issue when calling OpenRouter from FastAPI?

**Research Approach**:
- Document the current issue (works in standalone script, fails in FastAPI)
- Test synchronous requests library with asyncio.to_thread()
- Verify if issue persists in Linux deployment environment
- Document workaround or deployment recommendation

**Expected Output**: Working solution or documented deployment constraint

**Status**: Pending

---

## Research Deliverable

All research findings will be consolidated in this document with:
- Decision made for each research task
- Rationale for the chosen approach
- Alternatives considered and why they were rejected
- Code examples or patterns to be used in implementation

## Next Steps

1. Execute each research task in order
2. Document findings and decisions
3. Update this file with results
4. Proceed to Phase 1 design artifacts
