"""Flask application configuration."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
project_root = Path(__file__).parent.parent.parent  # Go up from app/ to backend/ to project root/
env_path = project_root / '.env'
load_dotenv(env_path)


class Config:
    """Base configuration."""
    
    # Flask - REQUIRED
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    # Database - Use DEV_DATABASE_URL (required for development/production)
    # TestingConfig will override this with TEST_DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'postgresql://placeholder')
    # Note: We use a placeholder to avoid errors during import when testing
    # The actual database URL will be set by TestingConfig
    
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
    
    # Override database URL for testing if TEST_DATABASE_URL is set
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', Config.SQLALCHEMY_DATABASE_URI)


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
