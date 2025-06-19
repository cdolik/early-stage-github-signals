# Contributing to Early-Stage GitHub Signals

Thank you for your interest in contributing to the Early-Stage GitHub Signals project! This document provides guidelines and best practices to ensure the project remains clean and well-maintained.

## Repository Hygiene Checklist

### Code Quality
- [ ] All Python code follows PEP 8 style guidelines
- [ ] JavaScript follows project's ESLint configuration
- [ ] Functions and classes have proper docstrings
- [ ] No unused imports or dead code
- [ ] No hardcoded secrets or credentials

### Git Practices
- [ ] Commit messages are descriptive and follow conventional commits format
- [ ] Feature branches are used for all changes
- [ ] PRs are small and focused on a single change
- [ ] Large binary files are not committed to the repository
- [ ] Sensitive or generated files are in .gitignore

### Documentation
- [ ] README.md is up-to-date with current functionality
- [ ] Code changes include corresponding documentation updates
- [ ] Important design decisions are documented

### Testing
- [ ] New features include appropriate tests
- [ ] All tests pass before submitting a PR
- [ ] No regression in test coverage

### Dependencies
- [ ] Dependencies are explicitly specified in requirements.txt
- [ ] Development dependencies are in requirements-dev.txt
- [ ] Dependencies are regularly updated via Dependabot

## Pull Request Process

1. Ensure your code follows the style guidelines
2. Update documentation as necessary
3. Include tests for new functionality
4. Make sure all tests pass
5. Submit a PR with a clear description of the changes

## Development Setup

See the [DEVELOPER_SETUP.md](docs/DEVELOPER_SETUP.md) document for detailed instructions on setting up your development environment.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT license.
