# Data Model: Better Auth Migration with HTTP-Only Cookies

**Feature ID:** 009-better-auth-migration
**Date:** 2026-02-09
**Status:** Draft

---

## Overview

This document defines the data models, schemas, and data flow for the Better Auth migration. Since we're maintaining JWT-based authentication (just moving from localStorage to cookies), minimal database schema changes are required.

---

## Database Schema

### Existing Schema (No Changes Required)

#### User Table
**Table:** `user`
**Purpose:** Store user account information

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email address |
| user_name | VARCHAR(100) | NOT NULL | Username for login |
| password | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `user_name` (for login queries)

**Relationships:**
- One-to-Many with `task` table
- One-to-Many with `testimonial` table
- One-to-Many with `conversation` table

**No Changes Required:** Existing User table supports cookie-based authentication

---

### Optional: Sessions Table (Future Enhancement)

**Note:** Not implemented in Phase 1. JWT remains stateless.

If we want to add server-side session management in the future:

#### Sessions Table (Optional)
**Table:** `session`
**Purpose:** Track active user sessions for revocation capability

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique session identifier |
| user_id | UUID | FOREIGN KEY → user.id | User who owns this session |
| refresh_token_hash | VARCHAR(255) | NOT NULL | Hashed refresh token |
| access_token_jti | VARCHAR(255) | NULL | JWT ID of current access token |
| created_at | TIMESTAMP | NOT NULL | Session creation time |
| expires_at | TIMESTAMP | NOT NULL | Session expiration time |
| last_activity | TIMESTAMP | NOT NULL | Last request timestamp |
| ip_address | VARCHAR(45) | NULL | Client IP address |
| user_agent | TEXT | NULL | Client user agent |
| revoked | BOOLEAN | DEFAULT FALSE | Session revoked flag |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `user_id`
- INDEX on `refresh_token_hash`
- INDEX on `expires_at` (for cleanup)

**Future Benefits:**
- Session revocation (logout from all devices)
- Session management UI
- Security monitoring
- Audit trail

---

## JWT Token Structure

### Access Token Payload

**Token Type:** JWT (JSON Web Token)
**Algorithm:** HS256
**Expiration:** 15 minutes
**Storage:** HTTP-only cookie named `access_token`

**Payload Structure:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID (UUID)
  "email": "user@example.com",                     // User email
  "name": "John Doe",                              // User display name
  "type": "access",                                // Token type
  "iat": 1707494400,                               // Issued at (Unix timestamp)
  "exp": 1707495300                                // Expires at (Unix timestamp)
}
```

**Claims:**
- `sub` (Subject): User ID - primary identifier
- `email`: User email address
- `name`: User display name
- `type`: Token type identifier ("access")
- `iat` (Issued At): Token creation timestamp
- `exp` (Expiration): Token expiration timestamp

### Refresh Token Payload

**Token Type:** JWT (JSON Web Token)
**Algorithm:** HS256
**Expiration:** 7 days
**Storage:** HTTP-only cookie named `refresh_token`

**Payload Structure:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // User ID (UUID)
  "type": "refresh",                               // Token type
  "iat": 1707494400,                               // Issued at
  "exp": 1708099200                                // Expires at (7 days later)
}
```

**Claims:**
- `sub` (Subject): User ID - primary identifier
- `type`: Token type identifier ("refresh")
- `iat` (Issued At): Token creation timestamp
- `exp` (Expiration): Token expiration timestamp

**Security Note:** Refresh tokens contain minimal information to reduce exposure if compromised.

---

## Cookie Configuration

### Access Token Cookie

