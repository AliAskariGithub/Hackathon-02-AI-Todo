# Implementation Plan: Better Auth Migration with HTTP-Only Cookies

**Feature ID:** 009-better-auth-migration
**Plan Date:** 2026-02-09
**Status:** Draft

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Better Auth Client (v1.4.18)                          │ │
│  │  - Cookie-based session management                     │ │
│  │  - Automatic cookie handling                           │ │
│  │  - CSRF protection                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Auth Provider (Updated)                               │ │
│  │  - Remove localStorage usage                           │ │
│  │  - Use Better Auth hooks                              │ │
│  │  - Handle session state                               │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP (credentials: 'include')
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Cookie Middleware                                     │ │
│  │  - Extract JWT from cookies                           │ │
│  │  - Validate token signature                           │ │
│  │  - Set user context                                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Auth Endpoints (Updated)                              │ │
│  │  - /api/users/login → Set HTTP-only cookie            │ │
│  │  - /api/users/register → Set HTTP-only cookie         │ │
│  │  - /api/auth/refresh → Refresh access token           │ │
│  │  - /api/auth/logout → Clear cookies                   │ │
│  └────────────────────────────────────────────────────────┘ │
│                            ↓                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  JWT Service (Updated)                                 │ │
│  │  - Create access tokens (15 min)                      │ │
│  │  - Create refresh tokens (7 days)                     │ │
│  │  - Validate tokens                                    │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  PostgreSQL Database (Neon)                  │
│  - User table (existing)                                     │
│  - No sessions table (stateless JWT)                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### Decision 1: Hybrid Approach
**Decision:** Use Better Auth client-side with custom FastAPI JWT backend

**Rationale:**
- Better Auth has no official Python backend package
- Maintains existing FastAPI infrastructure
- Leverages Better Auth's cookie management
- No need to rewrite entire backend

**Alternatives Considered:**
- Full Better Auth with Node.js backend (rejected: requires complete rewrite)
- Pure FastAPI without Better Auth (rejected: loses client-side benefits)

### Decision 2: JWT in Cookies
**Decision:** Continue using JWT format, store in HTTP-only cookies instead of localStorage

**Rationale:**
- Maintains API compatibility
- Leverages existing JWT infrastructure
- Provides XSS protection via HTTP-only flag
- No database schema changes required

**Alternatives Considered:**
- Server-side sessions with database (rejected: adds complexity and database load)
- Better Auth native sessions (rejected: requires Python backend)

### Decision 3: Dual-Token System
**Decision:** Implement access tokens (15 min) + refresh tokens (7 days)

**Rationale:**
- Short-lived access tokens limit damage if stolen
- Long-lived refresh tokens improve UX
- Industry standard pattern
- Better security posture

**Alternatives Considered:**
- Single long-lived token (rejected: security risk)
- Very short tokens with frequent refresh (rejected: poor UX)

### Decision 4: Gradual Migration
**Decision:** Support both localStorage and cookies during transition period

**Rationale:**
- Zero downtime deployment
- No forced user re-login
- Lower risk of issues
- Easy rollback if needed

**Alternatives Considered:**
- Big bang migration (rejected: high risk, forces re-login)
- Permanent dual support (rejected: maintenance burden)

### Decision 5: SameSite=Lax
**Decision:** Use SameSite=Lax for CSRF protection

**Rationale:**
- Prevents CSRF attacks on state-changing operations
- Compatible with OAuth flows (future)
- Balances security and usability

**Alternatives Considered:**
- SameSite=Strict (rejected: breaks OAuth, too restrictive)
- SameSite=None (rejected: requires additional CSRF tokens)

---

## Implementation Phases

### Phase 1: Backend Cookie Infrastructure (Days 1-2)

#### 1.1 Update JWT Service
**File:** `backend/src/utils/jwt.py`

**Changes:**
- Add `create_refresh_token()` function
- Update token expiration times (access: 15 min, refresh: 7 days)
- Add token type validation

**New Functions:**
```python
def create_access_token(user_id: str) -> str:
    """Create short-lived access token (15 minutes)"""

def create_refresh_token(user_id: str) -> str:
    """Create long-lived refresh token (7 days)"""

def decode_refresh_token(token: str) -> dict:
    """Decode and validate refresh token"""
```

