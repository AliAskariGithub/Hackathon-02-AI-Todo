# Tasks: Better Auth Migration with HTTP-Only Cookies

**Feature ID:** 009-better-auth-migration
**Date:** 2026-02-09
**Status:** Ready for Implementation

---

## Task Overview

This document breaks down the Better Auth migration into actionable, testable tasks. Each task includes acceptance criteria and test cases.

**Total Tasks:** 24
**Estimated Duration:** 8 days

---

## Phase 1: Backend Cookie Infrastructure (Tasks 1-8)

### T001: Update JWT Service for Dual-Token System
**Priority:** High
**Dependencies:** None
**Estimated Time:** 2 hours

**Description:**
Update `backend/src/utils/jwt.py` to support both access tokens (15 min) and refresh tokens (7 days).

**Changes:**
- Add `create_refresh_token()` function
- Update `create_access_token()` with shorter expiration
- Add `decode_refresh_token()` function
- Add token type validation

**Acceptance Criteria:**
- [ ] Access tokens expire in 15 minutes
- [ ] Refresh tokens expire in 7 days
- [ ] Both tokens include `type` claim
- [ ] Token validation checks token type
- [ ] Existing JWT functionality preserved

**Test Cases:**
```python
def test_create_access_token():
    token = create_access_token("user-id-123")
    payload = decode_jwt_token(token)
    assert payload["type"] == "access"
    assert payload["sub"] == "user-id-123"
    # Verify 15-minute expiration

def test_create_refresh_token():
    token = create_refresh_token("user-id-123")
    payload = decode_refresh_token(token)
    assert payload["type"] == "refresh"
    assert payload["sub"] == "user-id-123"
    # Verify 7-day expiration

def test_token_type_validation():
    access_token = create_access_token("user-id")
    # Should fail when decoded as refresh token
    with pytest.raises(JWTError):
        decode_refresh_token(access_token)
```

---

### T002: Update Authentication Dependency for Cookie Support
**Priority:** High
**Dependencies:** T001
**Estimated Time:** 2 hours

**Description:**
Update `backend/src/api/deps.py` to extract JWT from cookies with fallback to Authorization header.

**Changes:**
- Add `Cookie` parameter to `get_current_user()`
- Prioritize cookie over Authorization header
- Support both during migration period
- Add logging for auth method used

**Acceptance Criteria:**
- [ ] Extracts token from `access_token` cookie first
- [ ] Falls back to `Authorization: Bearer` header
- [ ] Returns 401 if neither present
- [ ] Logs which auth method was used
- [ ] Existing Bearer token auth still works

**Test Cases:**
```python
def test_cookie_authentication():
    # Test with cookie
    response = client.get("/api/tasks", cookies={"access_token": valid_token})
    assert response.status_code == 200

def test_header_authentication_fallback():
    # Test with Authorization header (backward compatibility)
    response = client.get("/api/tasks", headers={"Authorization": f"Bearer {valid_token}"})
    assert response.status_code == 200

def test_cookie_priority_over_header():
    # Cookie should be used when both present
    response = client.get(
        "/api/tasks",
        cookies={"access_token": valid_cookie_token},
        headers={"Authorization": f"Bearer {invalid_header_token}"}
    )
    assert response.status_code == 200  # Cookie token is valid

def test_no_auth_returns_401():
    response = client.get("/api/tasks")
    assert response.status_code == 401
```

---

### T003: Update Login Endpoint to Set Cookies
**Priority:** High
**Dependencies:** T001, T002
**Estimated Time:** 2 hours

**Description:**
Update `backend/src/api/routers/users.py` login endpoint to set HTTP-only cookies.

**Changes:**
- Add `Response` parameter to login function
- Generate both access and refresh tokens
- Set cookies with proper security flags
- Return user info (not token in body)
- Keep backward compatibility (also return token in body temporarily)

