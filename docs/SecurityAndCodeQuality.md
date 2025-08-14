# Security and Code Quality Guide

## Overview

This document outlines the security practices, tools, and procedures for maintaining high code quality and security standards in the Meal Planner API project.

## Table of Contents
- [Security Tools](#security-tools)
- [Quick Start](#quick-start)
- [Security Scanning](#security-scanning)
- [Code Quality](#code-quality)
- [CI/CD Integration](#cicd-integration)
- [Security Best Practices](#security-best-practices)

## Security Tools

### 1. **pip-audit** (Dependency Vulnerabilities)
- Official tool from Python Packaging Authority (PyPA)
- Scans Python packages against OSV (Open Source Vulnerability) database
- Automatically installed when running security audit

### 2. **Safety** (Additional CVE Database) - Optional
- Additional vulnerability checking using pyup.io database
- Install with: `pip install safety`

### 3. **Ruff** (Code Security & Quality)
- Modern, fast security and quality scanner (written in Rust)
- Includes all Bandit security rules (S-prefix) plus 700+ additional checks
- 10-100x faster than traditional tools
- Replaces: Bandit, Flake8, Black, isort

### 4. **Dependabot** (Automated Updates)
- GitHub-native dependency updater
- Configured for weekly scans
- Automatic PRs for security updates

## Quick Start

### Installation
```bash
# Navigate to backend directory
cd backend

# Install development dependencies (includes Ruff)
pip install -r requirements.txt

# pip-audit will auto-install on first run
```

### Basic Security Scan
```bash
# Run complete security audit
python scripts/security_audit.py

# Quick vulnerability scan (CI/CD friendly)
python scripts/security_audit.py --quick
```

## Security Scanning

### Using the Security Audit Script

The `backend/scripts/security_audit.py` script provides comprehensive security scanning:

#### Scan Options

| Command | Description | Use Case |
|---------|-------------|----------|
| `python scripts/security_audit.py` | Full scan (all checks) | Pre-commit, releases |
| `python scripts/security_audit.py --quick` | pip-audit only | CI/CD pipelines |
| `python scripts/security_audit.py --deps` | Dependencies only | Dependency review |
| `python scripts/security_audit.py --code` | Code security only | Code review |

#### Example Output
```
🔒 Security Audit for Meal Planner API
============================================================

🔍 Running pip-audit vulnerability scan...
  ✅ No vulnerabilities found with pip-audit

🔍 Running Ruff security analysis...
  ✅ No security issues found with Ruff

📦 Checking for outdated packages...
  📋 Found 22 outdated packages

============================================================
📊 SECURITY AUDIT SUMMARY
============================================================
✅ No security issues found!
  • Outdated packages: 22
============================================================
```

### Fixing Vulnerabilities

When vulnerabilities are found:

1. **Update the version in `requirements.txt`**
2. **Install updated packages:** `pip install -r requirements.txt --upgrade`
3. **Test the application:** `python tests/run_tests.py --local`
4. **Commit the changes**

## Code Quality

### Ruff Configuration

Our Ruff configuration (`backend/pyproject.toml`) includes:

- **Security Rules (S)**: All Bandit security checks
- **Error/Warning Rules (E, W)**: PEP 8 compliance
- **Code Quality (F, B, C4)**: Bug detection, comprehensions
- **Simplification (SIM)**: Code simplification suggestions
- **Import Sorting (I)**: Consistent import organization

### Running Ruff

```bash
# Check all code issues
ruff check app

# Check only security issues
ruff check app --select S

# Auto-fix fixable issues
ruff check app --fix

# Format code (replaces Black)
ruff format app

# Show statistics
ruff check app --statistics
```

### Common Security Rules

| Rule | Description | Severity |
|------|-------------|----------|
| S101 | Use of assert | Low (tests excluded) |
| S105 | Hardcoded password | High |
| S106 | Hardcoded password | High |
| S110 | try-except-pass | Medium |
| S301 | Pickle usage | High |
| S608 | SQL injection | Critical |

### Ignoring False Positives

Add to `pyproject.toml`:
```toml
[tool.ruff.lint.per-file-ignores]
"path/to/file.py" = ["S105"]  # Ignore specific rule for file
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/security.yml
name: Security Check

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run security audit
        run: |
          cd backend
          python scripts/security_audit.py --quick
```

### Pre-commit Hooks (Optional)

Create `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.12.9
    hooks:
      - id: ruff
        args: [--select, S]  # Security only
      - id: ruff-format
```

Install: `pre-commit install`

## Security Best Practices

### Dependency Management
- ✅ Pin exact versions in `requirements.txt`
- ✅ Review Dependabot PRs before merging
- ✅ Test thoroughly after updates
- ✅ Keep dependencies minimal

### Secrets Management
- ✅ Never commit secrets to git
- ✅ Use environment variables (`.env` file)
- ✅ Use strong, unique passwords
- ✅ Rotate secrets regularly

### Code Security
- ✅ Validate all user input
- ✅ Use parameterized SQL queries (SQLAlchemy ORM)
- ✅ Implement proper authentication (JWT)
- ✅ Use HTTPS in production
- ✅ Log security events

### Database Security
- ✅ Use least privilege principle
- ✅ Encrypt sensitive data
- ✅ Regular backups
- ✅ Use strong passwords

## Quick Reference

### Essential Commands
```bash
# Full security audit
python scripts/security_audit.py

# Quick vulnerability check
python scripts/security_audit.py --quick

# Code security only
ruff check app --select S

# Fix code issues
ruff check app --fix

# Format code
ruff format app

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests after updates
python tests/run_tests.py --local
```

### File Locations
- **Security script:** `backend/scripts/security_audit.py`
- **Ruff config:** `backend/pyproject.toml`
- **Dependencies:** `backend/requirements.txt`
- **Dependabot:** `.github/dependabot.yml`

## Maintenance Schedule

| Task | Frequency | Command/Action |
|------|-----------|----------------|
| Dependency scan | Daily (automated) | Dependabot |
| Manual audit | Before releases | `python scripts/security_audit.py` |
| Update dependencies | As needed | Review Dependabot PRs |
| Code quality check | Pre-commit | `ruff check app` |

## Additional Resources

- [OWASP Python Security](https://owasp.org/www-project-python-security/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [GitHub Security Features](https://docs.github.com/en/code-security)

---

*Last Updated: December 2024*
