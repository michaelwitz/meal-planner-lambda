# Meal Planner API Tests

## Overview
This directory contains all unit and integration tests for the Meal Planner API.
Tests can be run against either a local Docker PostgreSQL database or a cloud AWS Aurora database.

## Test Structure
- `conftest.py` - Pytest fixtures and test configuration
- `db_config.py` - Database configuration for local and cloud testing
- `run_tests.py` - Convenient test runner script for database selection
- `test_auth.py` - Authentication endpoint tests

## Database Configuration

### Setting Up Environment Variables
The test database URLs are configured in your `.env` file in the project root.

**Required environment variables:**
- `TEST_DATABASE_URL_LOCAL` - Local Docker PostgreSQL connection string
- `TEST_DATABASE_URL_CLOUD` - AWS Aurora Serverless PostgreSQL connection string  
- `TEST_DB_TARGET` - Default target: `local` or `cloud` (defaults to `local`)

**Note:** The `.env` file is already configured with both local and cloud database connections.

## Using the Test Runner Script

The `run_tests.py` script provides a convenient way to run tests with different databases:

```bash
# From the backend directory
python tests/run_tests.py                    # Run with local database (default)
python tests/run_tests.py --cloud            # Run with cloud database
python tests/run_tests.py --check            # Check database connections
python tests/run_tests.py --cloud --verbose  # Cloud database with verbose output
python tests/run_tests.py --coverage         # Run with coverage report
python tests/run_tests.py --file tests/test_auth.py  # Run specific test file
```

## Running Tests with Local Database

### Prerequisites
1. Activate the Python environment:
   ```bash
   conda activate meal-planner
   ```

2. Start the local test database:
   ```bash
   docker-compose -f docker-compose.test.yml up -d
   ```

### Run Tests with Local Database
```bash
# Uses local database by default
pytest

# Explicitly specify local database
pytest --db-target=local

# Or use environment variable
TEST_DB_TARGET=local pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=app --cov-report=term-missing
```

## Running Tests with Cloud Database

### Prerequisites
1. Ensure cloud database credentials are in your `.env` file
2. Ensure you can connect to the AWS Aurora database
   ```bash
   # Test connection (optional)
   psql -h meal-planner-db.cluster-cczg0cscuj55.us-east-1.rds.amazonaws.com -U postgres_admin -d meal_planner_test
   ```

### Run Tests with Cloud Database
```bash
# Using command-line option
pytest --db-target=cloud

# Using environment variable
TEST_DB_TARGET=cloud pytest

# With verbose output
pytest --db-target=cloud -v

# Run specific test file with cloud database
pytest --db-target=cloud tests/test_auth.py -v
```

### ⚠️ Cloud Database Notes
- The cloud database will be completely dropped and recreated for each test
- Make sure this is a dedicated test database, not production
- Tests may run slower due to network latency
- Ensure stable internet connection for consistent test results

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
