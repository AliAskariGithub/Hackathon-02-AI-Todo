# Data Model: Auth System & API Security

## User Entity
- **Identifier**: user_id (UUID/string) - Primary identifier extracted from JWT 'sub' claim
- **Attributes**:
  - email (string) - User's email address
  - created_at (timestamp) - Account creation time
  - updated_at (timestamp) - Last update time
- **Relationships**: Owns multiple Todo Lists
- **Validation**: Email must be valid format, user_id must be unique

## JWT Token Entity
- **Identifier**: token_id (internal, not exposed)
- **Attributes**:
  - sub (string) - Subject (user_id) extracted from JWT
  - exp (timestamp) - Expiration time
  - iat (timestamp) - Issued at time
  - jti (string) - JWT ID (optional for tracking)
- **State Transitions**: Valid → Expired (automatic based on exp timestamp)
- **Validation**: Must contain valid 'sub' claim matching user_id in URL

## Todo List Entity
- **Identifier**: list_id (UUID/string)
- **Attributes**:
  - title (string) - List title
  - user_id (string) - Owner reference (matches JWT 'sub')
  - created_at (timestamp)
  - updated_at (timestamp)
- **Relationships**: Belongs to one User, contains multiple Tasks
- **Validation**: user_id must match JWT 'sub' for access

## Access Control Validation
- **Rule**: JWT 'sub' must equal URL parameter user_id
- **Enforcement**: Checked at API gateway/middleware level
- **Response**: 403 Forbidden when rule violated