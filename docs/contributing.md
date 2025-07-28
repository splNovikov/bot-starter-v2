# 🤝 Contributing to Telegram Bot Starter

Thank you for considering contributing to this project! This guide will help you get started with contributing effectively.

## 🚀 Quick Start

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/amazing-feature`
3. **Make changes** following the architecture patterns
4. **Update documentation** if needed
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push to branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**

## 📋 Development Guidelines

### Code Quality Standards

- **Follow SOLID principles** - Each class should have a single responsibility
- **Update documentation** - Keep docs in sync with code changes
- **Use type hints** - All functions should have proper type annotations
- **Follow existing patterns** - Study existing code before implementing new features

### Architecture Compliance

- **Respect layer boundaries** - Business layer can depend on Core, but not vice versa
- **Use dependency injection** - Services should be easily mockable for testing
- **Follow localization-first design** - All user-facing text must use the `t()` function
- **Implement proper error handling** - Use structured exception handling with logging

### Code Style

- **Python 3.11+ features** - Use modern Python constructs
- **Descriptive naming** - Variables and functions should be self-documenting
- **Consistent formatting** - Follow existing code style
- **Meaningful comments** - Explain complex business logic

## 🧪 Testing (Future Enhancement)

**Note**: Comprehensive testing framework is planned for future releases. Current implementation focuses on clean architecture that supports easy testing when implemented.

### Planned Test Categories

1. **Unit Tests** - Individual functions and classes
2. **Integration Tests** - Component interactions  
3. **Localization Tests** - Multi-language functionality verification

## 📚 Documentation Standards

### Required Documentation

When contributing, ensure you update:

- **Code docstrings** - All public functions must have docstrings
- **README updates** - If adding major features
- **Architecture docs** - For core framework changes
- **Localization files** - Add translations for new user-facing text

### Documentation Format

```python
async def my_function(param1: str, user: User) -> str:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of the parameter
        user: Telegram user object for localization
        
    Returns:
        Localized response string
        
    Raises:
        ValueError: When param1 is invalid
        ServiceError: When external service fails
    """
```

## 🌍 Localization Contributions

### Adding New Languages

1. **Create locale file**: `locales/language_code.json`
2. **Follow existing structure** - Copy from `locales/en.json`
3. **Translate all keys** - Ensure complete coverage
4. **Test translations** - Verify parameter substitution works
5. **Update config** - Add to `SUPPORTED_LANGUAGES`

### Translation Guidelines

- **Maintain tone** - Keep the friendly, helpful tone
- **Preserve parameters** - Don't change `{parameter}` names
- **Consider length** - Telegram has message length limits
- **Cultural adaptation** - Adapt content for local culture when appropriate

## 🐛 Bug Reports

### Before Reporting

- **Search existing issues** - Check if already reported
- **Test with latest version** - Ensure bug still exists
- **Gather information** - Logs, steps to reproduce, environment

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '....'
3. See error

**Expected Behavior**
What you expected to happen

**Actual Behavior**
What actually happened

**Environment**
- Python version:
- aiogram version:
- OS:

**Logs**
```
Relevant log output
```
```

## ✨ Feature Requests  

### Before Requesting

- **Check existing features** - Might already exist
- **Consider architecture fit** - Should align with SOLID principles
- **Think about localization** - How will it work across languages

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Implementation**
How might this be implemented?

**Alternatives Considered**
Other solutions you've considered

**Localization Impact**
Will this require new translations?
```

## 🔧 Development Setup

### Prerequisites

- Python 3.11+
- Git
- Text editor or IDE

### Local Development

```bash
# Clone your fork
git clone https://github.com/yourusername/bot-starter-v2.git
cd bot-starter-v2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (when testing is implemented)
# pip install pytest pytest-cov pytest-asyncio

# Set up pre-commit hooks (optional)
# pip install pre-commit
# pre-commit install
```

### Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit with your bot token
# BOT_TOKEN=your_test_bot_token_here
```

## 📝 Commit Guidelines

### Commit Message Format

```
type(scope): description

Longer description if needed

Fixes #123
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```bash
feat(localization): add French language support

- Add locales/fr.json with complete translations
- Update configuration to include French
- Add tests for French language detection

Fixes #45

fix(handlers): resolve command alias registration issue

Commands with aliases were not being registered properly
with the aiogram router, causing them to fall through
to the default text handler.

Fixes #67
```

## 🎯 Areas Needing Help

### High Priority

- **Additional Languages** - Help translate to more languages
- **Testing Framework** - Implement comprehensive testing system  
- **Documentation** - Improve examples and tutorials
- **Performance** - Optimize hot paths and caching

### Medium Priority

- **New Features** - Weather service, reminders, etc.
- **Developer Tools** - Better debugging, profiling tools
- **CI/CD** - Automated deployment and quality checks

### Low Priority  

- **UI/UX** - Better inline keyboards and user interaction
- **Analytics** - Usage statistics and monitoring
- **Integrations** - Additional external service integrations

## 🏆 Recognition

### Contributors

All contributors will be recognized in:
- **README acknowledgments**
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions

### Types of Contributions

- **Code** - Features, bug fixes, optimizations
- **Documentation** - Guides, examples, API docs
- **Translation** - New languages and improvements
- **Quality Assurance** - Code review and standards compliance
- **Design** - Architecture improvements and patterns
- **Community** - Helping other users, issue triage

## 📞 Getting Help

### Channels

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - Questions and general discussion
- **Code Review** - Pull request feedback and suggestions

### Best Practices for Getting Help

- **Be specific** - Include relevant details and context
- **Show your work** - Share what you've tried
- **Follow up** - Let us know if solutions work
- **Help others** - Answer questions when you can

## 🎉 Thank You!

Your contributions make this project better for everyone. Whether it's a small bug fix, a new language translation, or a major feature - every contribution is valued and appreciated!

**Happy coding!** 🚀 