#### 1.2 Update Authentication Dependency
**File:** `backend/src/api/deps.py`

**Changes:**
- Add cookie-based token extraction
- Support both Cookie and Authorization header (dual mode)
- Prioritize cookie over header

**Updated Function:**
```python
async def get_current_user(
    access_token: str = Cookie(None, alias="access_token"),
    authorization: str = Header(None)
) -> User:
    """Extract user from cookie or Authorization header"""
```

#### 1.3 Update Login Endpoint
**File:** `backend/src/api/routers/users.py`

**Changes:**
- Set HTTP-only cookies in response
- Return user info (not token in body)
- Set both access and refresh tokens

**Updated Endpoint:**
```python
@router.post("/api/users/login")
async def login(response: Response, credentials: LoginRequest):
    # Validate credentials
    user = await authenticate_user(credentials)

    # Create tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=900,  # 15 minutes
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=604800,  # 7 days
        path="/"
    )

    return {"user": user.dict()}
```

#### 1.4 Add Refresh Endpoint
**File:** `backend/src/api/routers/auth.py` (NEW)

**New Endpoint:**
```python
@router.post("/api/auth/refresh")
async def refresh_token(
    response: Response,
    refresh_token: str = Cookie(None, alias="refresh_token")
):
    """Refresh access token using refresh token"""

    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")

        # Create new access token
        new_access_token = create_access_token(user_id)

        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=900,
            path="/"
        )

        return {"refreshed": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
```

#### 1.5 Add Logout Endpoint
**File:** `backend/src/api/routers/auth.py`

**New Endpoint:**
```python
@router.post("/api/auth/logout")
async def logout(response: Response):
    """Clear authentication cookies"""

    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")

    return {"logged_out": True}
```

#### 1.6 Update CORS Configuration
**File:** `backend/main.py`

**Changes:**
- Add `allow_credentials=True` to CORS middleware
- Ensure frontend origin is in allowed_origins

**Updated Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,  # REQUIRED for cookies
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)
```

---

### Phase 2: Frontend Better Auth Integration (Days 3-4)

#### 2.1 Configure Better Auth Client
**File:** `frontend/lib/auth.ts`

**Changes:**
- Configure Better Auth with cookie support
- Set base URL to backend
- Enable credentials

**New Configuration:**
```typescript
import { betterAuth } from "better-auth/client";

export const authClient = betterAuth({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000",
  credentials: "include",
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7 // 7 days
    }
  }
});

export const useSession = () => {
  // Use Better Auth's useSession hook
  return authClient.useSession();
};
```

#### 2.2 Update Auth Provider
**File:** `frontend/providers/auth-provider.tsx`

**Changes:**
- Remove localStorage usage
- Use Better Auth hooks
- Handle session from cookies

**Updated Provider:**
```typescript
'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { authClient } from '@/lib/auth';

