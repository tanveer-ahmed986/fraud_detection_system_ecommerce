# Contributing to Fraud Detection System

Thank you for your interest in contributing! This project aims to be a production-grade, open-source fraud detection system for e-commerce platforms.

## 🌟 How to Contribute

### Reporting Bugs

1. **Search existing issues** to avoid duplicates
2. **Use the bug report template** when creating a new issue
3. **Include**:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. **Check the roadmap** and existing issues first
2. **Use the feature request template**
3. **Explain**:
   - The problem your feature solves
   - Proposed solution
   - Alternative solutions considered
   - Impact on existing functionality

### Pull Requests

#### Before You Start

1. **Fork the repository** and create a feature branch from `main`
2. **Check existing issues** - comment if you want to work on something
3. **For major changes**, open an issue first to discuss

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/fraud_detection_system.git
cd fraud_detection_system

# Install dependencies
cd backend
pip install -e ".[dev]"

cd ../frontend
npm install

# Start local development
docker-compose up
```

#### Code Standards

**Backend (Python)**
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Add tests for new features (pytest)
- Ensure async/await patterns are used correctly

**Frontend (TypeScript)**
- Follow TypeScript best practices
- Use functional components with hooks
- Maintain type safety - no `any` types
- Add comments for complex logic

**General**
- Keep commits atomic and well-described
- Write meaningful commit messages: `feat: add SHAP explainability` or `fix: resolve CORS issue`
- Update documentation for API changes
- Add tests for bug fixes

#### Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov

# Frontend tests
cd frontend
npm test

# Integration tests
docker-compose up -d
pytest tests/integration/
```

#### Pull Request Process

1. **Update documentation** if you change APIs or behavior
2. **Add tests** for new features or bug fixes
3. **Ensure all tests pass** locally before pushing
4. **Update CHANGELOG.md** with your changes
5. **Fill out the PR template** completely
6. **Link related issues** using keywords like "Fixes #123"

#### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated and passing
- [ ] No console errors or warnings
- [ ] CHANGELOG.md updated
- [ ] Backward compatibility maintained (or breaking change noted)

## 🏗️ Project Structure

```
fraud_detection_system/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── routers/     # API endpoints
│   │   ├── ml/          # ML models and training
│   │   ├── models/      # Database models
│   │   └── middleware/  # Rate limiting, etc.
│   ├── tests/           # Backend tests
│   └── scripts/         # Training scripts
├── frontend/            # React dashboard
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Page components
│   │   └── api/         # API client
├── plugin/              # WooCommerce plugin
└── docker/              # Docker configurations
```

## 📋 Development Workflow

1. **Create a branch**: `git checkout -b feat/my-feature`
2. **Make changes** and commit: `git commit -m "feat: add my feature"`
3. **Push to fork**: `git push origin feat/my-feature`
4. **Open Pull Request** against `main` branch
5. **Address review feedback** if requested
6. **Squash commits** if requested by maintainers

## 🧪 Testing Guidelines

- **Unit tests**: Test individual functions/components
- **Integration tests**: Test API endpoints end-to-end
- **Model tests**: Verify ML model performance metrics
- **Coverage**: Aim for >80% code coverage on new code

## 📝 Commit Message Format

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, no logic change)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Example: `feat: add SHAP force plot visualization`

## 🎯 Priority Areas

We especially welcome contributions in:

1. **Model improvements**: Better feature engineering, new algorithms
2. **Integrations**: Shopify, Magento, custom e-commerce platforms
3. **Documentation**: Tutorials, guides, API docs
4. **Testing**: Increase test coverage, add edge cases
5. **Performance**: Optimize inference latency, database queries
6. **UI/UX**: Dashboard enhancements, visualizations

## 💬 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Open a [GitHub Discussion](https://github.com/yourusername/fraud_detection_system/discussions)
- Check existing [issues](https://github.com/yourusername/fraud_detection_system/issues)
- Read the [documentation](README.md)

Thank you for contributing! 🎉