**Acceptance Criteria:**
- [ ] Sets `access_token` cookie with 15-minute expiration
- [ ] Sets `refresh_token` cookie with 7-day expiration
- [ ] Cookies have HttpOnly, Secure, SameSite=Lax flags
- [ ] Returns user object in response body
- [ ] Temporarily also returns token in body for backward compatibility

**Test Cases:**
```python
def test_login_sets_cookies():
    response = client.post("/api/users/login", json={
        "user_name": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

def test_cookie_attributes():
    response = client.post("/api/users/login", json={
        "user_name": "testuser",
        "password": "password123"
    })
    access_cookie = response.cookies["access_token"]
    assert access_cookie.httponly == True
    assert access_cookie.samesite == "lax"
    assert access_cookie.max_age == 900  # 15 minutes

def test_login_returns_user_info():
    response = client.post("/api/users/login", json={
        "user_name": "testuser",
        "password": "password123"
    })
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
```

---

### T004: Update Register Endpoint to Set Cookies
**Priority:** High
**Dependencies:** T003
**Estimated Time:** 1 hour

**Description:**
Update `backend/src/api/routers/users.py` register endpoint to set cookies after registration.

**Changes:**
- Add `Response` parameter to register function
- Set cookies after successful registration
- Auto-login user after registration

**Acceptance Criteria:**
- [ ] Sets cookies after successful registration
- [ ] User automatically logged in
- [ ] Same cookie configuration as login
- [ ] Returns user object

**Test Cases:**
```python
def test_register_sets_cookies():
    response = client.post("/api/users/register", json={
        "user_name": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies

def test_register_auto_login():
    response = client.post("/api/users/register", json={
        "user_name": "newuser",
        "email": "new@example.com",
        "password": "password123"
    })
    # Should be able to access protected route immediately
    tasks_response = client.get("/api/tasks", cookies=response.cookies)
    assert tasks_response.status_code == 200
```

---

### T005: Create Refresh Token Endpoint
**Priority:** High
**Dependencies:** T001, T002
**Estimated Time:** 2 hours

**Description:**
Create new `backend/src/api/routers/auth.py` file with refresh endpoint.

**Changes:**
- Create new auth router
- Implement `/api/auth/refresh` endpoint
- Extract refresh token from cookie
- Generate new access token
- Set new access token cookie

**Acceptance Criteria:**
- [ ] Endpoint accepts refresh token from cookie
- [ ] Validates refresh token signature and expiration
- [ ] Generates new access token
- [ ] Sets new access token cookie
- [ ] Returns success response
- [ ] Returns 401 for invalid/expired refresh token

**Test Cases:**
```python
def test_refresh_token_success():
    # Login to get tokens
    login_response = client.post("/api/users/login", json={
        "user_name": "testuser",
        "password": "password123"
    })

    # Wait 1 second
    time.sleep(1)

    # Refresh token
    refresh_response = client.post("/api/auth/refresh", cookies=login_response.cookies)
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.cookies

    # New token should be different
    assert refresh_response.cookies["access_token"] != login_response.cookies["access_token"]

def test_refresh_without_token():
    response = client.post("/api/auth/refresh")
    assert response.status_code == 401

def test_refresh_with_invalid_token():
    response = client.post("/api/auth/refresh", cookies={"refresh_token": "invalid"})
    assert response.status_code == 401

def test_refresh_with_expired_token():
    expired_token = create_expired_refresh_token()
    response = client.post("/api/auth/refresh", cookies={"refresh_token": expired_token})
    assert response.status_code == 401
```

---

### T006: Create Logout Endpoint
**Priority:** Medium
**Dependencies:** T002
**Estimated Time:** 1 hour

**Description:**
Add logout endpoint to `backend/src/api/routers/auth.py` to clear cookies.

**Changes:**
- Implement `/api/auth/logout` endpoint
- Clear both access and refresh token cookies
- Return success response

