# Research: Auth System & API Security Implementation

## Decision: Token Verification Strategy
**Rationale**: For a hackathon environment, symmetric HS256 algorithm with a shared secret is simpler to implement and manage than asymmetric RS256 with JWKS endpoint. HS256 requires only one shared secret (BETTER_AUTH_SECRET) that both frontend and backend can use for signing and verification.

**Alternatives considered**:
- RS256 (asymmetric): More complex setup with public/private key pairs, requires JWKS endpoint management
- EdDSA: Newer algorithm with good security properties but less widespread support
- HS512: Similar to HS256 but with longer key length

## Decision: JWT Storage Strategy
**Rationale**: Better Auth typically stores JWTs in cookies by default for better security (HTTP-only cookies prevent XSS attacks). However, for API communication, the Authorization: Bearer header approach is more standard and flexible. We'll use cookies for frontend session management and Authorization headers for API calls.

**Alternatives considered**:
- Local storage: Vulnerable to XSS attacks
- Session storage: Lost on browser refresh
- Memory: Lost on page refresh but secure

## Decision: Python JWT Library Choice
**Rationale**: Both PyJWT and python-jose are mature libraries for JWT handling in Python. PyJWT is more widely adopted and has better documentation. It integrates well with FastAPI and supports all required algorithms including HS256.

**Alternatives considered**:
- python-jose: Good alternative with some additional features, but less commonly used
- cryptography library: Lower-level, requires more code to implement JWT handling

## Decision: FastAPI Security Implementation Approach
**Rationale**: FastAPI's dependency injection system makes it ideal to create a security dependency that can be injected into endpoints. This provides cleaner code than middleware for checking specific route parameters. The dependency can extract the JWT, decode it, and validate that the user ID matches the path parameter.

**Alternatives considered**:
- Middleware: Would apply globally, harder to customize per endpoint
- Manual validation in each endpoint: Repetitive and error-prone
- Custom decorator: Possible but less idiomatic for FastAPI

## Better Auth JWT Plugin Configuration
**Findings**: Better Auth supports JWT generation through its built-in token system. The JWT plugin allows customization of token content including adding user ID to the 'sub' claim. Configuration will involve setting up the auth provider with JWT options and ensuring the shared secret is synchronized.

## FastAPI JWT Verification Process
**Process**:
1. Extract Authorization header from request
2. Decode JWT using shared secret (BETTER_AUTH_SECRET)
3. Validate token hasn't expired
4. Extract 'sub' (user ID) from token
5. Compare with user_id in path parameter
6. Allow or deny request based on match