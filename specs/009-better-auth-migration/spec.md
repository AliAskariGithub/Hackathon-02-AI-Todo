# Feature Specification: Better Auth Migration with HTTP-Only Cookies

**Feature ID:** 009-better-auth-migration
**Status:** Draft
**Created:** 2026-02-09
**Last Updated:** 2026-02-09

---

## Overview

Migrate the application's authentication system from an insecure custom JWT + localStorage implementation to Better Auth with HTTP-only cookies. This migration addresses critical security vulnerabilities (XSS attacks) and provides a more robust, production-ready authentication system.

---

## Problem Statement

### Current Issues

1. **Security Vulnerability:** JWT tokens stored in localStorage are accessible to JavaScript, making the application vulnerable to XSS attacks
2. **No Session Management:** Stateless JWT with no server-side session validation or revocation capability
3. **Poor User Experience:** 30-minute token expiration requires frequent re-login with no refresh token mechanism
4. **Unused Dependencies:** Better Auth v1.4.18 is installed but not configured or used
5. **Inconsistent Implementation:** Mixed authentication patterns across 20+ files

### Impact

- **High Security Risk:** User credentials and sessions can be stolen via XSS
- **Poor UX:** Users must re-login every 30 minutes
- **Maintenance Burden:** Custom JWT implementation requires ongoing security updates
- **Technical Debt:** Unused Better Auth dependency and inconsistent patterns

---

## Goals

### Primary Goals

1. **Eliminate XSS Vulnerability:** Store authentication tokens in HTTP-only cookies that JavaScript cannot access
2. **Implement Better Auth:** Leverage Better Auth for robust session management
3. **Maintain Backward Compatibility:** Existing users continue working without data loss
4. **Improve Security Posture:** Add CSRF protection, secure cookie flags, and session validation

### Secondary Goals

1. **Better User Experience:** Implement refresh tokens for longer sessions
2. **Simplified Codebase:** Remove custom JWT utilities in favor of Better Auth
3. **Production Ready:** Proper cookie configuration for production deployment
4. **Developer Experience:** Clear authentication patterns and better error handling

---

## Requirements

### Functional Requirements

#### FR1: HTTP-Only Cookie Authentication
- **FR1.1:** Store session tokens in HTTP-only cookies (not accessible to JavaScript)
- **FR1.2:** Automatically include cookies in all API requests
- **FR1.3:** Support cookie-based authentication for all protected routes
- **FR1.4:** Remove all localStorage usage for authentication tokens

#### FR2: Better Auth Integration
- **FR2.1:** Configure Better Auth client on frontend with cookie-based sessions
- **FR2.2:** Implement Better Auth-compatible backend endpoints
- **FR2.3:** Support email/password authentication (existing functionality)
- **FR2.4:** Maintain JWT format for API authentication (backward compatible)

#### FR3: Session Management
- **FR3.1:** Implement server-side session validation
- **FR3.2:** Support session refresh without re-login
- **FR3.3:** Provide session revocation capability (logout)
- **FR3.4:** Handle session expiration gracefully with refresh tokens

#### FR4: User Migration
- **FR4.1:** Existing users can log in without password reset
- **FR4.2:** No data loss during migration
- **FR4.3:** Seamless transition from localStorage to cookies
- **FR4.4:** Support gradual rollout (both systems work temporarily)

#### FR5: Protected Routes
- **FR5.1:** All existing protected routes remain protected
- **FR5.2:** Middleware validates cookies before allowing access
- **FR5.3:** Redirect to login for unauthenticated requests
- **FR5.4:** Preserve current authorization logic (user owns resource)

### Non-Functional Requirements

#### NFR1: Security
- **NFR1.1:** HTTP-only cookies prevent JavaScript access
- **NFR1.2:** Secure flag enabled in production (HTTPS only)
- **NFR1.3:** SameSite=Lax to prevent CSRF attacks
- **NFR1.4:** CSRF token validation for state-changing operations
- **NFR1.5:** Bcrypt password hashing maintained (existing)

#### NFR2: Performance
- **NFR2.1:** Cookie-based auth adds <10ms latency per request
- **NFR2.2:** Session validation cached to reduce database queries
- **NFR2.3:** No impact on existing API response times

#### NFR3: Compatibility
- **NFR3.1:** Works with existing PostgreSQL database
- **NFR3.2:** Compatible with Docker deployment
- **NFR3.3:** Works with Kubernetes orchestration
- **NFR3.4:** No breaking changes to API contracts

#### NFR4: Maintainability
- **NFR4.1:** Clear separation between auth and business logic
- **NFR4.2:** Comprehensive error handling and logging
- **NFR4.3:** Well-documented configuration options
- **NFR4.4:** Easy to test authentication flows

