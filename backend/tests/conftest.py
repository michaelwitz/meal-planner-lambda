"""
Pytest fixtures for test setup using PostgreSQL test database.

To run tests:
1. Start the test database: docker-compose -f docker-compose.test.yml up -d
2. Run tests: pytest
3. Stop test database: docker-compose -f docker-compose.test.yml down
"""

import pytest
import os
from app import create_app
from app.models.database import db
from app.models.entities import User
import bcrypt


@pytest.fixture(scope='function')
def app():
    """
    Create a Flask app configured for testing with PostgreSQL.
    
    This fixture:
    1. Uses TEST_DATABASE_URL from environment
    2. Configures the app for testing
    3. Creates all tables in test database
    4. Yields the app for testing
    5. Drops all tables after test
    
    scope='function' means this runs for each test function
    """
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
