# Code Quality: Linting and Formatting

This document describes the code quality tools and configurations used in the Notification E2E Suite project.

## Overview

The project implements comprehensive code quality checks across JavaScript/TypeScript and Python code:

### JavaScript/TypeScript
- **ESLint**: Static code analysis for JavaScript/TypeScript
- **Prettier**: Code formatter for consistent code style

### Python
- **Black**: Code formatter for Python
- **Flake8**: Style guide enforcement and error checking
- **isort**: Python import sorting

### Automated
- **Pre-commit Hooks**: Automatic code quality checks before each commit

## Installation

### 1. Install Frontend Dependencies

```bash
cd frontend
npm install
```

This installs:
- ESLint (^10.3.0)
- Prettier (^3.0.0)
- All required plugins

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Black (>=23.0.0)
- Flake8 (>=6.0.0)
- isort (>=5.13.0)
- pre-commit (>=3.0.0)

### 3. Install Pre-commit Hooks

```bash
pre-commit install
```

This sets up automatic code quality checks before each commit.

## Configuration Files

### Frontend Configuration

#### `.prettierrc` (Root and frontend/)
Controls code formatting style:
- **Line length**: 100 characters
- **Quotes**: Single quotes
- **Trailing commas**: ES5 style
- **Semicolons**: True
- **Tab width**: 2 spaces

#### `eslint.config.js` (frontend/)
ESLint configuration with:
- TypeScript support
- React hooks plugin
- React refresh plugin
- Recommended rules

#### `.prettierignore` (Root and frontend/)
Files to exclude from Prettier formatting

### Python Configuration

#### `pyproject.toml`
Contains Black and isort configuration:

```toml
[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311"]

[tool.flake8]
max-line-length = 100
extend-ignore = ["E203", "W503"]
```

### Pre-commit Configuration

#### `.pre-commit-config.yaml`
Defines hooks that run automatically before commits:
- ESLint for JavaScript/TypeScript files
- Prettier for code formatting
- Black for Python formatting
- Flake8 for Python linting
- isort for import sorting
- YAML validation
- JSON validation
- File ending checks
- Trailing whitespace removal

## Usage

### Frontend Code Quality

#### Check Code with ESLint

```bash
cd frontend
npm run lint
```

Output example:
```
✖ 2 problems (2 errors, 0 warnings)
  2 errors and 0 warnings potentially fixable with the --fix option
```

#### Fix ESLint Issues Automatically

```bash
cd frontend
npx eslint . --fix
```

This fixes auto-fixable issues like:
- Unused imports
- Indentation
- Quote style

#### Format Code with Prettier

```bash
cd frontend
npm run format
```

This formats all code according to `.prettierrc` rules.

#### Check Formatting Without Modifying

```bash
cd frontend
npm run format:check
```

### Python Code Quality

#### Format Python Code with Black

```bash
# Format all Python files
black tests/

# Format specific file
black tests/conftest.py

# Check without modifying
black --check tests/
```

#### Lint Python Code with Flake8

```bash
# Lint all Python files
flake8 tests/

# Lint specific file
flake8 tests/conftest.py

# Show specific error codes
flake8 tests/ --show-source
```

#### Sort Python Imports

```bash
# Sort imports in all files
isort tests/

# Sort specific file
isort tests/conftest.py

# Check without modifying
isort --check-only tests/
```

#### Combined Python Quality Check

```bash
# Format and lint
black tests/ && isort tests/ && flake8 tests/
```

### Pre-commit Hooks

#### Run Hooks Manually

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run eslint --all-files
pre-commit run black --all-files
pre-commit run flake8 --all-files

# Run hooks in verbose mode
pre-commit run --all-files --verbose
```

#### Skip Hooks (Not Recommended)

```bash
# Skip hooks for a single commit
git commit --no-verify

# Bypass specific hook temporarily
SKIP=eslint git commit -m "message"
```

#### Uninstall Hooks

```bash
pre-commit uninstall
```

## Integrated Development Workflow

### Before Committing

1. **Format your code**:
   ```bash
   cd frontend && npm run format
   black tests/
   isort tests/
   ```

2. **Check for issues**:
   ```bash
   cd frontend && npm run lint
   flake8 tests/
   ```

3. **Fix auto-fixable issues**:
   ```bash
   cd frontend && npx eslint . --fix
   black tests/
   isort tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Your message"
   ```

Pre-commit hooks will run automatically and prevent the commit if there are issues.

### Example Commit Flow

```bash
# Make changes
echo "export const greeting = 'hello';" > frontend/src/greeting.ts

# Check code quality
cd frontend && npm run lint
# ESLint error: quotes should be double

# Fix automatically
npx eslint . --fix

# Format with Prettier
npm run format

# Try to commit
git add .
git commit -m "Add greeting export"

# Pre-commit hooks run automatically
# - ESLint check ✓
# - Prettier format ✓
# - Commit successful ✓
```

## Common Issues and Solutions

### Issue: ESLint Won't Fix All Errors

Some ESLint errors can't be auto-fixed. You need to fix them manually:

```bash
# Run ESLint with verbose output
npx eslint . --format=detailed

# Read the error description and fix manually
# Example: "Unexpected console statement"
# Solution: Remove the console.log statement
```

### Issue: Prettier and ESLint Conflicts

Sometimes Prettier formatting conflicts with ESLint rules:

```bash
# Check what Prettier would change
npx prettier --check .

