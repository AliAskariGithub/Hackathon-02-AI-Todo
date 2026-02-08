---
name: auth-skill
description: Implement secure authentication systems including SignUp, Login, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Registration (SignUp)**
   - Validate user input (email, password)
   - Hash passwords before storing
   - Prevent duplicate accounts
   - Return success or error responses

2. **User Login (Login)**
   - Verify credentials securely
   - Compare hashed passwords
   - Handle invalid login attempts
   - Issue authentication tokens on success

3. **Password Security**
   - Use strong hashing algorithms (bcrypt, argon2)
   - Apply proper salt rounds
   - Never store plain-text passwords
   - Support password reset flows

4. **JWT Token Management**
   - Generate access tokens
   - Set expiration times
   - Verify and decode tokens
   - Protect private routes with middleware

5. **Better Auth Integration**
   - Configure Better Auth providers
   - Connect with backend authentication flow
   - Manage sessions and tokens
   - Handle OAuth and credentials-based auth

## Best Practices
- Enforce strong password rules
- Use HTTPS only
- Store secrets in environment variables
- Implement refresh tokens
- Rate-limit auth endpoints
- Follow OWASP authentication guidelines

## Example Structure
```ts
// SignUp
POST /auth/register
{
  email: string,
  password: string
}

// SignIn
POST /auth/login
{
  email: string,
  password: string
}

// JWT Middleware
function authenticate(req, res, next) {
  const token = req.headers.authorization;
  verifyJWT(token);
  next();
}