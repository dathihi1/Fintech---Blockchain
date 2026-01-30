"""
Verify project is ready for GitHub deployment
"""
import os
import sys
from pathlib import Path

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_mark(passed):
    return f"{GREEN}✓{RESET}" if passed else f"{RED}✗{RESET}"

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  {text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def check_file_exists(filepath, description):
    exists = os.path.exists(filepath)
    status = check_mark(exists)
    print(f"{status} {description}: {filepath}")
    return exists

def check_file_not_exists(filepath, description):
    not_exists = not os.path.exists(filepath)
    status = check_mark(not_exists)
    print(f"{status} {description}: {filepath}")
    return not_exists

def check_gitignore_contains(pattern):
    gitignore_path = ".gitignore"
    if not os.path.exists(gitignore_path):
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return pattern in content

def main():
    print_header("GitHub Deployment Verification")
    
    all_passed = True
    
    # 1. Documentation Files
    print_header("1. Documentation Files")
    checks = [
        ("README.md", "Main README"),
        ("SETUP_GUIDE.md", "Setup Guide"),
        ("QUICKSTART.md", "Quick Start"),
        ("LICENSE", "License File"),
        ("CONTRIBUTING.md", "Contributing Guide"),
        ("backend/.env.example", "Environment Template"),
    ]
    
    for filepath, desc in checks:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 2. Security - No sensitive files
    print_header("2. Security Check")
    sensitive_files = [
        ("backend/.env", "Environment file should NOT be committed"),
        (".env", "Root .env should NOT exist"),
    ]
    
    for filepath, desc in sensitive_files:
        if not check_file_not_exists(filepath, desc):
            all_passed = False
            print(f"   {YELLOW}⚠ Remove this file before pushing!{RESET}")
    
    # 3. .gitignore Configuration
    print_header("3. .gitignore Configuration")
    patterns = [
        "__pycache__",
        "*.pyc",
        "venv/",
        "node_modules/",
        ".env",
        "backend/.env",
        "backend/ml/models/finbert_trading_vi/",
        "backend/ml/models/*.pth",
        "*.log",
        ".vscode/",
    ]
    
    for pattern in patterns:
        if check_gitignore_contains(pattern):
            print(f"{GREEN}✓{RESET} .gitignore contains: {pattern}")
        else:
            print(f"{RED}✗{RESET} .gitignore missing: {pattern}")
            all_passed = False
    
    # 4. ML Models (should be excluded)
    print_header("4. ML Models Check")
    
    large_files = [
        "backend/ml/models/finbert_trading_vi",
        "backend/ml/models/feature_scaler.pkl",
    ]
    
    for filepath in large_files:
        if os.path.exists(filepath):
            if check_gitignore_contains(os.path.basename(filepath)):
                print(f"{GREEN}✓{RESET} {filepath} exists and is in .gitignore")
            else:
                print(f"{YELLOW}⚠{RESET} {filepath} exists but may not be ignored")
                all_passed = False
        else:
            print(f"{BLUE}ℹ{RESET} {filepath} not present (OK if not trained yet)")
    
    # 5. Dependencies
    print_header("5. Dependencies")
    dep_checks = [
        ("backend/requirements.txt", "Backend requirements"),
        ("frontend/package.json", "Frontend package.json"),
    ]
    
    for filepath, desc in dep_checks:
        if not check_file_exists(filepath, desc):
            all_passed = False
    
    # 6. Project Structure
    print_header("6. Project Structure")
    dirs = [
        "backend/api",
        "backend/models",
        "backend/ml",
        "backend/tests",
        "frontend/src",
        "frontend/src/components",
        "infrastructure",
        "scripts",
    ]
    
    for directory in dirs:
        if os.path.isdir(directory):
            print(f"{GREEN}✓{RESET} Directory exists: {directory}")
        else:
            print(f"{RED}✗{RESET} Directory missing: {directory}")
            all_passed = False
    
    # 7. Git Repository
    print_header("7. Git Repository")
    
    if os.path.exists(".git"):
        print(f"{GREEN}✓{RESET} Git repository initialized")
    else:
        print(f"{YELLOW}⚠{RESET} Git not initialized. Run: git init")
        all_passed = False
    
    # Summary
    print_header("Summary")
    
    if all_passed:
        print(f"{GREEN}✓ All checks passed! Ready to push to GitHub.{RESET}\n")
        print("Next steps:")
        print("1. git add .")
        print("2. git commit -m 'Initial commit'")
        print("3. git remote add origin YOUR_REPO_URL")
        print("4. git push -u origin main")
        return 0
    else:
        print(f"{RED}✗ Some checks failed. Fix issues before pushing.{RESET}\n")
        print("Review DEPLOYMENT.md for detailed instructions.")
        return 1

if __name__ == "__main__":
    try:
        os.chdir(Path(__file__).parent.parent)
        sys.exit(main())
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")
        sys.exit(1)