---

## User Stories

### US1: Secure Login
**As a** user
**I want** my authentication tokens stored securely
**So that** my account cannot be compromised via XSS attacks

**Acceptance Criteria:**
- Tokens stored in HTTP-only cookies
- JavaScript cannot access authentication tokens
- Login works identically to current experience
- Session persists across browser tabs

### US2: Persistent Sessions
**As a** user
**I want** to stay logged in for longer periods
**So that** I don't have to re-login every 30 minutes

**Acceptance Criteria:**
- Session lasts at least 7 days with activity
- Automatic token refresh without user action
- Graceful handling of expired sessions
- Clear feedback when re-login is required

### US3: Seamless Migration
**As an** existing user
**I want** to continue using the app without disruption
**So that** I don't lose access to my data

**Acceptance Criteria:**
- Existing credentials work without reset
- No data loss during migration
- All existing features continue working
- Transparent migration (user unaware)

### US4: Secure Logout
**As a** user
**I want** to securely log out from all devices
**So that** my session is properly terminated

**Acceptance Criteria:**
- Logout clears all cookies
- Server-side session invalidated
- Cannot access protected routes after logout
- Works across all browser tabs

---

## Out of Scope

1. **OAuth Integration:** Google/GitHub login (Better Auth supports it, but not in this phase)
2. **Two-Factor Authentication:** 2FA/MFA implementation
3. **Password Reset Flow:** Email-based password recovery
4. **Email Verification:** Account verification via email
5. **Role-Based Access Control:** User roles and permissions
6. **Session Management UI:** Admin panel to view/revoke sessions
7. **Audit Logging:** Detailed authentication event logging
8. **Rate Limiting:** Login attempt throttling (separate feature)

---

## Technical Constraints

1. **Better Auth Limitation:** No official Python backend package exists
2. **Database:** Must work with existing PostgreSQL schema
3. **Deployment:** Must support Docker and Kubernetes
4. **Browser Support:** Modern browsers with cookie support
5. **HTTPS Requirement:** Secure cookies require HTTPS in production
6. **CORS Configuration:** Must handle cross-origin cookie transmission

---

## Success Metrics

### Security Metrics
- **Zero XSS vulnerabilities** in authentication flow
- **100% of tokens** stored in HTTP-only cookies
- **Zero localStorage usage** for authentication

### User Experience Metrics
- **Session duration:** Minimum 7 days with activity
- **Login success rate:** ≥99% (same as current)
- **Zero user complaints** about migration

### Technical Metrics
- **Migration completion:** 100% of auth files updated
- **Test coverage:** ≥90% for authentication flows
- **Zero breaking changes** to existing API contracts

---

## Dependencies

### External Dependencies
- Better Auth v1.4.18 (already installed)
- FastAPI with cookie support
- PostgreSQL database
- Docker/Kubernetes infrastructure

### Internal Dependencies
- Existing User model and database schema
- Current API endpoints and routes
- Frontend components and pages
- Backend middleware and dependencies

---

## Risks and Mitigations

### Risk 1: Session Data Loss During Migration
**Impact:** High
**Probability:** Medium
**Mitigation:**
- Support both localStorage and cookies temporarily
- Gradual rollout with feature flag
- Comprehensive testing before deployment

### Risk 2: CORS Issues with Cookies
**Impact:** High
**Probability:** Medium
**Mitigation:**
- Configure CORS to allow credentials
- Test cross-origin scenarios thoroughly
- Document cookie domain configuration

### Risk 3: Breaking Changes to API
**Impact:** High
**Probability:** Low
**Mitigation:**
- Maintain JWT format for backward compatibility
- Version API endpoints if needed
- Comprehensive integration tests

### Risk 4: Production HTTPS Requirement
**Impact:** Medium
**Probability:** Low
**Mitigation:**
- Document HTTPS requirement clearly
- Provide development workarounds
- Test in production-like environment

---

## Open Questions

1. **Session Storage:** Should we add a sessions table or keep stateless JWT?
2. **Token Refresh:** Client-side automatic refresh or server-side rotation?
3. **Migration Timeline:** Gradual rollout or big-bang deployment?
4. **Backward Compatibility:** How long to support localStorage fallback?
5. **Better Auth Backend:** Build custom Python integration or use JWT-compatible approach?

---

## References

- [Better Auth Documentation](https://better-auth.com)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [MDN HTTP Cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies)
- Current implementation: `specs/002-todo-auth-security/`

---

## Approval

**Stakeholders:**
- [ ] Product Owner
- [ ] Security Team
- [ ] Engineering Lead
- [ ] DevOps Team

**Sign-off Date:** _____________