**Acceptance Criteria:**
- [ ] Clears `access_token` cookie
- [ ] Clears `refresh_token` cookie
- [ ] Returns success response
- [ ] Works even without valid tokens

**Test Cases:**
```python
def test_logout_clears_cookies():
    # Login first
    login_response = client.post("/api/users/login", json={
        "user_name": "testuser",
        "password": "password123"
    })

    # Logout
    logout_response = client.post("/api/auth/logout", cookies=login_response.cookies)
    assert logout_response.status_code == 200

    # Cookies should be cleared (Max-Age=0)
    assert logout_response.cookies["access_token"].max_age == 0
    assert logout_response.cookies["refresh_token"].max_age == 0

def test_logout_without_cookies():
    # Should still succeed
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
```

---

### T007: Update CORS Configuration
**Priority:** High
**Dependencies:** None
**Estimated Time:** 30 minutes

**Description:**
Update `backend/main.py` CORS middleware to support credentials.

**Changes:**
- Add `allow_credentials=True` to CORS middleware
- Ensure frontend origin in allowed_origins
- Add `expose_headers` configuration

**Acceptance Criteria:**
- [ ] `allow_credentials=True` set
- [ ] Frontend URL in allowed_origins
- [ ] CORS headers present in responses
- [ ] Preflight requests handled correctly

**Test Cases:**
```python
def test_cors_allows_credentials():
    response = client.options("/api/users/login", headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST"
    })
    assert "Access-Control-Allow-Credentials" in response.headers
    assert response.headers["Access-Control-Allow-Credentials"] == "true"

def test_cors_allows_frontend_origin():
    response = client.get("/api/health", headers={
        "Origin": "http://localhost:3000"
    })
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"
```

---

### T008: Register Auth Router in Main App
**Priority:** High
**Dependencies:** T005, T006
**Estimated Time:** 15 minutes

**Description:**
Register the new auth router in `backend/main.py`.

**Changes:**
- Import auth router
- Include auth router in app

**Acceptance Criteria:**
- [ ] Auth router imported
- [ ] Auth router included with correct prefix
- [ ] Endpoints accessible at `/api/auth/*`

**Test Cases:**
```python
def test_refresh_endpoint_accessible():
    response = client.post("/api/auth/refresh")
    assert response.status_code in [200, 401]  # Not 404

def test_logout_endpoint_accessible():
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
```

---

## Phase 2: Frontend Better Auth Integration (Tasks 9-16)

### T009: Configure Better Auth Client
**Priority:** High
**Dependencies:** T001-T008 (backend ready)
**Estimated Time:** 1 hour

**Description:**
Configure Better Auth client in `frontend/lib/auth.ts` with cookie support.

**Changes:**
- Import Better Auth client
- Configure with backend URL
- Enable credentials
- Configure cookie cache

**Acceptance Criteria:**
- [ ] Better Auth client configured
- [ ] Base URL points to backend
- [ ] Credentials set to "include"
- [ ] Cookie cache enabled
- [ ] Exports `authClient` and `useSession`

**Test Cases:**
- Manual: Check browser DevTools → Application → Cookies
- Manual: Verify cookies sent with requests (Network tab)

---

### T010: Update Auth Provider
**Priority:** High
**Dependencies:** T009
**Estimated Time:** 2 hours

**Description:**
Update `frontend/providers/auth-provider.tsx` to use Better Auth hooks.

**Changes:**
- Remove localStorage usage
- Use Better Auth `useSession` hook
- Update login/logout functions
- Remove manual JWT decoding

**Acceptance Criteria:**
- [ ] No localStorage.getItem calls
- [ ] No localStorage.setItem calls
- [ ] Uses Better Auth hooks
- [ ] Session state managed by Better Auth
- [ ] Login/logout work correctly

