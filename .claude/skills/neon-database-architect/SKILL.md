---
name: database-skill
description: Design and manage relational database schemas, tables, and migrations following best practices.
---

# Database Skill – Schema Design & Migrations

## Instructions

1. **Schema design**
   - Identify entities and relationships
   - Normalize tables (up to 3NF where applicable)
   - Define clear primary and foreign keys

2. **Table creation**
   - Use meaningful table and column names
   - Choose appropriate data types
   - Apply constraints (NOT NULL, UNIQUE, CHECK)

3. **Migrations**
   - Version-controlled migration files
   - Separate up and down (rollback) logic
   - Ensure migrations are idempotent and reversible

4. **Indexes & performance**
   - Add indexes for frequently queried columns
   - Avoid over-indexing
   - Optimize for common query patterns

## Best Practices
- Keep schemas simple and consistent
- Avoid premature optimization
- Document tables and relationships
- Test migrations on staging before production
- Never edit old migrations; create new ones

## Example Structure

```sql
-- users table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posts table
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_user
    FOREIGN KEY (user_id)
    REFERENCES users(id)
    ON DELETE CASCADE
);
