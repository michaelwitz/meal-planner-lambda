"""
Test database configuration for local and cloud testing.

This module provides configuration for both local Docker PostgreSQL
and AWS Aurora Serverless PostgreSQL databases.

All sensitive information (URLs, passwords) should be stored in .env file.

Usage:
    # Use local database (default)
    TEST_DB_TARGET=local pytest
    
    # Use cloud database
    TEST_DB_TARGET=cloud pytest
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file in project root (parent directory)
project_root = Path(__file__).parent.parent.parent  # Go up from tests/ to backend/ to project root/
env_path = project_root / '.env'
load_dotenv(env_path)


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    name: str
    url: str
    description: str
    is_cloud: bool = False
    requires_vpn: bool = False
    
    def __str__(self):
        return f"{self.name}: {self.description}"


class TestDatabaseConfig:
    """Manages test database configurations."""
    
    @classmethod
    def _get_local_config(cls) -> DatabaseConfig:
        """Get local database configuration from environment."""
        url = os.getenv('TEST_DATABASE_URL_LOCAL')
        if not url:
            raise ValueError(
                "TEST_DATABASE_URL_LOCAL not found in environment. "
                "Please set it in your .env file."
            )
        
        return DatabaseConfig(
            name="local",
            url=url,
            description="Local Docker PostgreSQL database",
            is_cloud=False,
            requires_vpn=False
        )
    
    @classmethod
    def _get_cloud_config(cls) -> DatabaseConfig:
        """Get cloud database configuration from environment."""
        url = os.getenv('TEST_DATABASE_URL_CLOUD')
        if not url:
            raise ValueError(
                "TEST_DATABASE_URL_CLOUD not found in environment. "
                "Please set it in your .env file."
            )
        
        # Check if VPN is required (optional env var)
        requires_vpn = os.getenv('CLOUD_DB_REQUIRES_VPN', 'false').lower() == 'true'
        
        return DatabaseConfig(
            name="cloud",
            url=url,
            description="AWS Aurora Serverless PostgreSQL database",
            is_cloud=True,
            requires_vpn=requires_vpn
        )
    
    @classmethod
    def get_config(cls, target: Optional[str] = None) -> DatabaseConfig:
        """
        Get database configuration based on target.
        
        Args:
            target: Database target ('local' or 'cloud'). If None, uses TEST_DB_TARGET env var.
                   Defaults to 'local' if not specified.
        
        Returns:
            DatabaseConfig object for the selected target.
        
        Raises:
            ValueError: If target is not recognized or configuration is missing.
        """
        if target is None:
            target = os.getenv('TEST_DB_TARGET', 'local').lower()
        
        if target == 'local':
            config = cls._get_local_config()
        elif target == 'cloud':
            config = cls._get_cloud_config()
        else:
            raise ValueError(
                f"Unknown database target: {target}. "
                "Available options: local, cloud"
            )
        
        print(f"\n🗄️  Using {config.name} database for testing")
        print(f"   {config.description}")
        
        if config.is_cloud:
            print("   ⚠️  Warning: Using cloud database. Be careful with test data!")
            if config.requires_vpn:
                print("   🔒 Note: VPN connection may be required")
        
        return config
    
    @classmethod
    def get_database_url(cls, target: Optional[str] = None) -> str:
        """
        Get database URL for the specified target.
        
        Args:
            target: Database target ('local' or 'cloud')
        
        Returns:
            Database URL string
        """
        return cls.get_config(target).url
    
    @classmethod
    def is_cloud_database(cls, target: Optional[str] = None) -> bool:
        """
        Check if the target is a cloud database.
        
        Args:
            target: Database target
        
        Returns:
            True if cloud database, False otherwise
        """
        return cls.get_config(target).is_cloud
    
    @classmethod
    def validate_connection(cls, target: Optional[str] = None) -> bool:
        """
        Validate that we can connect to the specified database.
        
        Args:
            target: Database target
        
        Returns:
            True if connection successful, raises exception otherwise
        """
        from sqlalchemy import create_engine
        from sqlalchemy.exc import OperationalError
        
        config = cls.get_config(target)
        engine = create_engine(config.url)
        
        try:
            with engine.connect() as conn:
                result = conn.execute("SELECT 1")
                print(f"   ✅ Successfully connected to {config.name} database")
                return True
        except OperationalError as e:
            print(f"   ❌ Failed to connect to {config.name} database")
            raise e
        finally:
            engine.dispose()


# Convenience function for quick access
def get_test_database_url(target: Optional[str] = None) -> str:
    """Get test database URL for the specified target."""
    return TestDatabaseConfig.get_database_url(target)
