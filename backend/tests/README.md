# Meal Planner API Tests

## Overview
This directory contains all unit and integration tests for the Meal Planner API.

## Test Structure
- `conftest.py` - Pytest fixtures and test configuration
- `test_auth.py` - Authentication endpoint tests

## Running Tests

### Prerequisites
1. Activate the Python environment:
   ```bash
   conda activate meal-planner
   ```

2. Start the test database:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

### Run All Tests
```bash
# From the backend directory
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=term-missing
```

### Run Specific Test Files
```bash
# Run only authentication tests
pytest tests/test_auth.py -v
```

### Run Specific Test Cases
```bash
# Run a specific test class
pytest tests/test_auth.py::TestAuthentication -v

# Run a specific test method
pytest tests/test_auth.py::TestAuthentication::test_register_new_user_success -v
```

## Test Coverage

### Check Coverage for Specific Modules
```bash
# Coverage for auth module
pytest tests/test_auth.py --cov=app.blueprints.auth --cov=app.services.auth_service --cov-report=term-missing
```

### Generate HTML Coverage Report
```bash
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

## Test Database
The tests use a separate PostgreSQL database running on port 5456 (configured in `docker-compose.test.yml`).

- Database: `meal_planner_test_db`
- Port: 5456
- Container: `meal_planner_test_db`

The test database is automatically cleared and recreated for each test function to ensure test isolation.

## Writing New Tests

### Test Structure
```python
class TestFeatureName:
    """Group related tests in a class."""
    
    def test_successful_case(self, client):
        """Test the happy path."""
        # Arrange: Set up test data
        # Act: Perform the action
        # Assert: Check the results
        
    def test_error_case(self, client):
        """Test error handling."""
        # Test validation errors, edge cases, etc.
```

### Available Fixtures
- `app` - Flask application configured for testing
- `client` - Test client for making HTTP requests
- `auth_headers` - Headers with valid JWT token for authenticated requests
- `runner` - CLI runner for testing Flask commands

## Cleanup
After running tests, stop the test database:
```bash
docker-compose -f docker-compose.test.yml down
```

## Current Test Status
✅ **Authentication Tests (12/12 passing)**
- User registration with validation
- Duplicate email/username prevention
- Password strength validation
- Login with email or username
- Invalid credential handling
- JWT-protected profile endpoint
- Logout functionality

## TODO
- [ ] Add tests for password reset endpoints (when implemented)
- [ ] Add tests for token refresh endpoints (when implemented)
- [ ] Add tests for user profile update endpoints
- [ ] Add tests for food catalog endpoints
- [ ] Add tests for meal planning endpoints
- [ ] Add tests for user favorites endpoints
