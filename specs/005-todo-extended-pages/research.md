# Research: Extended Pages & Carousel Implementation

**Feature**: Extended Pages & Carousel
**Date**: 2026-02-05
**Status**: Completed

## Research Findings

### 1. Better Auth Custom Routes Research

#### Custom Login/Signup Routes Implementation
- **Finding**: Better Auth provides `authClient` for programmatic authentication
- **Decision**: Use Better Auth's signIn/signUp methods with custom UI
- **Rationale**: Maintains the same authentication flow while allowing custom UI design
- **Implementation**:
  - Login: `authClient.signIn.email({ email, password })`
  - Signup: `authClient.signUp.email({ email, password, name })`
- **Compatibility**: Compatible with existing auth patterns in the project

### 2. Carousel Overflow Research

#### Handling Testimonials That Don't Divide Evenly by 3
- **Finding**: Need to handle cases where testimonial count isn't divisible by 3
- **Decision**: Implement padding with empty placeholders to maintain grid consistency
- **Rationale**: Maintains visual consistency even when testimonials don't divide evenly
- **Implementation**:
  - Calculate chunks of 3 testimonials
  - If final chunk has < 3 items, pad with empty items or repeat testimonials
  - Alternative: Display remaining testimonials as a partial slide

#### Pagination and Chunking Patterns
- **Finding**: Array chunking is standard practice for carousels
- **Decision**: Use array slicing to create chunks of 3 testimonials
- **Rationale**: Provides predictable and efficient grouping
- **Implementation**: Slice array into groups of 3 with modulo arithmetic for overflow

### 3. Settings State Management Research

#### Server Actions vs Traditional API Fetches Comparison
- **Finding**: Server Actions are preferred in Next.js 16+ for mutations
- **Decision**: Use Server Actions for settings updates (Recommended approach)
- **Rationale**: Server Actions provide better performance, automatic loading states, and improved error handling
- **Implementation**: Create Server Actions for updating user profile and preferences

#### Better Auth Session Synchronization Patterns
- **Finding**: Better Auth provides `useSession` hook for real-time session updates
- **Decision**: Use `useSession` to automatically reflect profile changes
- **Rationale**: Ensures UI stays in sync with server state after updates
- **Implementation**: Call `useSession` to access and update user data after Server Action completion

### 4. Framer Motion Carousel Research

#### Best Practices for Automated Carousel Transitions
- **Finding**: Use useEffect with setInterval for automatic rotation
- **Decision**: Implement useEffect with cleanup to manage rotation interval
- **Rationale**: Prevents memory leaks and provides controlled automation
- **Implementation**: Set interval to 5000ms with cleanup function to clear interval

#### AnimatePresence Implementation for Layout Jump Prevention
- **Finding**: AnimatePresence manages enter/exit animations safely
- **Decision**: Wrap carousel slides with AnimatePresence for smooth transitions
- **Rationale**: Prevents layout jumps by properly handling DOM element removal/addition
- **Implementation**: Use AnimatePresence with proper keys to track slide changes

### 5. Form Validation Research

#### Zod Validation Patterns with Shadcn Form
- **Finding**: Shadcn Form integrates well with Zod for validation
- **Decision**: Use Zod schema validation with Shadcn Form components
- **Rationale**: Provides type-safe validation with good UX patterns
- **Implementation**: Define Zod schema and use with Shadcn Form's validation hooks

#### Accessibility Patterns for Form Validation
- **Finding**: Proper error messaging and ARIA attributes improve accessibility
- **Decision**: Include error messages with proper ARIA relationships
- **Rationale**: Ensures all users can understand and resolve form errors
- **Implementation**: Use aria-describedby and proper error message placement

## Architecture Decisions

### Carousel Overflow Handling
- **Decision**: Pad final chunk with duplicate items or placeholder cards
- **Rationale**: Maintains consistent grid layout even when testimonial count isn't divisible by 3
- **Alternatives Considered**:
  - Show partial grid: Creates inconsistent layout
  - Show all remaining items: May look odd if just 1 testimonial remains
- **Chosen**: Padding approach for visual consistency

### Settings State Management
- **Decision**: Use Server Actions for updating user profile info
- **Rationale**: Server Actions provide better developer experience, automatic optimistic updates, and improved error handling in Next.js App Router
- **Alternatives Considered**:
  - Traditional API fetches: Requires more boilerplate and client-side caching
  - Client-side mutations only: No optimistic updates, less reliable
- **Chosen**: Server Actions for optimal Next.js 16+ integration

### Carousel Automation Approach
- **Decision**: Use useEffect with setInterval for 5-second rotation
- **Rationale**: Provides precise timing with cleanup to prevent memory leaks
- **Alternatives Considered**:
  - CSS animations: Less control over timing and interaction
  - Third-party carousel libraries: Adds unnecessary complexity
- **Chosen**: useEffect approach for maximum control

## Best Practices Identified

### Performance
- Use transform and opacity properties for animations to ensure GPU acceleration
- Implement proper cleanup in useEffect hooks to prevent memory leaks
- Memoize expensive computations in carousel components
- Debounce resize handlers for responsive behavior

### Accessibility
- Implement proper keyboard navigation for carousel controls
- Ensure sufficient color contrast for Electric Lime theme
- Maintain focus management during page transitions
- Provide skip links for keyboard users in footer

### Theming
- Define theme variables consistently across components
- Use semantic color names rather than hardcoded values
- Maintain consistent spacing and sizing across themes
- Test all components in both light and dark modes

### Form Handling
- Implement progressive disclosure for complex forms
- Provide clear validation feedback near form controls
- Use appropriate input types for different data
- Implement proper loading states for form submissions

## Implementation Notes

### Context7 MCP Findings
- Better Auth's useSession hook properly synchronizes state in Next.js 16.1.2 App Router
- Framer Motion 12+ works seamlessly with Next.js 16.1.2 with no compatibility issues
- Server Actions in Next.js 16.1.2 provide excellent integration for form submissions

### Potential Issues & Solutions
- Carousel memory leaks: Implement proper useEffect cleanup
- Form validation errors: Use Zod for runtime validation
- Auth state desynchronization: Use Better Auth's session hooks for consistency
- Mobile performance: Optimize carousel for lightweight animations only