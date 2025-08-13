"""
Test suite for authentication endpoints.

How pytest works:
1. Each function starting with 'test_' is a test case
2. Fixtures (from conftest.py) are passed as parameters
3. Use 'assert' statements to check conditions
4. If any assertion fails, the test fails
"""

import pytest
import json


class TestAuthentication:
    """Group authentication tests in a class for organization."""
    
    def test_register_new_user_success(self, client):
        """
        Test successful user registration.
        
        Args:
            client: Test client fixture from conftest.py
        """
        # Arrange: Prepare test data
        new_user_data = {
            'email': 'newuser@test.com',
            'username': 'newuser-123',  # Testing hyphen in username
            'password': 'SecurePass123',
            'full_name': 'New Test User',
            'sex': 'FEMALE',
            'phone_number': '555-1234',
            'address_line_1': '456 New St',
            'city': 'New City',
            'state_province_code': 'NC',
            'country_code': 'us',  # Testing lowercase (should be uppercased)
            'postal_code': '54321'
        }
        
        # Act: Make the request
        response = client.post('/api/auth/register', 
                              json=new_user_data,
                              content_type='application/json')
        
        # Assert: Check the response
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'access_token' in data
        assert data['token_type'] == 'bearer'
        assert data['expires_in'] == 86400  # 24 hours as configured
        
        # Check user data in response
        assert data['user']['email'] == 'newuser@test.com'
        assert data['user']['username'] == 'newuser-123'
        assert data['user']['full_name'] == 'New Test User'
        assert data['user']['country_code'] == 'US'  # Should be uppercased
        assert 'password' not in data['user']  # Password should never be returned
        assert 'password_hash' not in data['user']
    
    def test_register_duplicate_email_fails(self, client):
        """Test that registering with existing email fails."""
        # Try to register with existing email
        duplicate_data = {
            'email': 'existing@test.com',  # This user exists in fixtures
            'username': 'different_username',
            'password': 'Password123',
            'full_name': 'Another User',
            'sex': 'MALE',
            'phone_number': '555-9999',
            'address_line_1': '789 Street',
            'city': 'City',
            'state_province_code': 'ST',
            'country_code': 'US',
            'postal_code': '11111'
        }
        
        response = client.post('/api/auth/register', json=duplicate_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email already registered' in data['error']
    
    def test_register_duplicate_username_fails(self, client):
        """Test that registering with existing username fails."""
        duplicate_data = {
            'email': 'different@test.com',
            'username': 'existinguser',  # This username exists in fixtures
            'password': 'Password123',
            'full_name': 'Another User',
            'sex': 'OTHER',
            'phone_number': '555-8888',
            'address_line_1': '321 Avenue',
            'city': 'Town',
            'state_province_code': 'TW',
            'country_code': 'US',
            'postal_code': '22222'
        }
        
        response = client.post('/api/auth/register', json=duplicate_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Username already taken' in data['error']
    
    def test_register_invalid_password_fails(self, client):
        """Test that weak password is rejected."""
        invalid_data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'weak',  # Too short, no numbers
            'full_name': 'Test User',
            'sex': 'MALE',
            'phone_number': '555-7777',
            'address_line_1': '111 Street',
            'city': 'City',
            'state_province_code': 'ST',
            'country_code': 'US',
            'postal_code': '33333'
        }
        
        response = client.post('/api/auth/register', json=invalid_data)
        
        assert response.status_code == 400  # Bad request for invalid password
    
    def test_login_with_email_success(self, client):
        """Test successful login with email."""
        login_data = {
            'login': 'existing@test.com',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['email'] == 'existing@test.com'
        assert data['user']['username'] == 'existinguser'
    
    def test_login_with_username_success(self, client):
        """Test successful login with username."""
        login_data = {
            'login': 'existinguser',
            'password': 'password123'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['username'] == 'existinguser'
    
    def test_login_wrong_password_fails(self, client):
        """Test login with wrong password."""
        login_data = {
            'login': 'existing@test.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid credentials' in data['error']
    
    def test_login_nonexistent_user_fails(self, client):
        """Test login with non-existent user."""
        login_data = {
            'login': 'nonexistent@test.com',
            'password': 'anypassword'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid credentials' in data['error']
    
    def test_get_profile_with_token_success(self, client, auth_headers):
        """
        Test getting user profile with valid JWT token.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture with JWT token
        """
        response = client.get('/api/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['email'] == 'existing@test.com'
        assert data['username'] == 'existinguser'
        assert 'password' not in data
        assert 'password_hash' not in data
    
    def test_get_profile_without_token_fails(self, client):
        """Test that profile endpoint requires authentication."""
        response = client.get('/api/auth/profile')
        
        assert response.status_code == 401  # Unauthorized
        data = response.get_json()
        assert 'msg' in data  # Flask-JWT-Extended error message
    
    def test_get_profile_with_invalid_token_fails(self, client):
        """Test profile endpoint with invalid token."""
        headers = {
            'Authorization': 'Bearer invalid.token.here',
            'Content-Type': 'application/json'
        }
        
        response = client.get('/api/auth/profile', headers=headers)
        
        assert response.status_code == 422  # Unprocessable Entity
        data = response.get_json()
        assert 'msg' in data
    
    def test_logout_with_token_success(self, client, auth_headers):
        """Test logout endpoint with valid token."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        assert 'Logout successful' in data['message']