# Format with Prettier
npx prettier --write .

# Re-run ESLint to verify
npx eslint .
```

### Issue: Black and Flake8 Conflicts

Black's formatting may trigger Flake8 line-length warnings. Configuration in `pyproject.toml` handles this:

```toml
[tool.black]
line-length = 100

[tool.flake8]
max-line-length = 100  # Must match Black's line-length
```

### Issue: Pre-commit Hooks Failing

If a hook fails during commit:

1. **Review the error output**:
   ```bash
   pre-commit run --all-files --verbose
   ```

2. **Fix the issues**:
   - ESLint: `npx eslint . --fix`
   - Prettier: `npx prettier --write .`
   - Black: `black tests/`
   - Flake8: Fix manually based on error
   - isort: `isort tests/`

3. **Add fixed files and retry**:
   ```bash
   git add .
   git commit -m "Your message"
   ```

### Issue: Node Modules Not Installed

```bash
# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install

# Verify ESLint is installed
npx eslint --version
```

### Issue: Python Virtual Environment Issues

```bash
# Create fresh virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Pre-commit Not Running

```bash
# Check if hooks are installed
cat .git/hooks/pre-commit

# Reinstall hooks
pre-commit install

# Test hooks manually
pre-commit run --all-files
```

## IDE Integration

### VS Code (ESLint and Prettier)

1. Install extensions:
   - ESLint (Microsoft)
   - Prettier - Code formatter (Prettier)

2. Create `.vscode/settings.json`:
   ```json
   {
     "editor.formatOnSave": true,
     "editor.defaultFormatter": "esbenp.prettier-vscode",
     "[javascript]": {
       "editor.defaultFormatter": "esbenp.prettier-vscode"
     },
     "[typescript]": {
       "editor.defaultFormatter": "esbenp.prettier-vscode"
     },
     "[json]": {
       "editor.defaultFormatter": "esbenp.prettier-vscode"
     },
     "eslint.enable": true,
     "eslint.alwaysShowStatus": true,
     "eslint.validate": ["javascript", "typescript"]
   }
   ```

3. Restart VS Code

### VS Code (Python)

1. Install extensions:
   - Python (Microsoft)
   - Pylance (Microsoft)

2. Create `.vscode/settings.json`:
   ```json
   {
     "[python]": {
       "editor.formatOnSave": true,
       "editor.defaultFormatter": "ms-python.python"
     },
     "python.formatting.provider": "black",
     "python.linting.enabled": true,
     "python.linting.flake8Enabled": true,
     "python.linting.pylintEnabled": false,
     "python.linting.mypyEnabled": false
   }
   ```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Lint Frontend
  run: |
    cd frontend
    npm run lint

- name: Format Check
  run: |
    cd frontend
    npm run format:check

- name: Lint Python
  run: |
    flake8 tests/
    black --check tests/
```

### GitLab CI

```yaml
lint:frontend:
  script:
    - cd frontend && npm run lint

format:check:
  script:
    - cd frontend && npm run format:check

lint:python:
  script:
    - flake8 tests/
    - black --check tests/
```

### Pre-commit in CI

```bash
# Install pre-commit
pip install pre-commit

# Run all hooks
pre-commit run --all-files

# Fail if any hook fails (exit code 1)
```

## Best Practices

1. **Run linting before committing**:
   - Catch issues early
   - Prevent bad code from entering the repository

2. **Use consistent code style**:
   - Makes code reviews easier
   - Improves code readability
   - Reduces cognitive load

3. **Keep configuration files updated**:
   - Review ESLint/Flake8 rules periodically
   - Update tool versions in package.json and requirements.txt
   - Document any custom rules

4. **Enable IDE integration**:
   - Get immediate feedback while coding
   - Fix issues as you type
   - Improve productivity

5. **Run tools in pre-commit hooks**:
   - Automatic enforcement of code quality
   - Prevents committing bad code
   - Team-wide consistency

## Troubleshooting Commands

```bash
# Verify tools are installed
cd frontend && npx eslint --version && npx prettier --version
black --version && flake8 --version && isort --version

# Run all quality checks
cd frontend && npm run lint && npm run format:check
black --check tests/ && flake8 tests/ && isort --check tests/

# Fix all auto-fixable issues
cd frontend && npx eslint . --fix && npm run format
black tests/ && isort tests/

# Test pre-commit hooks
pre-commit run --all-files --verbose

# Clear cache and reinstall
cd frontend && rm -rf node_modules package-lock.json && npm install
rm -rf .venv && python -m venv .venv && pip install -r requirements.txt
```

## Additional Resources

- [ESLint Documentation](https://eslint.org/docs/rules/)
- [Prettier Documentation](https://prettier.io/docs/en/index.html)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Pre-commit Documentation](https://pre-commit.com/)

## Quick Reference

### Frontend

```bash
# Check issues
npm run lint

# Fix issues
npx eslint . --fix

# Format code
npm run format

# Check formatting
npm run format:check
```

### Python

```bash
# Check issues
flake8 tests/

# Format code
black tests/

# Sort imports
isort tests/

# Check without modifying
black --check tests/ && isort --check tests/
```

### Pre-commit

```bash
# Install hooks
pre-commit install

# Run all hooks
pre-commit run --all-files

# Skip hooks (not recommended)
git commit --no-verify
```
