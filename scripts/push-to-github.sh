#!/bin/bash
# ============================================
# Smart Trading Journal - GitHub Push Script
# ============================================

echo ""
echo "========================================"
echo "  Smart Trading Journal"
echo "  GitHub Deployment"
echo "========================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")/.."

echo "[1/6] Checking Git status..."
git status
echo ""

echo "[2/6] Adding all files..."
git add .
echo ""

echo "[3/6] Checking what will be committed..."
git status
echo ""

read -p "Press Enter to continue..."
echo ""

echo "[4/6] Creating initial commit..."
git commit -m "Initial commit: Smart Trading Journal v1.0

Features:
- FastAPI backend with NLP sentiment analysis
- React frontend with Material-UI
- PostgreSQL database with Docker
- ML models for behavioral pattern detection
- Comprehensive documentation and setup guides
- Demo mode for easy testing
- Symbol autocomplete with Binance integration

Tech Stack:
- Backend: FastAPI, SQLAlchemy, PyTorch, Transformers
- Frontend: React, Vite, Material-UI
- Database: PostgreSQL 15
- NLP: FinBERT for sentiment analysis
- Testing: pytest, comprehensive test suite

Documentation:
- README.md with full setup guide
- QUICKSTART.md for 5-minute setup
- SETUP_GUIDE.md for detailed instructions
- DEPLOYMENT.md for GitHub deployment
- CONTRIBUTING.md for contributors
- PROJECT_SUMMARY.md with overview
"
echo ""

echo "[5/6] Setup remote repository..."
echo ""
echo "Please create a repository on GitHub first!"
echo "Repository name: smart-trading-journal"
echo "Description: AI-powered trading journal with NLP sentiment analysis"
echo ""

read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter repository name (default: smart-trading-journal): " REPO_NAME
REPO_NAME=${REPO_NAME:-smart-trading-journal}

REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "Repository URL: $REPO_URL"
echo ""

git remote add origin "$REPO_URL"
git branch -M main
echo ""

echo "[6/6] Pushing to GitHub..."
echo ""
git push -u origin main
echo ""

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "  SUCCESS!"
    echo "========================================"
    echo ""
    echo "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "Next steps:"
    echo "1. Visit your repository on GitHub"
    echo "2. Add description and topics"
    echo "3. Enable Issues and Discussions"
    echo "4. Add to your portfolio!"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  ERROR!"
    echo "========================================"
    echo ""
    echo "Something went wrong. Please check:"
    echo "1. GitHub repository exists"
    echo "2. You're logged in to GitHub"
    echo "3. Repository URL is correct"
    echo ""
    echo "Try manually:"
    echo "  git remote add origin $REPO_URL"
    echo "  git branch -M main"
    echo "  git push -u origin main"
    echo ""
fi

read -p "Press Enter to exit..."