**Test Cases:**
```typescript
// Manual testing
test('login sets cookies not localStorage', async () => {
  await login({username: 'test', password: 'test'});
  expect(localStorage.getItem('auth-token')).toBeNull();
  // Check cookies in DevTools
});

test('session persists across page refresh', async () => {
  await login({username: 'test', password: 'test'});
  window.location.reload();
  // Session should still be active
  expect(session).toBeTruthy();
});
```

---

### T011: Update API Client for Credentials
**Priority:** High
**Dependencies:** T009
**Estimated Time:** 1 hour

**Description:**
Update `frontend/services/api-client.ts` to include credentials with all requests.

**Changes:**
- Add `credentials: 'include'` to fetch options
- Remove Authorization header logic
- Add automatic token refresh on 401

**Acceptance Criteria:**
- [ ] All requests include `credentials: 'include'`
- [ ] No manual Authorization header
- [ ] 401 triggers refresh attempt
- [ ] Retry after successful refresh

**Test Cases:**
```typescript
test('requests include credentials', () => {
  const spy = jest.spyOn(global, 'fetch');
  apiClient.get('/api/tasks');
  expect(spy).toHaveBeenCalledWith(
    expect.any(String),
    expect.objectContaining({credentials: 'include'})
  );
});
```

---

### T012: Update Login Form
**Priority:** High
**Dependencies:** T010, T011
**Estimated Time:** 1 hour

**Description:**
Update `frontend/components/Auth/LoginForm.tsx` to remove localStorage usage.

**Changes:**
- Remove `localStorage.setItem('auth-token')` calls
- Remove `localStorage.setItem('userId')` calls
- Use auth provider's login function
- Handle response without token in body

**Acceptance Criteria:**
- [ ] No localStorage usage
- [ ] Uses auth provider login
- [ ] Handles cookie-based response
- [ ] Redirects to dashboard on success
- [ ] Shows error messages

**Test Cases:**
- Manual: Login and verify no localStorage entries
- Manual: Verify cookies set in DevTools
- Manual: Verify redirect to dashboard

---

### T013: Update Signup Form
**Priority:** High
**Dependencies:** T010, T011
**Estimated Time:** 1 hour

**Description:**
Update `frontend/components/Auth/SignupForm.tsx` to remove localStorage usage.

**Changes:**
- Remove localStorage calls
- Use auth provider
- Handle cookie-based response

**Acceptance Criteria:**
- [ ] No localStorage usage
- [ ] Uses auth provider
- [ ] Auto-login after registration
- [ ] Redirects to dashboard

**Test Cases:**
- Manual: Register and verify no localStorage
- Manual: Verify auto-login works
- Manual: Verify cookies set

---

### T014: Update Navbar Logout
**Priority:** Medium
**Dependencies:** T010
**Estimated Time:** 30 minutes

**Description:**
Update `frontend/components/Navbar.tsx` to use Better Auth logout.

**Changes:**
- Remove localStorage.removeItem calls
- Use auth provider logout
- Call `/api/auth/logout` endpoint

**Acceptance Criteria:**
- [ ] No localStorage removal
- [ ] Uses auth provider logout
- [ ] Clears cookies
- [ ] Redirects to login

**Test Cases:**
- Manual: Logout and verify cookies cleared
- Manual: Verify cannot access protected routes

---

### T015: Update Chat Page
**Priority:** Medium
**Dependencies:** T010, T011
**Estimated Time:** 1 hour

**Description:**
Update `frontend/app/chat/ChatPageContent.tsx` to remove localStorage usage.

**Changes:**
- Remove `localStorage.getItem('auth-token')` calls
- Remove `localStorage.getItem('userId')` calls
- Get user info from session context

**Acceptance Criteria:**
- [ ] No localStorage usage
- [ ] Uses session context for user info
- [ ] Chat functionality works
- [ ] Messages load correctly

**Test Cases:**
- Manual: Open chat and verify it works
- Manual: Send message and verify it works
- Manual: Check no localStorage access in console

---

