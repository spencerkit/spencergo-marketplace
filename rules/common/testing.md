# Testing

## Minimum Test Coverage: 80%

Test Types (ALL required):
1. **Unit Tests** - Individual functions, utilities, components
2. **Integration Tests** - API endpoints, database operations
3. **E2E Tests** - Critical user flows (framework chosen per language)

## Test-Driven Development

MANDATORY workflow:
1. Write test first (RED)
2. Run test - it should FAIL
3. Write minimal implementation (GREEN)
4. Run test - it should PASS
5. Refactor (IMPROVE)
6. Verify coverage (80%+)

## Test Quality

- Tests should be readable and self-documenting
- Use descriptive test names that explain the scenario
- Follow AAA pattern: Arrange, Act, Assert
- Avoid test interdependence - each test should run independently
- Mock external dependencies (APIs, databases, file system)
