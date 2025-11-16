# Contributing to StickerCraft

Thank you for your interest in contributing to StickerCraft! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
   ```bash
   git clone https://github.com/YOUR_USERNAME/stikky.git
   cd stikky
   ```
3. **Create a branch** for your changes
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed setup instructions.

### Quick Start

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
flutter pub get
flutter run
```

## Code Style

### Python (Backend)
- Follow PEP 8 style guide
- Use type hints where possible
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions and classes

Example:
```python
async def generate_sticker(
    prompt: str,
    style: str = "cartoon"
) -> List[Dict]:
    """
    Generate sticker from text prompt.

    Args:
        prompt: Text description of desired sticker
        style: Visual style preset

    Returns:
        List of generated sticker variants
    """
    # Implementation
```

### Dart (Frontend)
- Follow Dart style guide
- Use `flutter analyze` to check for issues
- Format code with `dart format`
- Use meaningful widget names
- Keep widgets small and focused

Example:
```dart
class StickerCard extends StatelessWidget {
  final String imageUrl;
  final VoidCallback onTap;

  const StickerCard({
    super.key,
    required this.imageUrl,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // Implementation
  }
}
```

## Testing

### Backend Tests
```bash
cd backend
pytest
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
flutter test
flutter test --coverage
```

## Commit Messages

Use conventional commit format:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(api): add character expression endpoint

Add new endpoint for generating character expressions
with pose control using ControlNet.

Closes #123
```

```
fix(export): resolve WhatsApp size limit issue

Reduce image quality incrementally when file size
exceeds 100KB limit for WhatsApp static stickers.
```

## Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** if applicable
5. **Submit PR** with clear description

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Screenshots (if applicable)

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
```

## Feature Requests

Submit feature requests as GitHub issues with:
- Clear use case description
- Expected behavior
- Any relevant mockups/designs

## Bug Reports

Submit bugs with:
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, versions)
- Screenshots/logs if applicable

## Code Review

All submissions require review. We'll look for:
- Code quality and style
- Test coverage
- Documentation
- Performance impact
- Security considerations

## License

By contributing, you agree that your contributions will be licensed under the project's license.

## Questions?

Feel free to open an issue for any questions or clarifications needed.

---

Thank you for contributing to StickerCraft! 🎨
