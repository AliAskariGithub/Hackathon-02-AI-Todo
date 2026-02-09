# Data Model: Todo Full-Stack Web Application - Modern Frontend & UX

**Date**: 2026-02-03

## Overview
This document defines the data structures and state management for the frontend components of the Todo application.

## Frontend State Models

### Navigation State
- **Name**: Navigation State
- **Description**: Represents the current authentication status and determines which navigation items to display
- **Fields**:
  - isAuthenticated: boolean
  - userRole: string (optional)
  - userId: string (when authenticated)
- **Validation**:
  - isAuthenticated must be a boolean value
  - userId required when isAuthenticated is true
- **State Transitions**: Unauthenticated → Authenticated (login), Authenticated → Unauthenticated (logout)

### User Session
- **Name**: User Session
- **Description**: Contains authentication token and user identity information used for API calls and conditional rendering
- **Fields**:
  - token: string (JWT token from Better Auth)
  - user: object
    - id: string
    - email: string
    - name: string
  - expiresAt: Date
- **Validation**:
  - token must be a valid JWT format
  - user object must contain id and email
- **State Transitions**: Session created (login) → Session expired/invalidated (logout/token expiry)

### Testimonial Submission (UI State)
- **Name**: Testimonial Submission
- **Description**: Represents user feedback that can be submitted through the modal interface (UI/Frontend state only for this spec)
- **Fields**:
  - name: string (min length: 1, max length: 100)
  - email: string (valid email format)
  - rating: integer (1-5)
  - message: string (min length: 10, max length: 1000)
  - createdAt: Date
- **Validation**:
  - name required, 1-100 characters
  - email must be valid email format
  - rating must be between 1-5
  - message required, 10-1000 characters
- **State Transitions**: Form filled → Submitted (successful), Form filled → Validation error

### Protected Route State
- **Name**: Protected Route State
- **Description**: Represents pages that require authentication to access, with appropriate redirect behavior
- **Fields**:
  - route: string (URL path)
  - requiresAuth: boolean
  - redirectPath: string (where to redirect if not authenticated)
- **Validation**:
  - route must be a valid path
  - requiresAuth must be boolean
  - redirectPath required if requiresAuth is true
- **State Transitions**: Route accessed → Check authentication → Allow access/Deny access and redirect

## Component State Models

### Form State
- **Name**: Form State
- **Description**: Manages state for login and registration forms
- **Fields**:
  - formData: object
  - isSubmitting: boolean
  - errors: object
  - isValid: boolean
- **Validation**:
  - formData must match form schema
  - isSubmitting indicates form processing state
- **State Transitions**: Idle → Submitting → Success/Error

### Task State (for Dashboard)
- **Name**: Task State
- **Description**: Manages user's tasks in the dashboard with optimistic updates
- **Fields**:
  - tasks: array of task objects
  - isLoading: boolean
  - error: string (optional)
  - optimisticUpdates: map of pending updates
- **Validation**:
  - tasks must be an array of valid task objects
  - Each task must have id, title, description, completed status
- **State Transitions**: Loading → Loaded → Updated (with optimistic UI)

## API Response Models

### Auth API Response
- **Name**: Auth API Response
- **Description**: Structure of authentication API responses
- **Fields**:
  - success: boolean
  - user: object (user data if successful)
  - token: string (JWT token if successful)
  - error: string (error message if failed)
- **Validation**:
  - success must be boolean
  - user and token present only on successful login
  - error present only on failed login

### Task API Response
- **Name**: Task API Response
- **Description**: Structure of task-related API responses from backend
- **Fields**:
  - success: boolean
  - data: array/object (task data)
  - error: string (optional)
- **Validation**:
  - success must be boolean
  - data contains task information from backend API

## Component Interaction Models

### Navbar Props
- **Name**: Navbar Props
- **Description**: Properties passed to the Navbar component
- **Fields**:
  - user: object (current user data if authenticated)
  - isAuthenticated: boolean
- **Validation**:
  - user object present when isAuthenticated is true
  - All fields are read-only for the component

### Testimonial Grid Props
- **Name**: Testimonial Grid Props
- **Description**: Properties passed to the Testimonial Grid component
- **Fields**:
  - testimonials: array of testimonial objects
  - onAddTestimonial: function (callback to open modal)
- **Validation**:
  - testimonials must be an array
  - onAddTestimonial must be a function