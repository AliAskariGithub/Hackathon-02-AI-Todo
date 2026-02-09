# Data Model for Todo Backend & Database

## Task Entity

### Fields
- `id`: UUID (Primary Key, default: generated)
- `title`: String (Required, max length: 255)
- `description`: Text (Optional)
- `completed`: Boolean (Default: False)
- `user_id`: UUID (Foreign Key reference to User, Required for isolation)
- `created_at`: DateTime (Default: current timestamp)
- `updated_at`: DateTime (Default: current timestamp, updated on change)

### Relationships
- Belongs to one User (many-to-one relationship)
- User can have many Tasks

### Validation Rules
- Title must be between 1 and 255 characters
- User_id must reference an existing User record
- completed field can only be True or False

## User Entity (Stub)

### Fields
- `id`: UUID (Primary Key, default: generated)
- `email`: String (Unique, Required)
- `created_at`: DateTime (Default: current timestamp)
- `updated_at`: DateTime (Default: current timestamp, updated on change)

### Relationships
- Has many Tasks (one-to-many relationship)

### Notes
- This is a stub model prepared for Spec 2 (authentication)
- Will be expanded with authentication fields in future spec

## Database Schema

### Indexes
- Index on user_id for efficient user-based queries
- Index on completed for filtering completed tasks
- Composite index on user_id and completed for combined filtering

### Constraints
- Foreign key constraint on user_id referencing users table
- Not null constraints on required fields
- Unique constraint on user email