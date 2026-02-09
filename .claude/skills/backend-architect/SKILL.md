---
name: backend-routes-db
description: Generate backend routes, handle requests/responses, and connect to databases. Use for API and server-side development.
---

# Backend Routes & Database Integration

## Instructions

1. **Project setup**
   - Choose backend framework (e.g., Express, FastAPI)
   - Configure environment variables
   - Initialize server entry point

2. **Route generation**
   - Define RESTful routes (GET, POST, PUT, DELETE)
   - Use route grouping/modules
   - Apply middleware for validation and auth

3. **Request & response handling**
   - Parse request body and params
   - Validate input data
   - Return structured JSON responses
   - Handle errors with proper status codes

4. **Database connection**
   - Configure DB client/ORM
   - Establish secure connection
   - Create models/schemas
   - Perform CRUD operations

## Best Practices
- Use async/await for non-blocking operations
- Centralize error handling
- Never expose sensitive data in responses
- Use environment variables for secrets
- Keep controllers, routes, and models separated

## Example Structure
```js
// routes/user.routes.js
import express from "express";
import { getUsers, createUser } from "../controllers/user.controller.js";

const router = express.Router();

router.get("/", getUsers);
router.post("/", createUser);

export default router;
