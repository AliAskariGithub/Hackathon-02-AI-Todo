# API Contracts: Extended Pages & Carousel

**Feature**: Extended Pages & Carousel
**Date**: 2026-02-05
**Status**: Draft

## Overview
This document outlines the API contracts for the Extended Pages & Carousel feature. Most of the functionality leverages existing APIs (authentication, user management), but this document also covers any new API endpoints needed for the feature.

## Existing API Integration

### Better Auth Integration
The custom authentication pages will use the Better Auth client API:

#### Login Endpoint
- **Method**: POST
- **Path**: `/api/auth/sign-in/email` (via authClient)
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "rememberMe": "boolean (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "data": {
      "user": {
        "id": "string",
        "email": "string",
        "name": "string",
        "image": "string (optional)",
        "emailVerified": "boolean"
      },
      "session": {
        "token": "string",
        "expiresAt": "string (ISO date)"
      }
    },
    "error": {
      "message": "string",
      "code": "string"
    }
  }
  ```

#### Signup Endpoint
- **Method**: POST
- **Path**: `/api/auth/sign-up/email` (via authClient)
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "name": "string",
    "image": "string (optional)"
  }
  ```
- **Response**:
  ```json
  {
    "data": {
      "user": {
        "id": "string",
        "email": "string",
        "name": "string",
        "image": "string (optional)",
        "emailVerified": "boolean"
      },
      "session": {
        "token": "string",
        "expiresAt": "string (ISO date)"
      }
    },
    "error": {
      "message": "string",
      "code": "string"
    }
  }
  ```

## New Form Endpoints

### Contact Form Submission
- **Method**: POST
- **Path**: `/api/contact`
- **Authentication**: Not required (public form)
- **Request Body**:
  ```json
  {
    "name": "string (min 2 chars)",
    "email": "string (valid email)",
    "subject": "string (min 5 chars)",
    "message": "string (min 10 chars)"
  }
  ```
- **Response** (Success - 200):
  ```json
  {
    "success": true,
    "message": "string (confirmation message)"
  }
  ```
- **Response** (Validation Error - 400):
  ```json
  {
    "success": false,
    "errors": {
      "field": ["error messages"]
    }
  }
  ```
- **Response** (Server Error - 500):
  ```json
  {
    "success": false,
    "message": "string (error message)"
  }
  ```

### Update User Profile
- **Method**: PUT
- **Path**: `/api/users/profile`
- **Authentication**: Required (JWT token in Authorization header)
- **Request Body**:
  ```json
  {
    "name": "string (min 2 chars)",
    "email": "string (valid email)",
    "bio": "string (max 280 chars, optional)",
    "avatar": "string (URL, optional)"
  }
  ```
- **Response** (Success - 200):
  ```json
  {
    "success": true,
    "user": {
      "id": "string",
      "name": "string",
      "email": "string",
      "bio": "string (optional)",
      "avatar": "string (optional)",
      "updatedAt": "string (ISO date)"
    }
  }
  ```
- **Response** (Validation Error - 400):
  ```json
  {
    "success": false,
    "errors": {
      "field": ["error messages"]
    }
  }
  ```
- **Response** (Unauthorized - 401):
  ```json
  {
    "success": false,
    "message": "Unauthorized: Invalid or expired token"
  }
  ```

### Get Testimonials
- **Method**: GET
- **Path**: `/api/testimonials`
- **Authentication**: Not required (public data)
- **Query Parameters**:
  - `limit`: number (optional, default: 9, for 3 pages of 3)
  - `offset`: number (optional, default: 0)
- **Response** (Success - 200):
  ```json
  {
    "testimonials": [
      {
        "id": "string",
        "author": "string",
        "position": "string (optional)",
        "company": "string (optional)",
        "quote": "string",
        "rating": "number (optional)",
        "avatar": "string (optional)",
        "createdAt": "string (ISO date)"
      }
    ],
    "pagination": {
      "total": "number",
      "currentPage": "number",
      "totalPages": "number",
      "hasNext": "boolean",
      "hasPrevious": "boolean"
    }
  }
  ```

## Server Actions Contracts

### Update Profile Server Action
- **Function**: `updateUserProfile(formData: FormData)`
- **Expected Form Fields**:
  - `name`: string (min 2 chars)
  - `email`: string (valid email)
  - `bio`: string (max 280 chars, optional)
- **Return Type**:
  ```ts
  {
    success: boolean;
    message: string;
    errors?: Record<string, string[]>;
  }
  ```

## Protected Route Validation

### Settings Route Protection
- **Route**: `/settings`
- **Middleware**: Authentication check
- **Behavior**: If user is not authenticated, redirect to `/login`
- **Expected Headers**:
  - `Authorization: Bearer {jwt_token}` (for API calls)
  - Cookie: `auth-token={token}` (for page access)

## Validation Schemas

### Contact Form Schema
```ts
interface ContactFormSchema {
  name: z.ZodString.min(2);
  email: z.ZodString.email();
  subject: z.ZodString.min(5);
  message: z.ZodString.min(10);
}
```

### Profile Update Schema
```ts
interface ProfileUpdateSchema {
  name: z.ZodString.min(2);
  email: z.ZodString.email();
  bio: z.ZodOptional<z.ZodString.max(280)>;
}
```

## Error Handling Contracts

### Standard Error Response Format
```ts
interface ErrorResponse {
  success: false;
  message: string;
  error_code?: string;
  details?: Record<string, unknown>;
}
```

### Validation Error Response Format
```ts
interface ValidationErrorResponse {
  success: false;
  message: "Validation failed";
  errors: Record<string, string[]>;
  error_code: "VALIDATION_ERROR";
}
```

## Security Considerations

### Rate Limiting
- Contact form submissions limited to 5 per hour per IP
- Auth endpoints limited to 10 attempts per minute per IP

### Input Sanitization
- All form inputs are sanitized before processing
- HTML content is escaped to prevent XSS
- Email validation follows RFC standards

### Authentication Headers
- All authenticated requests must include Authorization header
- JWT tokens are validated on every protected request
- Session timeouts are enforced