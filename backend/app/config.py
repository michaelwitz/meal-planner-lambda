"""Flask application configuration."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration."""
    
    # Flask - REQUIRED
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    # Database - REQUIRED
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # JWT - REQUIRED
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    if not JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable is not set")
    
    JWT_ACCESS_TOKEN_EXPIRES_STR = os.getenv('JWT_ACCESS_TOKEN_EXPIRES')
    if not JWT_ACCESS_TOKEN_EXPIRES_STR:
        raise ValueError("JWT_ACCESS_TOKEN_EXPIRES environment variable is not set")
    JWT_ACCESS_TOKEN_EXPIRES = int(JWT_ACCESS_TOKEN_EXPIRES_STR)
    
    # API - Hardcoded as part of application design
    API_PREFIX = '/api'


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    
    # Override database URL for testing
    TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL')
    if TEST_DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL
    # If TEST_DATABASE_URL not set, will use regular DATABASE_URL from parent Config


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
