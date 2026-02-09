# Research: Todo Full-Stack Web Application - Modern Frontend & UX

**Date**: 2026-02-03

## Overview
This document captures the research findings and technical decisions made during the planning phase for implementing the frontend UX of the Todo application.

## Technology Research

### Next.js 16.1.2 with App Router
- **Decision**: Use Next.js 16.1.2 with App Router for the frontend architecture
- **Rationale**:
  - Leverages the latest Next.js features including server components, streaming, and improved bundling
  - App Router provides better performance and SEO compared to Pages Router
  - Aligns with the requirement to use Next.js 16.1.2
- **Alternatives considered**:
  - Create React App: Outdated approach, lacks SSR/SSG capabilities
  - Remix: Good alternative but Next.js has broader ecosystem support

### Better Auth Integration
- **Decision**: Integrate Better Auth for authentication management
- **Rationale**:
  - Provides robust authentication with JWT handling
  - Offers server-side session management
  - Integrates well with Next.js App Router
  - Handles social authentication if needed in future
- **Alternatives considered**:
  - NextAuth.js: Popular but Better Auth offers simpler setup
  - Clerk: Commercial solution with potential costs

### Shadcn UI Components
- **Decision**: Use Shadcn UI for consistent component design
- **Rationale**:
  - Provides accessible, customizable components
  - Integrates well with Tailwind CSS
  - Offers good documentation and community support
  - Maintains consistent design language across the application
- **Alternatives considered**:
  - Material UI: React-based but adds bundle size
  - Headless UI: Requires more customization work

### State Management and Optimistic Updates
- **Decision**: Implement `useOptimistic` hook for optimistic UI updates
- **Rationale**:
  - Provides better user experience with instant feedback
  - Part of React 18+ features, aligns with Next.js 16
  - Reduces perceived latency for task toggling and testimonial submission
- **Alternatives considered**:
  - Redux Toolkit: Overkill for this application size
  - Zustand: Good alternative but useOptimistic is React-native solution

## Architecture Patterns

### Client vs Server Components
- **Decision**: Use Server Components for static content (landing page) and Client Components for interactive elements (navbar, forms, modals)
- **Rationale**:
  - Server Components provide better performance and SEO
  - Client Components handle interactivity and state
  - Optimal balance between performance and functionality
- **Considerations**:
  - Authentication state requires Client Components
  - Need to carefully decide which components should be client vs server

### Proxy Strategy for Protected Routes
- **Decision**: Implement proxy.ts for handling protected routes
- **Rationale**:
  - Follows Next.js 16.1.2 "Edge-first" routing patterns
  - Provides centralized route protection
  - Handles authentication checks at the edge
- **Implementation details**:
  - Redirect unauthenticated users from /dashboard to login
  - Verify JWT tokens before allowing access to protected routes

### API Client Strategy
- **Decision**: Create centralized fetch wrapper that automatically attaches JWT
- **Rationale**:
  - Ensures consistent authentication headers across all API calls
  - Simplifies API integration
  - Centralizes error handling and request/response processing
- **Implementation approach**:
  - Extract JWT from Better Auth session
  - Attach as Authorization header to all backend API calls
  - Handle token refresh if needed

## Component Architecture

### Navbar Component
- **Decision**: Create auth-aware navbar with conditional rendering
- **Rationale**:
  - Provides consistent navigation across all pages
  - Dynamically updates based on authentication state
  - Sticky positioning for easy access
- **Key features**:
  - Shows Login/Register when logged out
  - Shows Dashboard/User button when logged in
  - Uses useSession() hook from Better Auth

### Testimonials Section
- **Decision**: Implement testimonial grid with modal for adding new testimonials
- **Rationale**:
  - Provides social proof on landing page
  - Modal prevents page navigation during submission
  - Clean, organized display of user feedback
- **Considerations**:
  - For Spec 3, testimonial storage is UI/frontend state only
  - Future implementation would connect to backend API

### Dashboard Implementation
- **Decision**: Create protected dashboard for task management
- **Rationale**:
  - Centralized location for user's personal tasks
  - Connects to Spec 2 API for user-specific data
  - Provides core value proposition of the application
- **Features**:
  - Displays user-specific tasks
  - Implements optimistic UI for task toggling
  - Protected route requiring authentication

## Responsive Design Strategy

### Mobile-First Approach
- **Decision**: Implement responsive design using Tailwind CSS with mobile-first approach
- **Rationale**:
  - Aligns with UI/UX standards in constitution
  - Ensures good experience across all device sizes
  - Simplifies development with Tailwind's utility classes
- **Breakpoints**:
  - Mobile: Up to 768px
  - Tablet: 768px - 1024px
  - Desktop: 1024px+

## Security Considerations

### JWT Token Handling
- **Decision**: Secure JWT token handling with proper httpOnly cookies where possible
- **Rationale**:
  - Prevents XSS attacks
  - Ensures secure transmission of authentication tokens
  - Aligns with security enforcement requirements
- **Implementation**:
  - Use Better Auth's built-in token management
  - Ensure tokens are not exposed in client-side logs
  - Implement proper token refresh mechanisms

### Protected Route Security
- **Decision**: Implement multiple layers of protection for sensitive routes
- **Rationale**:
  - Prevents unauthorized access to user data
  - Ensures data isolation requirements are met
  - Provides defense in depth approach
- **Layers**:
  - Client-side redirects
  - Server-side authentication checks
  - Backend API validation