interface AuthContextType {
  session: any;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, isLoading } = authClient.useSession();

  const login = async (credentials: any) => {
    // Better Auth handles cookie storage automatically
    await authClient.signIn.email(credentials);
  };

  const logout = async () => {
    await authClient.signOut();
  };

  return (
    <AuthContext.Provider value={{ session, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

#### 2.3 Update API Client
**File:** `frontend/services/api-client.ts`

**Changes:**
- Add `credentials: 'include'` to all requests
- Remove Authorization header logic
- Let cookies be sent automatically

**Updated Client:**
```typescript
const apiClient = {
  async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const response = await fetch(url, {
      ...options,
      credentials: 'include',  // Send cookies automatically
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        // Try to refresh token
        await this.refreshToken();
        // Retry original request
        return this.request(endpoint, options);
      }
      throw new Error(`HTTP ${response.status}`);
    }

    return response.json();
  },

  async refreshToken() {
    await fetch(`${API_BASE_URL}/api/auth/refresh`, {
      method: 'POST',
      credentials: 'include'
    });
  }
};
```

#### 2.4 Update Login Form
**File:** `frontend/components/Auth/LoginForm.tsx`

**Changes:**
- Remove localStorage.setItem calls
- Use Better Auth login method
- Handle response without token in body

**Updated Form:**
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  setLoading(true);

  try {
    // Call backend login (sets cookies automatically)
    const response = await apiClient.post('/api/users/login', {
      user_name: userName,
      email: isEmail ? identifier : "",
      password,
    });

    // No need to store token - it's in HTTP-only cookie
    login(response.user);  // Just update session state

    toast({
      title: 'Success',
      description: 'Logged in successfully',
    });

    router.push('/dashboard');
  } catch (error) {
    setError('Invalid credentials');
  } finally {
    setLoading(false);
  }
};
```

#### 2.5 Update Signup Form
**File:** `frontend/components/Auth/SignupForm.tsx`

**Changes:**
- Remove localStorage.setItem calls
- Use Better Auth signup method
- Handle response without token in body

**Similar changes to LoginForm**

#### 2.6 Remove Auth Service
**File:** `frontend/services/auth-service.ts`

**Action:** DELETE (no longer needed, Better Auth handles everything)

#### 2.7 Update Navbar
**File:** `frontend/components/Navbar.tsx`

**Changes:**
- Remove localStorage.removeItem calls
- Use Better Auth logout method

**Updated Logout:**
```typescript
const handleLogout = async () => {
  await authClient.signOut();
  router.push('/login');
};
```

---

### Phase 3: Token Refresh Implementation (Day 5)

#### 3.1 Frontend Auto-Refresh
**File:** `frontend/lib/auth-refresh.ts` (NEW)

**Implementation:**
```typescript
export function setupTokenRefresh() {
  // Refresh token every 14 minutes (before 15-min expiration)
  setInterval(async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        credentials: 'include'
      });
      console.log('Token refreshed successfully');
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Redirect to login if refresh fails
      window.location.href = '/login';
    }
  }, 14 * 60 * 1000); // 14 minutes
}
```

#### 3.2 Initialize Refresh in Layout
**File:** `frontend/app/layout.tsx`

**Changes:**
- Call setupTokenRefresh on mount

**Updated Layout:**
```typescript
'use client';

import { useEffect } from 'react';
import { setupTokenRefresh } from '@/lib/auth-refresh';