**Cookie Name:** `access_token`
**Value:** JWT string (e.g., `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

**Attributes:**
```http
Set-Cookie: access_token=<jwt_value>;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/;
  Max-Age=900
```

**Attribute Details:**
- `HttpOnly`: Prevents JavaScript access (XSS protection)
- `Secure`: Only sent over HTTPS (production)
- `SameSite=Lax`: CSRF protection, allows top-level navigation
- `Path=/`: Available for all routes
- `Max-Age=900`: 15 minutes (900 seconds)

### Refresh Token Cookie

**Cookie Name:** `refresh_token`
**Value:** JWT string

**Attributes:**
```http
Set-Cookie: refresh_token=<jwt_value>;
  HttpOnly;
  Secure;
  SameSite=Lax;
  Path=/api/auth/refresh;
  Max-Age=604800
```

**Attribute Details:**
- `HttpOnly`: Prevents JavaScript access
- `Secure`: Only sent over HTTPS (production)
- `SameSite=Lax`: CSRF protection
- `Path=/api/auth/refresh`: Only sent to refresh endpoint (security)
- `Max-Age=604800`: 7 days (604800 seconds)

### Environment-Specific Configuration

**Development:**
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=False,  # Allow HTTP in development
    samesite="lax",
    max_age=900,
    path="/"
)
```

**Production:**
```python
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    secure=True,  # Require HTTPS
    samesite="lax",
    max_age=900,
    path="/",
    domain=".yourdomain.com"  # Allow subdomains
)
```

---

## API Request/Response Models

### Login Request
**Endpoint:** `POST /api/users/login`

**Request Body:**
```json
{
  "user_name": "johndoe",
  "email": "john@example.com",  // Optional, either email or username
  "password": "securepassword123"
}
```

**Response Body:**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "john@example.com",
    "user_name": "johndoe",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

**Response Headers:**
```http
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Max-Age=900; Path=/
Set-Cookie: refresh_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Max-Age=604800; Path=/api/auth/refresh
```

**Note:** Token is NOT in response body, only in cookies.

### Register Request
**Endpoint:** `POST /api/users/register`

**Request Body:**
```json
{
  "user_name": "johndoe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as login (automatically logs in after registration)

### Refresh Token Request
**Endpoint:** `POST /api/auth/refresh`

**Request Headers:**
```http
Cookie: refresh_token=<jwt>
```

**Response Body:**
```json
{
  "refreshed": true
}
```

**Response Headers:**
```http
Set-Cookie: access_token=<new_jwt>; HttpOnly; Secure; SameSite=Lax; Max-Age=900; Path=/
```

**Note:** Only access token is refreshed, refresh token remains the same.

### Logout Request
**Endpoint:** `POST /api/auth/logout`

**Request Headers:**
```http
Cookie: access_token=<jwt>; refresh_token=<jwt>
```

**Response Body:**
```json
{
  "logged_out": true
}
```

**Response Headers:**
```http
Set-Cookie: access_token=; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Path=/
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Lax; Max-Age=0; Path=/api/auth/refresh
```

**Note:** Cookies cleared by setting Max-Age=0.

---

## Authentication Flow Data

### Login Flow

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Backend │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  POST /api/users/login                      │
     │  {user_name, password}                      │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                                              │ Validate credentials
     │                                              │ Hash password check
     │                                              │
     │                                              │ Generate access_token (15 min)
     │                                              │ Generate refresh_token (7 days)
     │                                              │
     │  200 OK                                      │
     │  Set-Cookie: access_token=<jwt>             │
     │  Set-Cookie: refresh_token=<jwt>            │
     │  {user: {...}}                              │
     │<─────────────────────────────────────────────┤
     │                                              │
     │  Browser stores cookies automatically       │
     │                                              │
```

### Protected Request Flow

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Backend │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  GET /api/tasks                             │
     │  Cookie: access_token=<jwt>                 │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                                              │ Extract JWT from cookie
     │                                              │ Verify signature
     │                                              │ Check expiration
     │                                              │ Extract user_id from 'sub'
     │                                              │
     │                                              │ Fetch user's tasks
     │                                              │
     │  200 OK                                      │
     │  {tasks: [...]}                             │
     │<─────────────────────────────────────────────┤
     │                                              │
```

### Token Refresh Flow

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Backend │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  (14 minutes after login)                   │
     │  POST /api/auth/refresh                     │
     │  Cookie: refresh_token=<jwt>                │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                                              │ Extract refresh_token
     │                                              │ Verify signature
     │                                              │ Check expiration
     │                                              │ Extract user_id
     │                                              │
     │                                              │ Generate new access_token
     │                                              │
     │  200 OK                                      │
     │  Set-Cookie: access_token=<new_jwt>         │
     │  {refreshed: true}                          │
     │<─────────────────────────────────────────────┤
     │                                              │
     │  Browser updates access_token cookie        │
     │                                              │
```

### Logout Flow

```
┌─────────┐                                    ┌─────────┐
│ Client  │                                    │ Backend │
└────┬────┘                                    └────┬────┘
     │                                              │
     │  POST /api/auth/logout                      │
     │  Cookie: access_token=<jwt>                 │
     │  Cookie: refresh_token=<jwt>                │
     ├─────────────────────────────────────────────>│
     │                                              │
     │                                              │ (Optional: Validate tokens)
     │                                              │
     │  200 OK                                      │
     │  Set-Cookie: access_token=; Max-Age=0       │
     │  Set-Cookie: refresh_token=; Max-Age=0      │
     │  {logged_out: true}                         │
     │<─────────────────────────────────────────────┤
     │                                              │
     │  Browser deletes cookies                    │
     │                                              │
```

---

## Frontend State Management

### Better Auth Session State

**State Structure:**
```typescript
interface Session {
  user: {
    id: string;
    email: string;
    name: string;
    user_name: string;
  } | null;
  isLoading: boolean;
  error: Error | null;
}
```

**State Management:**
- Better Auth client manages session state automatically
- Session derived from cookie validation
- No manual state updates needed
- Reactive updates across components

### Auth Context State

**Context Structure:**
```typescript
interface AuthContextType {
  session: Session | null;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
}
```

**State Flow:**
1. AuthProvider wraps app
2. Better Auth client validates cookies on mount
3. Session state updated automatically
4. Components consume via `useAuth()` hook

---

## Migration Data Mapping

### localStorage → Cookies Mapping

| Old (localStorage) | New (Cookie) | Notes |
|-------------------|--------------|-------|
| `auth-token` | `access_token` | JWT moved to HTTP-only cookie |
| `userId` | Extracted from JWT `sub` claim | No separate storage needed |
| N/A | `refresh_token` | New: long-lived refresh token |

### Backward Compatibility (Temporary)

During migration, backend supports both:

**Priority Order:**
1. Check for `access_token` cookie (new system)
2. Fall back to `Authorization: Bearer` header (old system)
3. Return 401 if neither present

**Code:**
```python
async def get_current_user(
    access_token: str = Cookie(None),
    authorization: str = Header(None)
) -> User:
    token = access_token or (
        authorization.split(" ")[1] if authorization else None
    )
    if not token:
        raise HTTPException(status_code=401)
    # Validate token...
```

---

## Security Considerations

### Token Security

**Access Token:**
- Short-lived (15 minutes) limits exposure window
- HTTP-only prevents XSS theft
- Secure flag prevents MITM (production)
- SameSite prevents CSRF

**Refresh Token:**
- Longer-lived (7 days) for UX
- Restricted path (`/api/auth/refresh`) limits exposure
- HTTP-only prevents XSS theft
- Can be revoked (future: sessions table)

### Password Security

**Hashing:**
- Algorithm: bcrypt
- Salt: Auto-generated per password
- Rounds: 12 (default bcrypt)
- Never stored in plain text
- Never transmitted in responses

**Validation:**
```python
# Hash password on registration
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Verify password on login
is_valid = bcrypt.checkpw(
    password.encode('utf-8'),
    stored_hash.encode('utf-8')
)
```

---

## Data Validation

### Input Validation

**Login Request:**
```python
class LoginRequest(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6, max_length=100)
```

**Register Request:**
```python
class RegisterRequest(BaseModel):
    user_name: str = Field(..., min_length=3, max_length=100)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    password: str = Field(..., min_length=6, max_length=100)
```

### Token Validation

**JWT Validation:**
- Signature verification (HS256)
- Expiration check (`exp` claim)
- Token type check (`type` claim)
- User existence check (optional)

---

## Performance Considerations

### Cookie Size

**Access Token:** ~200-300 bytes
**Refresh Token:** ~150-200 bytes
**Total:** ~400-500 bytes per request

**Impact:** Minimal overhead (<1KB per request)

### Database Queries

**Current (per request):**
1. Extract user_id from JWT
2. Optional: Validate user exists (cached)

**No additional queries** compared to current system.

### Caching Strategy

**User Data Caching:**
- Cache user info in memory (Redis future)
- TTL: 5 minutes
- Invalidate on user update

---

## Monitoring & Metrics

### Metrics to Track

**Authentication Metrics:**
- Login success rate
- Login failure rate (by reason)
- Token refresh success rate
- Token refresh failure rate
- Average session duration

**Security Metrics:**
- Failed login attempts per user
- Token validation failures
- Expired token usage attempts
- CORS errors

**Performance Metrics:**
- Authentication latency (p50, p95, p99)
- Token refresh latency
- Cookie size overhead

---

## Conclusion

The data model for Better Auth migration maintains the existing database schema while transitioning from localStorage to HTTP-only cookies. The JWT structure remains compatible, with the addition of refresh tokens for improved UX. No database migrations are required, making this a low-risk, high-security-benefit change.
