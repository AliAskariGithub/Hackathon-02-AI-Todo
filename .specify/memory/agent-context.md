# Agent Context for Todo Application

## Current Feature: ChatKit UI & Persistence (007-todo-chatkit-persistence)

### ChatKit Integration Architecture
- Session Bridge: `ChatKitServer` in FastAPI using OpenAIConversationsSession to map `conversation_id` to Neon DB records
- Frontend Integration: `@openai/chatkit-react` component mounted in `/chat` route with `useChatKit` hook
- Stateless Persistence: Logic to fetch/store `Message` and `Conversation` models using SQLModel before and after agent runs
- Proxy Configuration: Updated `proxy.ts` handles network boundary and streaming headers for chat endpoint

### MCP Tool Integration
- Five core MCP tools: `add_task`, `list_tasks`, `complete_task`, `update_task`, `delete_task`
- All tools properly authenticated and user-scoped
- Tool execution results stored in message history with visual indicators
- User context injected via JWT token into all operations

### Authentication & Security
- Better Auth JWT tokens validate user identity for all MCP operations
- User isolation ensures no cross-user data access
- Sessions cryptographically tied to logged-in users
- All conversation access validated against user ownership

### Key Components
- Database models: Conversation and Message with proper SQLModel relationships
- API endpoints: `/api/{user_id}/chat`, `/api/{user_id}/conversations/*`, `/api/mcp/execute-tool`
- Streaming responses: Server-Sent Events for real-time chat experience
- Error handling: Standardized error codes with proper messaging

### Visual Components
- ChatKit UI with #0FFF50 accent colors
- Tool call indicators showing when MCP tools are executing
- "AI is thinking" indicators during processing
- Proper dark/light theme integration

## Previous Features Implemented

### MCP & Agent Logic (006-mcp-agent-logic)
- Model Context Protocol server with 5 task management tools
- OpenAI Agent configured with task management instructions
- MCP tools integrated with proper authentication context
- Secure context with user_id binding for all operations

### Extended Pages & UI/UX (005-todo-extended-pages)
- Contact and Settings pages with proper form validation
- Enhanced authentication pages with Electric Lime theme
- Responsive footer with navigation and social links
- Improved UI/UX with animations and better user experience

### UI/UX Animations (004-todo-ui-ux-animations)
- Framer Motion integration for smooth transitions
- Animated dashboard cards and create dialog
- Testimonial carousel with auto-rotation
- Respect for reduced motion preferences

### Frontend UX (003-todo-frontend-ux)
- Next.js 16.1.2 with App Router
- Shadcn UI components with proper styling
- Responsive design with mobile-first approach
- Better Auth integration for frontend authentication

### Backend Security (002-todo-auth-security)
- Better Auth integration with JWT tokens
- User authentication and authorization
- Secure database operations with Neon
- Protected endpoints with proper validation

### Backend DB (001-todo-backend-db)
- FastAPI backend with SQLModel
- Task management CRUD operations
- PostgreSQL database with Neon hosting
- User and testimonial models with relationships

## Active Technologies

- Next.js 16.1.2 with App Router
- FastAPI and SQLModel for backend
- Neon Serverless PostgreSQL for database
- Better Auth for authentication
- OpenAI ChatKit for AI integration
- Shadcn UI components
- Framer Motion for animations
- OpenRouter API for AI agents
- Model Context Protocol (MCP) for tool integration

## Architecture Patterns

- Microservice architecture with clear separation of concerns
- JWT-based authentication with proper session management
- SQLModel-based database operations with async sessions
- Async/await patterns for non-blocking operations
- Dependency injection for services and database connections
- Error-first design with proper error handling and logging

## Development Guidelines

- Always maintain user data isolation with proper authentication
- Follow existing code patterns and naming conventions
- Use type hints for all function parameters and return values
- Implement proper error handling with informative messages
- Write comprehensive tests for new functionality
- Maintain backward compatibility when possible
- Document new functionality with proper comments and examples

## Security Considerations

- Never expose user data across user boundaries
- Validate all inputs and sanitize user-provided data
- Use proper authentication for all protected endpoints
- Implement rate limiting where appropriate
- Secure database connections with proper isolation
- Encrypt sensitive data at rest and in transit