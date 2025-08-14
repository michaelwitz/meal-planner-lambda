#!/usr/bin/env python3
"""
Security audit script for Meal Planner API.

This script performs comprehensive security scanning of Python dependencies
and code for known vulnerabilities and security issues.

Usage:
    python scripts/security_audit.py              # Run all security checks
    python scripts/security_audit.py --quick      # Quick scan (pip-audit only) - fastest
    python scripts/security_audit.py --deps       # Full dependency scan (pip-audit + Safety + outdated)
    python scripts/security_audit.py --code       # Only scan code with Ruff
"""

import sys
import subprocess
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class Colors:
    """Terminal color codes."""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class SecurityAuditor:
    """Performs security audits on Python projects."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.backend_dir = project_root / 'backend'
        self.requirements_file = self.backend_dir / 'requirements.txt'
        self.vulnerabilities_found = False
        
    def check_tool_installed(self, tool: str) -> bool:
        """Check if a security tool is installed."""
        try:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
    
    def ensure_pip_audit(self) -> bool:
        """Ensure pip-audit is installed."""
        if not self.check_tool_installed('pip-audit'):
            print(f"{Colors.YELLOW}📦 Installing pip-audit...{Colors.RESET}")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', 'pip-audit'],
                    check=True,
                    capture_output=True
                )
                print(f"{Colors.GREEN}✅ pip-audit installed{Colors.RESET}")
                return True
            except subprocess.CalledProcessError:
                print(f"{Colors.RED}❌ Failed to install pip-audit{Colors.RESET}")
                return False
        return True
    
    def run_pip_audit(self) -> Tuple[bool, List[Dict]]:
        """Run pip-audit to check for vulnerable dependencies."""
        if not self.ensure_pip_audit():
            return False, []
            
        print(f"\n{Colors.BLUE}🔍 Running pip-audit vulnerability scan...{Colors.RESET}")
        
        cmd = ['pip-audit']
        
        # Add requirements file if it exists
        if self.requirements_file.exists():
            cmd.extend(['-r', str(self.requirements_file)])
        
        # Add JSON output for parsing
        cmd.extend(['--format', 'json'])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=str(self.backend_dir)
            )
            
            # Parse JSON output
            vulnerabilities = []
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    # pip-audit returns data in {"dependencies": [...], "fixes": []}
                    if isinstance(data, dict) and 'dependencies' in data:
                        # Filter only packages with vulnerabilities
                        for dep in data['dependencies']:
                            if dep.get('vulns'):
                                vulnerabilities.append(dep)
                except json.JSONDecodeError:
                    pass
            
            if not vulnerabilities:
                print(f"{Colors.GREEN}  ✅ No vulnerabilities found with pip-audit{Colors.RESET}")
                return False, []
            else:
                # Count total vulnerabilities
                total_vulns = sum(len(pkg.get('vulns', [])) for pkg in vulnerabilities)
                print(f"{Colors.RED}  ⚠️  Found {total_vulns} vulnerabilities in {len(vulnerabilities)} packages{Colors.RESET}")
                
                for vuln in vulnerabilities:
                    print(f"\n  {Colors.YELLOW}Package:{Colors.RESET} {vuln['name']} {vuln['version']}")
                    for v in vuln.get('vulns', []):
                        print(f"    {Colors.RED}ID:{Colors.RESET} {v['id']}")
                        if 'aliases' in v and v['aliases']:
                            print(f"    {Colors.YELLOW}CVE:{Colors.RESET} {', '.join(v['aliases'])}")
                        desc = v.get('description', 'No description')[:150]
                        print(f"    {Colors.RESET}Description: {desc}...")
                        if 'fix_versions' in v and v['fix_versions']:
                            fix_ver = v['fix_versions'][0] if v['fix_versions'] else 'Unknown'
                            print(f"    {Colors.GREEN}Fix:{Colors.RESET} Update to {fix_ver} in requirements.txt")
                
                return True, vulnerabilities
                
        except Exception as e:
            print(f"{Colors.RED}  ❌ Error running pip-audit: {e}{Colors.RESET}")
            return False, []
    
    def run_safety_check(self) -> Tuple[bool, List[Dict]]:
        """Run safety check for additional vulnerability scanning."""
        if not self.check_tool_installed('safety'):
            print(f"\n{Colors.YELLOW}⏭️  Safety not installed. Install with: pip install safety{Colors.RESET}")
            print(f"{Colors.BLUE}    Safety provides additional CVE checking from pyup.io database{Colors.RESET}")
            return False, []
        
        print(f"\n{Colors.BLUE}🔍 Running Safety vulnerability scan...{Colors.RESET}")
        
        cmd = ['safety', 'check', '--json']
        
        if self.requirements_file.exists():
            cmd.extend(['-r', str(self.requirements_file)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=str(self.backend_dir)
            )
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}  ✅ No vulnerabilities found with Safety{Colors.RESET}")
                return False, []
            else:
                # Safety returns JSON even on failure
                try:
                    report = json.loads(result.stdout)
                    vulnerabilities = report.get('vulnerabilities', [])
                    vuln_count = len(vulnerabilities)
                    
                    if vuln_count > 0:
                        print(f"{Colors.RED}  ⚠️  Found {vuln_count} vulnerabilities with Safety{Colors.RESET}")
                        
                        for vuln in vulnerabilities[:5]:  # Show first 5
                            print(f"\n  {Colors.YELLOW}Package:{Colors.RESET} {vuln['package_name']} {vuln['analyzed_version']}")
                            print(f"    {Colors.RED}CVE:{Colors.RESET} {vuln.get('cve', vuln.get('vulnerability_id', 'Unknown'))}")
                            severity = vuln.get('severity', 'Unknown')
                            color = Colors.RED if severity == 'high' else Colors.YELLOW
                            print(f"    {color}Severity:{Colors.RESET} {severity}")
                            print(f"    Advisory: {vuln['advisory'][:100]}...")
                        
                        if vuln_count > 5:
                            print(f"\n  ... and {vuln_count - 5} more vulnerabilities")
                        
                        return True, vulnerabilities
                except json.JSONDecodeError:
                    pass
                    
                return False, []
                
        except Exception as e:
            print(f"{Colors.RED}  ❌ Error running Safety: {e}{Colors.RESET}")
            return False, []
    
    def run_code_security(self) -> Tuple[bool, Dict]:
        """Run Ruff for security and code quality analysis."""
        if not self.check_tool_installed('ruff'):
            print(f"\n{Colors.YELLOW}⏭️  Ruff not installed{Colors.RESET}")
            print(f"{Colors.BLUE}    Install with: {Colors.GREEN}pip install ruff{Colors.RESET}")
            print(f"{Colors.BLUE}    Ruff provides fast security scanning and code quality checks{Colors.RESET}")
            return False, {}
    
        # Run Ruff with security rules
        print(f"\n{Colors.BLUE}🔍 Running Ruff security analysis...{Colors.RESET}")
        
        app_dir = self.backend_dir / 'app'
        if not app_dir.exists():
            print(f"{Colors.YELLOW}  ⏭️  No app directory found, skipping...{Colors.RESET}")
            return False, {}
        
        # Run ruff with security rules (S prefix)
        cmd = ['ruff', 'check', str(app_dir), '--select', 'S', '--output-format', 'json']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.stdout:
                issues = json.loads(result.stdout)
            else:
                issues = []
            
            if not issues:
                print(f"{Colors.GREEN}  ✅ No security issues found with Ruff{Colors.RESET}")
                return False, {'results': []}
            else:
                print(f"{Colors.RED}  ⚠️  Found {len(issues)} security issues with Ruff{Colors.RESET}")
                
                # Group by rule code
                by_rule = {}
                for issue in issues:
                    rule = issue.get('code', 'Unknown')
                    if rule not in by_rule:
                        by_rule[rule] = []
                    by_rule[rule].append(issue)
                
                for rule, rule_issues in list(by_rule.items())[:5]:  # Show first 5 rule types
                    print(f"\n  {Colors.YELLOW}Rule {rule}: {len(rule_issues)} issues{Colors.RESET}")
                    for issue in rule_issues[:2]:  # Show first 2 of each type
                        msg = issue.get('message', 'No message')
                        file = Path(issue.get('filename', 'unknown')).name
                        line = issue.get('location', {}).get('row', '?')
                        print(f"    • {msg}")
                        print(f"      {Colors.BLUE}File:{Colors.RESET} {file}:{line}")
                
                return True, {'results': issues}
                
        except Exception as e:
            print(f"{Colors.RED}  ❌ Error running Ruff: {e}{Colors.RESET}")
            return False, {}
    
    def check_outdated_packages(self) -> List[Dict]:
        """Check for outdated packages that might have security updates."""
        print(f"\n{Colors.BLUE}📦 Checking for outdated packages...{Colors.RESET}")
        
        cmd = [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json']
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            outdated = json.loads(result.stdout)
            
            if not outdated:
                print(f"{Colors.GREEN}  ✅ All packages are up to date{Colors.RESET}")
                return []
            else:
                print(f"{Colors.YELLOW}  📋 Found {len(outdated)} outdated packages:{Colors.RESET}")
                for pkg in outdated[:10]:  # Show first 10
                    print(f"    • {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
                
                if len(outdated) > 10:
                    print(f"    ... and {len(outdated) - 10} more")
                
                return outdated
                
        except Exception as e:
            print(f"{Colors.RED}  ❌ Error checking outdated packages: {e}{Colors.RESET}")
            return []
    
    def print_summary(self, pip_vulns: int, safety_vulns: int, ruff_issues: int, outdated: int):
        """Print a summary of the security audit."""
        print(f"\n{'=' * 60}")
        print(f"{Colors.BOLD}📊 SECURITY AUDIT SUMMARY{Colors.RESET}")
        print(f"{'=' * 60}")
        
        total_issues = pip_vulns + safety_vulns + ruff_issues
        
        if total_issues == 0:
            print(f"{Colors.GREEN}✅ No security issues found!{Colors.RESET}")
        else:
            print(f"{Colors.RED}⚠️  Found {total_issues} total security issues{Colors.RESET}")
            
        if pip_vulns > 0:
            print(f"  {Colors.RED}• Dependency vulnerabilities (pip-audit): {pip_vulns}{Colors.RESET}")
        if safety_vulns > 0:
            print(f"  {Colors.RED}• Dependency vulnerabilities (Safety): {safety_vulns}{Colors.RESET}")
        if ruff_issues > 0:
            print(f"  {Colors.YELLOW}• Code security issues (Ruff): {ruff_issues}{Colors.RESET}")
        if outdated > 0:
            print(f"  {Colors.BLUE}• Outdated packages: {outdated}{Colors.RESET}")
        
        print(f"{'=' * 60}\n")
        
        # Recommendations
        if total_issues > 0:
            print(f"{Colors.BOLD}📋 Recommendations:{Colors.RESET}")
            if pip_vulns > 0 or safety_vulns > 0:
                print(f"  1. Update vulnerable packages in {Colors.YELLOW}requirements.txt{Colors.RESET}")
                print(f"  2. Run '{Colors.GREEN}pip install -r requirements.txt --upgrade{Colors.RESET}' to apply updates")
                print(f"  3. Test your application after updating dependencies")
            if ruff_issues > 0:
                next_num = 4 if (pip_vulns > 0 or safety_vulns > 0) else 1
                print(f"  {next_num}. Review and fix code security issues identified by Ruff")
            if outdated > 0 and total_issues == 0:
                print(f"  1. Consider updating outdated packages for latest features and patches")
    
    def run_audit(self, deps_only: bool = False, code_only: bool = False, 
                  quick: bool = False) -> int:
        """Run the security audit."""
        print(f"{Colors.BOLD}🔒 Security Audit for Meal Planner API{Colors.RESET}")
        print("=" * 60)
        
        pip_vulns = 0
        safety_vulns = 0
        ruff_issues = 0
        outdated_count = 0
        
        # Quick mode - only run pip-audit
        if quick:
            has_vulns, vulns = self.run_pip_audit()
            # Count total vulnerabilities, not just packages
            pip_vulns = sum(len(pkg.get('vulns', [])) for pkg in vulns) if has_vulns else 0
            self.print_summary(pip_vulns, 0, 0, 0)
            return 1 if has_vulns else 0
        
        # Dependency scanning
        if not code_only:
            # Run pip-audit (always)
            has_vulns, vulns = self.run_pip_audit()
            # Count total vulnerabilities, not just packages
            pip_vulns = sum(len(pkg.get('vulns', [])) for pkg in vulns) if has_vulns else 0
            
            # Run safety check (optional)
            has_vulns, vulns = self.run_safety_check()
            safety_vulns = len(vulns) if has_vulns else 0
            
            # Check outdated packages
            outdated = self.check_outdated_packages()
            outdated_count = len(outdated)
        
        # Code scanning
        if not deps_only:
            has_issues, report = self.run_code_security()
            ruff_issues = len(report.get('results', [])) if has_issues else 0
        
        # Print summary
        self.print_summary(pip_vulns, safety_vulns, ruff_issues, outdated_count)
        
        # Return exit code
        return 1 if (pip_vulns + safety_vulns + ruff_issues) > 0 else 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Security audit script for Meal Planner API',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Quick scan: pip-audit only (fastest, good for CI/CD)'
    )
    parser.add_argument(
        '--deps',
        action='store_true',
        help='Full dependency scan: pip-audit + Safety + outdated packages (skip code scan)'
    )
    parser.add_argument(
        '--code',
        action='store_true',
        help='Code security scan only with Ruff (security + quality checks)'
    )
    
    args = parser.parse_args()
    
    # Find project root
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    
    # Run audit
    auditor = SecurityAuditor(project_root)
    return auditor.run_audit(
        deps_only=args.deps,
        code_only=args.code,
        quick=args.quick
    )


if __name__ == '__main__':
    sys.exit(main())
