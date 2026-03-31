# AGENTS.md

## Commands

- **Lint**: `npm run lint` (ESLint with Prettier integration)
- **Lint Fix**: `npm run lint:fix` (Auto-fix linting issues)
- **Test**: No test framework configured (npm test returns error)
- **Start**: `node app.js` (Runs on port 3003)

## Code Style Guidelines

### Import Organization

- External imports first (express, mongoose, etc.)
- Local imports second (controllers, models, utils)
- Use CommonJS require() syntax

### Formatting & Linting

- ESLint with Prettier integration
- ES2021 syntax, CommonJS modules
- 2-space indentation (Prettier default)
- No semicolons (follow existing codebase pattern)

### Naming Conventions

- **Files**: kebab-case (voxSpotify.js, users.js)
- **Variables**: camelCase
- **Constants**: UPPER_SNAKE_CASE for environment variables
- **Functions**: camelCase for module exports

### Error Handling

- Use try-catch for async operations
- Return consistent JSON responses with status codes
- Always sanitize user input with mongoSanitize
- Handle database connection errors gracefully

### Security

- Always use mongoSanitize on req.body, req.params, req.query
- Environment variables for sensitive data (MongoDB connection strings)
- Helmet.js for security headers with environment-specific configs
- Generate secure random tokens using crypto.randomBytes()

### Database Patterns

- Mongoose schemas with required fields
- Use findOneAndUpdate for atomic operations
- Upsert operations where appropriate
- Handle null/default values explicitly
