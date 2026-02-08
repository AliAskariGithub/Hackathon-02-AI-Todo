# Quickstart Guide: Todo Full-Stack Web Application - Modern Frontend & UX

**Date**: 2026-02-03

## Overview
This guide provides a quick overview of setting up and running the frontend for the Todo application.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Access to the backend API from Spec 2
- Better Auth configured with proper secrets

## Setup Instructions

### 1. Clone and Navigate
```bash
# Navigate to the project directory
cd frontend
```

### 2. Install Dependencies
```bash
npm install
# or
yarn install
```

### 3. Environment Configuration
Create a `.env.local` file in the frontend directory:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3001
BETTER_AUTH_SECRET=your-secret-key
```

### 4. Run Development Server
```bash
npm run dev
# or
yarn dev
```

The application will be available at `http://localhost:3000`

## Key Features

### Navigation
- The navbar is located in `src/components/Navbar.tsx`
- Uses `useSession()` from Better Auth to check authentication state
- Conditionally renders Login/Register (when logged out) or Dashboard/User button (when logged in)

### Landing Page
- Located at `src/app/page.tsx`
- Contains hero section and testimonials grid
- Includes 'Add Testimonial' button that opens a modal

### Authentication Pages
- Login page: `src/app/login/page.tsx`
- Register page: `src/app/register/page.tsx`
- Both use Shadcn UI components and React Hook Form

### Dashboard
- Located at `src/app/dashboard/page.tsx`
- Protected route that requires authentication
- Displays user-specific tasks from the backend API

## Development Commands

### Running in Development
```bash
npm run dev
```

### Building for Production
```bash
npm run build
```

### Running Tests
```bash
npm run test
```

### Linting
```bash
npm run lint
```

## API Integration
The frontend uses a centralized API client located at `src/lib/api-client.ts` that:
- Automatically attaches JWT tokens from Better Auth session
- Handles error responses
- Provides consistent request/response patterns

## Component Structure
- UI Components: `src/components/ui/` (Shadcn components)
- Main Components: `src/components/` (Navbar, Hero, etc.)
- Forms: `src/components/forms/` (Login, Register forms)
- Testimonials: `src/components/Testimonials/` (grid, modal, cards)
- Hooks: `src/hooks/` (custom React hooks)

## Key Technologies
- Next.js 16.1.2 with App Router
- Better Auth for authentication
- Shadcn UI for component library
- Tailwind CSS for styling
- React Hook Form for form handling
- React 19 features including useOptimistic for optimistic updates

## Troubleshooting

### Common Issues
1. **Authentication not working**: Ensure `BETTER_AUTH_SECRET` matches between frontend and backend
2. **API calls failing**: Verify `NEXT_PUBLIC_API_BASE_URL` points to running backend
3. **Styling issues**: Check that Tailwind CSS is properly configured

### Development Tips
- Use the proxy configuration in `src/app/proxy.ts` for protected routes
- Implement optimistic UI updates using the `useOptimistic` hook
- All API calls should go through the centralized client in `src/lib/api-client.ts`