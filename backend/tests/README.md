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

### Environment Variables
All database URLs are configured in the `.env` file in the project root.

#### Development Database
- `DEV_DATABASE_URL` - Development database connection (port 5455)
- Used when running the Flask app locally with `flask run`

#### Test Databases
- `TEST_DATABASE_URL_LOCAL` - Local Docker test database (port 5456)
- `TEST_DATABASE_URL_CLOUD` - AWS Aurora cloud test database
- `TEST_DATABASE_URL` - Active test database (automatically set by test runner)

#### Database Selection
- `TEST_DB_TARGET` - Default target: `local` or `cloud` (defaults to `local`)

**Note:** The test runner script (`run_tests.py`) automatically sets `TEST_DATABASE_URL` based on your target selection.

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
   # From project root
   docker-compose -f docker-compose.test.yml up -d
   ```

### Run Tests with Local Database
```bash
# Using the test runner script (recommended)
python tests/run_tests.py --local

# Or directly with pytest (requires TEST_DATABASE_URL to be set)
pytest

# With verbose output
python tests/run_tests.py --local --verbose

# With coverage report
python tests/run_tests.py --local --coverage
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
# Using the test runner script (recommended)
python tests/run_tests.py --cloud

# With verbose output
python tests/run_tests.py --cloud --verbose

# Run specific test file with cloud database
python tests/run_tests.py --cloud --file tests/test_auth.py

# With coverage report
python tests/run_tests.py --cloud --coverage
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

## Test Databases

### Local Test Database (Docker)
- **Port**: 5456 (different from development port 5455)
- **Container**: `meal_planner_test_db`
- **Database**: `meal_planner_test_db`
- **Docker Compose**: `docker-compose.test.yml`

### Cloud Test Database (AWS Aurora)
- **Type**: AWS Aurora Serverless PostgreSQL
- **Database**: `meal_planner_test`
- **Region**: us-east-1

**Note**: Both databases are automatically cleared and recreated for each test function to ensure test isolation.

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
✅ **Authentication Tests (16/16 passing)**
- User registration with validation
- Duplicate email/username prevention  
- Password strength validation
- Missing required fields validation
- Invalid email format validation
- Invalid sex value validation
- Login with email or username
- Empty credentials handling
- Invalid credential handling
- JWT-protected profile endpoint
- Invalid/missing token handling
- Logout functionality

## TODO
- [ ] Add tests for password reset endpoints (when implemented)
- [ ] Add tests for token refresh endpoints (when implemented)
- [ ] Add tests for user profile update endpoints
- [ ] Add tests for food catalog endpoints
- [ ] Add tests for meal planning endpoints
- [ ] Add tests for user favorites endpoints