### T016: Delete Auth Service File
**Priority:** Low
**Dependencies:** T010-T015
**Estimated Time:** 15 minutes

**Description:**
Delete `frontend/services/auth-service.ts` as it's no longer needed.

**Changes:**
- Delete file
- Remove any imports

**Acceptance Criteria:**
- [ ] File deleted
- [ ] No import errors
- [ ] App builds successfully

**Test Cases:**
```bash
npm run build
# Should succeed with no errors
```

---

## Phase 3: Token Refresh Implementation (Tasks 17-18)

### T017: Implement Frontend Auto-Refresh
**Priority:** High
**Dependencies:** T005 (refresh endpoint)
**Estimated Time:** 2 hours

**Description:**
Create `frontend/lib/auth-refresh.ts` with automatic token refresh logic.

**Changes:**
- Create refresh setup function
- Set interval for 14-minute refresh
- Handle refresh failures
- Redirect to login on failure

**Acceptance Criteria:**
- [ ] Refreshes every 14 minutes
- [ ] Calls `/api/auth/refresh` endpoint
- [ ] Handles success silently
- [ ] Redirects to login on failure
- [ ] Logs refresh attempts

**Test Cases:**
- Manual: Wait 14 minutes and verify refresh
- Manual: Check Network tab for refresh requests
- Manual: Verify no interruption to user

---

### T018: Initialize Refresh in App Layout
**Priority:** High
**Dependencies:** T017
**Estimated Time:** 30 minutes

**Description:**
Update `frontend/app/layout.tsx` to initialize token refresh.

**Changes:**
- Import setupTokenRefresh
- Call on mount
- Cleanup on unmount

**Acceptance Criteria:**
- [ ] Refresh initialized on app load
- [ ] Only initialized once
- [ ] Cleanup on unmount

**Test Cases:**
- Manual: Verify refresh starts after login
- Manual: Verify no duplicate intervals

---

## Phase 4: Middleware & Route Protection (Tasks 19-20)

### T019: Create Auth Middleware
**Priority:** High
**Dependencies:** T009-T016
**Estimated Time:** 2 hours

**Description:**
Create `frontend/middleware.ts` for route protection.

**Changes:**
- Create middleware file
- Check for access_token cookie
- Redirect to login if missing
- Redirect to dashboard if logged in on auth pages

**Acceptance Criteria:**
- [ ] Protected routes require cookie
- [ ] Redirects to login if no cookie
- [ ] Auth pages redirect to dashboard if logged in
- [ ] Public routes accessible

**Test Cases:**
- Manual: Access /dashboard without login → redirect to /login
- Manual: Access /login while logged in → redirect to /dashboard
- Manual: Access / without login → no redirect

---

### T020: Test Route Protection
**Priority:** High
**Dependencies:** T019
**Estimated Time:** 1 hour

**Description:**
Manually test all route protection scenarios.

**Test Cases:**
- [ ] Cannot access /dashboard without login
- [ ] Cannot access /chat without login
- [ ] Cannot access /settings without login
- [ ] Can access / without login
- [ ] Can access /login without login
- [ ] Can access /signup without login
- [ ] Redirected to /dashboard after login
- [ ] Redirected to /login after logout

---

## Phase 5: Testing & Validation (Tasks 21-22)

### T021: Backend Integration Tests
**Priority:** High
**Dependencies:** T001-T008
**Estimated Time:** 3 hours

**Description:**
Create comprehensive backend integration tests.

**Test File:** `backend/tests/test_auth_cookies.py`

**Test Cases:**
- [ ] Login sets cookies correctly
- [ ] Register sets cookies correctly
- [ ] Cookie authentication works
- [ ] Header authentication works (backward compat)
- [ ] Cookie priority over header
- [ ] Refresh token works
- [ ] Logout clears cookies
- [ ] Invalid tokens rejected
- [ ] Expired tokens rejected
- [ ] CORS works with credentials

---

