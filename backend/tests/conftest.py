"""
Pytest fixtures for test setup using PostgreSQL test database.

To run tests with local database:
1. Start the test database: docker-compose -f docker-compose.test.yml up -d
2. Run tests: pytest  (or TEST_DB_TARGET=local pytest)
3. Stop test database: docker-compose -f docker-compose.test.yml down

To run tests with cloud database:
1. Ensure cloud database credentials are in .env file
2. Run tests: TEST_DB_TARGET=cloud pytest

To specify database target via command line:
pytest --db-target=local  (or --db-target=cloud)
"""

import pytest
import os
from app import create_app
from app.models.database import db
from app.models.entities import User
import bcrypt
from tests.db_config import TestDatabaseConfig, get_test_database_url


def pytest_addoption(parser):
    """
    Add custom command-line options to pytest.
    
    This allows running tests with:
    pytest --db-target=local
    pytest --db-target=cloud
    """
    parser.addoption(
        "--db-target",
        action="store",
        default=None,
        help="Database target for tests: local or cloud (default: uses TEST_DB_TARGET env var or 'local')"
    )


@pytest.fixture(scope='session')
def db_target(request):
    """
    Get the database target from command-line option or environment.
    
    Priority:
    1. Command-line option (--db-target)
    2. TEST_DB_TARGET environment variable
    3. Default to 'local'
    """
    return request.config.getoption("--db-target")


@pytest.fixture(scope='function')
def app(db_target):
    """
    Create a Flask app configured for testing with PostgreSQL.
    
    This fixture:
    1. Uses database URL based on db_target (local or cloud)
    2. Configures the app for testing
    3. Creates all tables in test database
    4. Yields the app for testing
    5. Drops all tables after test (only for local database)
    
    scope='function' means this runs for each test function
    """
    # Get database URL based on target
    database_url = get_test_database_url(db_target)
    is_cloud = TestDatabaseConfig.is_cloud_database(db_target)
    
    # Set the database URL in environment for the app to use
    os.environ['TEST_DATABASE_URL'] = database_url
    
    # Create app with test config (will use TEST_DATABASE_URL)
    app = create_app('testing')
    
    # Create tables in test database
    with app.app_context():
        db.create_all()
        
        # Add a test user that already exists
        existing_user = User(
            email='existing@test.com',
            username='existinguser',
            password_hash=bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode('utf-8'),
            full_name='Existing User',
            sex='MALE',
            phone_number='555-0001',
            address_line_1='123 Test St',
            city='Test City',
            state_province_code='TC',
            country_code='US',
            postal_code='12345'
        )
        db.session.add(existing_user)
        db.session.commit()
    
    yield app
    
    # Cleanup: drop all tables after test
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create a test client for making HTTP requests.
    
    This fixture provides a way to make requests to your Flask app
    without running a real server.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create a test runner for CLI commands.
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def auth_headers(client):
    """
    Get authentication headers with a valid JWT token.
    
    This fixture logs in a test user and returns headers with the JWT token.
    """
    # Login to get token
    response = client.post('/api/auth/login', 
        json={
            'login': 'existing@test.com',
            'password': 'password123'
        }
    )
    
    data = response.get_json()
    token = data['access_token']
    
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
