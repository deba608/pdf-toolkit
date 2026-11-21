# Contributing to PDF Toolkit

Thank you for your interest in contributing! This document outlines the process and standards for contributing to PDF Toolkit.

## Code of Conduct

By participating, you agree to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please be respectful and inclusive.

## How to Contribute

### Reporting Bugs

1. **Search** existing [issues](https://github.com/deba608/pdf-toolkit/issues) first
2. **Create** a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots/logs if applicable
   - Environment: OS, Python version, PDF Toolkit version

### Suggesting Features

1. **Check** [discussions](https://github.com/deba608/pdf-toolkit/discussions) for similar ideas
2. **Open** a feature request issue with:
   - Use case / problem statement
   - Proposed solution
   - Alternatives considered
   - Mockups (if UI-related)

### Pull Requests

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feat/your-feature-name`
3. **Make** your changes following our standards
4. **Test** thoroughly (see Testing section)
5. **Commit** with conventional commit messages
6. **Push** to your fork
7. **Open** a Pull Request against `main`

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/pdf-toolkit.git
cd pdf-toolkit

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run application
python -m src.main
```

## Code Standards

### Python Style

- **Formatter**: Black (line length 100)
- **Linter**: Ruff (replaces flake8, isort, etc.)
- **Type Checking**: mypy (strict mode)
- **Docstrings**: Google style for public APIs

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[scope]: <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`

**Examples**:
```
feat(merge): add custom output filename option
fix(encrypt): handle empty owner password correctly
docs: update USER_GUIDE with watermark workflow
refactor(core): extract command pattern for undo/redo
test(pdf_engine): add split_by_pages edge cases
```

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<short-description>` | `feat/batch-processing` |
| Bugfix | `fix/<short-description>` | `fix/preview-crash-large-pdf` |
| Docs | `docs/<short-description>` | `docs/update-readme-screenshots` |
| Refactor | `refactor/<short-description>` | `refactor/command-pattern` |
| Test | `test/<short-description>` | `test/merge-edge-cases` |

## Testing

### Running Tests

```bash
# All tests
pytest -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# UI tests (requires display)
pytest tests/ui/ -v

# With coverage
pytest --cov=src --cov-report=html --cov-report=term
```

### Writing Tests

- **Unit tests**: Test individual functions/classes in isolation
- **Integration tests**: Test complete workflows (merge → save → reopen)
- **UI tests**: Use pytest-qt for widget testing
- **Fixtures**: Use `tests/conftest.py` for shared fixtures

```python
# Example unit test
def test_merge_preserves_page_count(tmp_path):
    pdf1 = create_test_pdf(tmp_path / "a.pdf", pages=3)
    pdf2 = create_test_pdf(tmp_path / "b.pdf", pages=2)
    
    result = PdfEngine.merge([pdf1, pdf2], tmp_path / "merged.pdf")
    
    assert result.page_count == 5
```

### Test Data

- Use `tests/fixtures/` for sample PDFs
- Generate test PDFs programmatically in tests (fast, reproducible)
- Large test files: add to `.gitignore`, generate in CI

## Architecture Guidelines

### Adding a New Tool

1. **Engine**: Add method to `src/core/pdf_engine.py`
2. **Model**: Add any new data classes to `src/core/models.py`
3. **UI Panel**: Add panel in `src/ui/widgets/tool_panels.py`
4. **Register**: Add to `ToolPanelsStack.panels` dict
5. **Menu**: Add action in `MainWindow._setup_menu()`
6. **Tests**: Add unit + integration tests

### Command Pattern (Undo/Redo)

All mutating operations should use the Command pattern:

```python
# src/core/commands.py
class Command(ABC):
    @abstractmethod
    def execute(self) -> PdfFile: ...
    @abstractmethod
    def undo(self) -> PdfFile: ...
```

### Threading

- All PDF operations **must** run in `QThreadPool` via `QRunnable`
- Never block the main (GUI) thread
- Use `WorkerSignals` for progress/result/error communication

## Documentation

- **README.md**: Project overview, install, quick start
- **docs/USER_GUIDE.md**: Comprehensive user manual
- **docs/ARCHITECTURE.md**: Technical architecture (if needed)
- **Code comments**: Public APIs must have docstrings
- **Type hints**: Required for all public functions

## Release Process

Maintainers only:

1. Update version in `src/__version__.py`
2. Update `CHANGELOG.md`
3. Create git tag: `git tag -a v1.2.0 -m "Release v1.2.0"`
4. Push tag: `git push origin v1.2.0`
5. GitHub Actions builds and creates release
6. Verify artifacts on all platforms

## Getting Help

- **Questions**: [GitHub Discussions](https://github.com/deba608/pdf-toolkit/discussions)
- **Bugs**: [GitHub Issues](https://github.com/deba608/pdf-toolkit/issues)
- **Security**: [Security Policy](https://github.com/deba608/pdf-toolkit/security/policy)

## Recognition

Contributors are recognized in:
- `AUTHORS.md` (all contributors)
- Release notes (significant contributions)
- README (regular contributors)

---

*Thank you for contributing to PDF Toolkit!*