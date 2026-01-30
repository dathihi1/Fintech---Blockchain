# 🤝 Contributing to Smart Trading Journal

Thank you for considering contributing! This document provides guidelines for contributing to the project.

## 🎯 How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports:
1. Check existing [Issues](https://github.com/your-username/smart-trading-journal/issues)
2. Use the latest version
3. Check if it's already fixed in `main` branch

**Good Bug Report Includes:**
- Clear title and description
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- System info (OS, Python version, Node version)
- Error logs/stack traces

**Template:**
```markdown
## Bug Description
Brief description here

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: Windows 11 / Ubuntu 22.04 / macOS 13
- Python: 3.12
- Node: 20.0.0
- Docker: 24.0.0

## Logs
```
paste error logs here
```
```

### ✨ Suggesting Features

**Before Submitting:**
- Check if feature already exists
- Check if someone already suggested it
- Make sure it fits project scope

**Good Feature Request:**
```markdown
## Feature Description
What feature do you want?

## Use Case
Why is this useful?

## Possible Implementation
How might this work? (optional)

## Alternatives
Other solutions you've considered
```

### 💻 Code Contributions

#### Setup Development Environment

```bash
# Fork and clone
git clone https://github.com/YOUR-USERNAME/smart-trading-journal.git
cd smart-trading-journal

# Create branch
git checkout -b feature/amazing-feature

# Setup environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install

# Run tests before making changes
cd ../backend
pytest tests/
```

#### Code Style

**Python (Backend):**
- Follow PEP 8
- Use type hints
- Docstrings for all functions/classes
- Max line length: 100 characters

```python
def analyze_sentiment(text: str, model: str = "finbert") -> dict:
    """Analyze sentiment of trading note.
    
    Args:
        text: Trading note text
        model: Model name to use
        
    Returns:
        Dict with sentiment scores
    """
    # implementation
    pass
```

**JavaScript (Frontend):**
- Use ESLint configuration
- Use modern ES6+ features
- PropTypes for React components

```javascript
const TradeCard = ({ trade, onUpdate }) => {
  // component code
};

TradeCard.propTypes = {
  trade: PropTypes.object.isRequired,
  onUpdate: PropTypes.func.isRequired,
};
```

#### Testing

**Backend Tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/test_nlp.py -v  # Specific file
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

**Add Tests for New Features:**
- Unit tests for new functions
- Integration tests for new endpoints
- Update existing tests if behavior changes

#### Commit Messages

Use conventional commits format:

```
type(scope): brief description

Detailed explanation of what and why

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting, no code change
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
feat(nlp): add emotion detection for Vietnamese text

fix(api): correct sentiment score calculation
Fixes #42

docs(readme): update installation instructions

test(trades): add integration tests for CRUD operations
```

## 🔄 Pull Request Process

### 1. Before Submitting

- [ ] Code follows style guidelines
- [ ] Added/updated tests
- [ ] All tests pass
- [ ] Updated documentation
- [ ] No merge conflicts with `main`

### 2. PR Description Template

```markdown
## Description
What does this PR do?

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass

## Related Issues
Fixes #123
Relates to #456
```

### 3. Review Process

1. Maintainer will review within 1-2 days
2. Address feedback and update PR
3. Once approved, maintainer will merge
4. Delete your branch after merge

## 📁 Project Structure

```
backend/
├── api/          # FastAPI endpoints - add new routes here
├── analyzers/    # Analysis logic - trading analysis algorithms
├── core/         # Core config - auth, settings
├── ml/           # ML models - NLP, behavioral analysis
├── models/       # Database models - SQLAlchemy ORM
├── nlp/          # NLP engine - text processing
├── services/     # Business logic - reusable services
└── tests/        # Test files - mirror structure

frontend/
├── src/
│   ├── components/  # Reusable UI components
│   ├── pages/       # Page components
│   ├── services/    # API client
│   └── hooks/       # Custom React hooks
```

## 🎨 Adding New Features

### Backend Endpoint

1. Create route in `api/`
2. Add business logic in `services/`
3. Update database models if needed
4. Add tests in `tests/`
5. Update API docs

**Example:**
```python
# backend/api/analytics.py
from fastapi import APIRouter, Depends
from services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/performance")
async def get_performance(
    user: User = Depends(get_current_user)
):
    """Get trading performance metrics."""
    service = AnalyticsService()
    return await service.calculate_performance(user.id)
```

### Frontend Component

1. Create component in `components/`
2. Add to appropriate page
3. Update services if new API calls needed
4. Test in browser

**Example:**
```javascript
// frontend/src/components/PerformanceChart.jsx
import React from 'react';
import { Line } from 'recharts';

const PerformanceChart = ({ data }) => {
  return (
    <Line data={data} />
  );
};

export default PerformanceChart;
```

## 🧪 Testing Guidelines

### Write Tests For:

- New API endpoints
- New business logic
- Bug fixes
- Complex algorithms

### Test Structure:

```python
# backend/tests/test_new_feature.py
import pytest
from api.new_feature import new_function

def test_new_function_success():
    """Test successful case."""
    result = new_function("valid_input")
    assert result == expected_output

def test_new_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        new_function("invalid_input")
```

## 📝 Documentation

Update documentation when:
- Adding new features
- Changing existing behavior
- Adding configuration options
- Fixing complex bugs

**Files to Update:**
- `README.md` - Overview, features list
- `SETUP_GUIDE.md` - Installation steps
- API docstrings - Code documentation
- `docs/` folder - Detailed guides

## 🚀 Release Process

Maintainers only:

1. Update version in `package.json` and `pyproject.toml`
2. Update CHANGELOG.md
3. Create release tag: `git tag v1.2.3`
4. Push tag: `git push origin v1.2.3`
5. Create GitHub release with notes

## ❓ Questions?

- 📖 Check [README.md](README.md)
- 🔍 Search [existing issues](https://github.com/your-username/smart-trading-journal/issues)
- 💬 Create new [discussion](https://github.com/your-username/smart-trading-journal/discussions)

## 🎉 Recognition

Contributors will be:
- Listed in README.md
- Thanked in release notes
- Added to GitHub contributors

Thank you for contributing! 🙏