### T022: Frontend E2E Tests
**Priority:** Medium
**Dependencies:** T009-T020
**Estimated Time:** 2 hours

**Description:**
Create end-to-end tests for authentication flow.

**Test Cases:**
- [ ] Complete login flow
- [ ] Complete signup flow
- [ ] Session persistence across tabs
- [ ] Token refresh works
- [ ] Logout works
- [ ] Protected route access
- [ ] Cookies set correctly
- [ ] No localStorage usage

---

## Phase 6: Cleanup & Documentation (Tasks 23-24)

### T023: Remove localStorage Code
**Priority:** Medium
**Dependencies:** T021, T022 (tests pass)
**Estimated Time:** 2 hours

**Description:**
Search and remove all remaining localStorage authentication code.

**Files to Check:**
- All files in `frontend/app/`
- All files in `frontend/components/`
- All files in `frontend/lib/`
- `frontend/lib/jwt-utils.ts` (delete)

**Acceptance Criteria:**
- [ ] No `localStorage.getItem('auth-token')` calls
- [ ] No `localStorage.setItem('auth-token')` calls
- [ ] No `localStorage.getItem('userId')` calls
- [ ] No `localStorage.setItem('userId')` calls
- [ ] jwt-utils.ts deleted
- [ ] App builds successfully
- [ ] All tests pass

**Verification:**
```bash
# Search for localStorage usage
grep -r "localStorage.getItem('auth-token')" frontend/
grep -r "localStorage.setItem('auth-token')" frontend/
grep -r "localStorage.getItem('userId')" frontend/
grep -r "localStorage.setItem('userId')" frontend/

# Should return no results
```

---

### T024: Update Documentation
**Priority:** Low
**Dependencies:** T023
**Estimated Time:** 2 hours

**Description:**
Update project documentation for new authentication system.

**Files to Update:**
- `README.md` - Update auth section
- `frontend/.env.example` - Add Better Auth config
- `backend/.env.example` - Update auth config
- `DOCKER_GUIDE.md` - Update for cookies
- Create `AUTH_MIGRATION_GUIDE.md`

**Acceptance Criteria:**
- [ ] README updated with cookie-based auth
- [ ] Environment examples updated
- [ ] Docker guide mentions HTTPS requirement
- [ ] Migration guide created
- [ ] Troubleshooting section added

---

## Task Dependencies Graph

```
Phase 1 (Backend):
T001 → T002 → T003 → T004
  ↓      ↓      ↓
T005 → T006 → T008
  ↓
T007 (parallel)

Phase 2 (Frontend):
T009 → T010 → T011 → T012
         ↓      ↓      ↓
       T013   T014   T015 → T016

Phase 3 (Refresh):
T017 → T018

Phase 4 (Middleware):
T019 → T020

Phase 5 (Testing):
T021 (backend tests)
T022 (frontend tests)

Phase 6 (Cleanup):
T023 → T024
```

---

## Success Criteria

### All Tasks Complete When:
- [ ] All 24 tasks marked as complete
- [ ] All acceptance criteria met
- [ ] All test cases pass
- [ ] No localStorage usage for auth
- [ ] All tokens in HTTP-only cookies
- [ ] Token refresh working
- [ ] Route protection working
- [ ] Documentation updated
- [ ] Zero breaking changes to API

---

## Notes

- Tasks can be worked on in parallel within phases
- Backend tasks (T001-T008) should be completed before frontend tasks
- Testing tasks (T021-T022) validate all previous work
- Cleanup (T023-T024) should only happen after tests pass
- Each task should be committed separately for easy rollback

---

## Rollback Tasks

If rollback is needed:

**R001: Revert Frontend Changes**
- Restore localStorage code
- Revert auth provider changes
- Redeploy frontend

**R002: Keep Backend Cookie Support**
- Backend continues supporting both methods
- No backend rollback needed

**R003: Investigate and Fix**
- Identify root cause
- Apply fix
- Retry migration
