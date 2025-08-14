#!/usr/bin/env python3
"""
Test runner script for Meal Planner API.

This script provides an easy way to run tests against either local or cloud databases.

Usage:
    python run_tests.py                    # Run with default (local) database
    python run_tests.py --local            # Explicitly use local database
    python run_tests.py --cloud            # Use cloud database
    python run_tests.py --check            # Check database connections
    python run_tests.py --cloud --verbose  # Run with cloud database in verbose mode
    python run_tests.py --cloud --file tests/test_auth.py  # Run specific test file
"""

import sys
import os
import subprocess
import argparse
from pathlib import Path

# Add backend directory to path to import test modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.db_config import TestDatabaseConfig


def check_database_connections():
    """Check connections to both local and cloud databases."""
    print("🔍 Checking database connections...\n")
    
    # Check local database
    print("Local Database:")
    try:
        TestDatabaseConfig.validate_connection('local')
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Tip: Make sure Docker is running and start the test database:")
        print("      docker-compose -f docker-compose.test.yml up -d\n")
    
    # Check cloud database
    print("\nCloud Database:")
    try:
        TestDatabaseConfig.validate_connection('cloud')
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Tip: Check your .env file for TEST_DATABASE_URL_CLOUD")
        print("   💡 Ensure you have network access to AWS Aurora database\n")


def run_tests(args):
    """Run pytest with the specified configuration."""
    # Build pytest command
    pytest_args = ['pytest']
    
    # Add database target
    if args.cloud:
        pytest_args.extend(['--db-target=cloud'])
        print("🌩️  Running tests with CLOUD database")
    else:
        pytest_args.extend(['--db-target=local'])
        print("🏠 Running tests with LOCAL database")
    
    # Add verbose flag
    if args.verbose:
        pytest_args.append('-v')
    
    # Add coverage report
    if args.coverage:
        pytest_args.extend(['--cov=app', '--cov-report=term-missing'])
    
    # Add specific test file or directory
    if args.file:
        pytest_args.append(args.file)
    
    # Add any additional pytest arguments
    if args.pytest_args:
        pytest_args.extend(args.pytest_args)
    
    print(f"📝 Command: {' '.join(pytest_args)}\n")
    
    # Run pytest
    result = subprocess.run(pytest_args)
    return result.returncode


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run Meal Planner API tests with local or cloud database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                     # Run all tests with local database
  python run_tests.py --cloud             # Run all tests with cloud database
  python run_tests.py --check             # Check database connections
  python run_tests.py --cloud -v          # Verbose output with cloud database
  python run_tests.py --file tests/test_auth.py  # Run specific test file
  python run_tests.py --coverage          # Run with coverage report
  python run_tests.py -- -x               # Stop on first failure (pytest arg)
        """
    )
    
    # Database selection
    db_group = parser.add_mutually_exclusive_group()
    db_group.add_argument(
        '--local',
        action='store_true',
        default=True,
        help='Use local Docker database (default)'
    )
    db_group.add_argument(
        '--cloud',
        action='store_true',
        help='Use cloud AWS Aurora database'
    )
    
    # Other options
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check database connections and exit'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose test output'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Generate coverage report'
    )
    parser.add_argument(
        '--file',
        help='Specific test file or directory to run'
    )
    parser.add_argument(
        'pytest_args',
        nargs=argparse.REMAINDER,
        help='Additional arguments to pass to pytest (use -- before pytest args)'
    )
    
    args = parser.parse_args()
    
    # Remove -- from pytest args if present
    if args.pytest_args and args.pytest_args[0] == '--':
        args.pytest_args = args.pytest_args[1:]
    
    # Check database connections if requested
    if args.check:
        check_database_connections()
        return 0
    
    # Run tests
    return run_tests(args)


if __name__ == '__main__':
    sys.exit(main())