export default function RootLayout({ children }) {
  useEffect(() => {
    setupTokenRefresh();
  }, []);

  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
```

---

### Phase 4: Middleware & Route Protection (Day 6)

#### 4.1 Create Auth Middleware
**File:** `frontend/middleware.ts`

**Implementation:**
```typescript
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const protectedRoutes = ['/dashboard', '/chat', '/settings'];
const authRoutes = ['/login', '/signup'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for session cookie
  const hasSession = request.cookies.has('access_token');

  // Redirect to login if accessing protected route without session
  if (protectedRoutes.some(route => pathname.startsWith(route)) && !hasSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }

  // Redirect to dashboard if accessing auth routes with session
  if (authRoutes.some(route => pathname.startsWith(route)) && hasSession) {
    const url = request.nextUrl.clone();
    url.pathname = '/dashboard';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
```

---

### Phase 5: Testing & Validation (Day 7)

#### 5.1 Manual Testing Checklist
- [ ] Login with email/password sets cookies
- [ ] Cookies are HTTP-only (check DevTools)
- [ ] Protected routes accessible after login
- [ ] API requests include cookies automatically
- [ ] Token refresh works before expiration
- [ ] Logout clears cookies
- [ ] Cannot access protected routes after logout
- [ ] CORS works with credentials
- [ ] Works in Docker environment
- [ ] Works across browser tabs

#### 5.2 Integration Tests
**File:** `backend/tests/test_auth_cookies.py` (NEW)

**Tests:**
```python
def test_login_sets_cookies():
    """Test that login endpoint sets HTTP-only cookies"""

def test_cookie_authentication():
    """Test that cookies are used for authentication"""

def test_token_refresh():
    """Test that refresh endpoint updates access token"""

def test_logout_clears_cookies():
    """Test that logout clears all cookies"""
```

---

### Phase 6: Cleanup & Documentation (Day 8)

#### 6.1 Remove localStorage Code
- Remove all `localStorage.getItem('auth-token')` calls
- Remove all `localStorage.setItem('auth-token')` calls
- Remove all `localStorage.removeItem('auth-token')` calls
- Remove `frontend/lib/jwt-utils.ts` (no longer needed)

#### 6.2 Update Environment Variables
**File:** `frontend/.env.example`

**Updates:**
```env
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Better Auth Configuration
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
BETTER_AUTH_SECRET=your-secret-key-change-in-production
```

**File:** `backend/.env.example`

**Updates:**
```env
# Authentication
BETTER_AUTH_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION_DELTA_MINUTES=15  # Access token
REFRESH_TOKEN_EXPIRATION_DAYS=7  # Refresh token

# CORS (must include frontend URL)
ALLOWED_ORIGINS=http://localhost:3000
```

#### 6.3 Update Documentation
- Update README with new auth flow
- Document cookie requirements (HTTPS in production)
- Add troubleshooting guide for CORS issues
- Document migration process

---

## Rollback Plan

### If Issues Occur During Deployment

**Step 1:** Revert frontend deployment
- Frontend falls back to localStorage (dual support still active)
- Users continue with existing sessions

**Step 2:** Investigate issue
- Check browser console for errors
- Check backend logs for cookie issues
- Verify CORS configuration

**Step 3:** Fix and redeploy
- Apply fix
- Test in staging
- Redeploy to production

### If Critical Issues After Full Migration

**Step 1:** Restore localStorage support
- Uncomment localStorage code
- Redeploy frontend

**Step 2:** Keep cookie support active
- Both systems work simultaneously
- Investigate root cause

**Step 3:** Plan second migration attempt
- Address issues found
- Test more thoroughly
- Retry migration

---

## Success Criteria

### Technical Criteria
- ✅ Zero localStorage usage for authentication
- ✅ All tokens in HTTP-only cookies
- ✅ Token refresh working automatically
- ✅ All protected routes secured
- ✅ CORS configured correctly
- ✅ Works in Docker/Kubernetes

### Security Criteria
- ✅ XSS cannot steal tokens
- ✅ CSRF protection via SameSite
- ✅ Secure flag enabled in production
- ✅ Short-lived access tokens (15 min)
- ✅ Long-lived refresh tokens (7 days)

### User Experience Criteria
- ✅ No forced re-login during migration
- ✅ Sessions persist across tabs
- ✅ Automatic token refresh (no interruption)
- ✅ Clear error messages
- ✅ Smooth logout experience

---

## Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Backend Cookie Infrastructure | 2 days | None |
| Phase 2: Frontend Better Auth Integration | 2 days | Phase 1 |
| Phase 3: Token Refresh Implementation | 1 day | Phase 2 |
| Phase 4: Middleware & Route Protection | 1 day | Phase 3 |
| Phase 5: Testing & Validation | 1 day | Phase 4 |
| Phase 6: Cleanup & Documentation | 1 day | Phase 5 |
| **Total** | **8 days** | |

---

## Risk Mitigation

### Risk 1: CORS Issues with Cookies
**Mitigation:**
- Test CORS thoroughly in development
- Document CORS configuration clearly
- Provide troubleshooting guide

### Risk 2: Production HTTPS Requirement
**Mitigation:**
- Document HTTPS requirement
- Provide development workarounds (Secure=false in dev)
- Test in production-like environment

### Risk 3: Session Loss During Deployment
**Mitigation:**
- Gradual migration (dual support)
- Deploy during low-traffic period
- Monitor error rates closely

### Risk 4: Browser Compatibility
**Mitigation:**
- Test in major browsers (Chrome, Firefox, Safari, Edge)
- Document browser requirements
- Provide fallback for unsupported browsers

---

## Monitoring & Observability

### Metrics to Track
- Authentication success rate
- Token refresh success rate
- Cookie-based auth vs header-based auth ratio
- 401 error rate
- Session duration

### Logging
- Log all authentication attempts
- Log token refresh attempts
- Log CORS errors
- Log cookie setting/reading errors

### Alerts
- Alert on high 401 error rate
- Alert on token refresh failures
- Alert on CORS errors

---

## Conclusion

This implementation plan provides a comprehensive, phased approach to migrating from localStorage-based JWT authentication to Better Auth with HTTP-only cookies. The gradual migration strategy ensures zero downtime and minimal user disruption while achieving significant security improvements.
