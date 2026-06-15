# Notification E2E Suite

A comprehensive end-to-end testing suite for the MultiChannelNotifier backend system, featuring a React frontend application and Playwright-based automated tests.

## Project Structure

```
notification-e2e-suite/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # React UI components
│   │   ├── api/        # API client module (see frontend/src/api/README.md)
│   │   └── utils/      # Utility functions
│   ├── package.json
│   ├── .eslintrc.js    # ESLint configuration
│   └── .prettierrc      # Prettier configuration
├── tests/              # Playwright E2E test suite (Python)
│   ├── pages/          # Page Object Models
│   ├── unit/           # Unit tests
│   ├── property/       # Property-based tests
│   ├── e2e/            # End-to-end flow tests
│   ├── data/           # Test data files
│   └── README.md       # Test suite documentation
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── .prettierrc          # Prettier configuration (shared)
├── pyproject.toml       # Python project configuration (Black, Flake8)
├── pytest.ini           # Pytest configuration
└── .kiro/
    └── specs/          # Specification documents
```

## Technology Stack

**Frontend:**
- React 19+ with TypeScript
- Vite as build tool
- CSS Modules for styling
- Fetch API for HTTP requests
- ESLint for code quality
- Prettier for code formatting

**Testing:**
- Playwright (Python)
- pytest as test runner
- Hypothesis for property-based testing
- pytest-html for reporting
- Black for Python formatting
- Flake8 for Python linting

**Code Quality:**
- Pre-commit hooks for automated code quality checks
- ESLint for JavaScript/TypeScript linting
- Prettier for consistent code formatting
- Black for Python code formatting
- Flake8 for Python linting

## Prerequisites

Before setting up the project, ensure you have the following installed:

### System Requirements
- **Node.js**: Version 18 or higher ([download](https://nodejs.org/))
- **npm**: Version 8 or higher (comes with Node.js)
- **Python**: Version 3.10 or higher ([download](https://www.python.org/))
- **Git**: For version control ([download](https://git-scm.com/))
- **MultiChannelNotifier Backend**: Running on `http://localhost:8081`

### Verify Installation

```bash
# Check Node.js and npm
node --version    # Should be v18+
npm --version     # Should be v8+

# Check Python
python --version  # Should be 3.10+

# Check Git
git --version
```

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd notification-e2e-suite
```

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Optional: Install Git hooks (from project root)
cd ..
npm install -g pre-commit  # Or use: pip install pre-commit
pre-commit install
```

### 3. Test Suite Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (required for E2E tests)
playwright install

# Note: playwright install will download ~300MB of browser binaries
# This is a one-time setup step
```

## Running the Application

### Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

**Available npm commands:**
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint to check code quality
- `npm run format` - Format code with Prettier (if configured)

### Backend Requirements

Before running tests, ensure the MultiChannelNotifier backend is running:

```bash
# Backend should be accessible at
http://localhost:8081/api/v1/notifications
```

## Running Tests

### Quick Start

```bash
# Run all tests
pytest

# Run all tests with HTML report
pytest --html=tests/reports/test_report.html --self-contained-html
```

### Run Specific Test Categories

```bash
# Unit tests only (specific examples and edge cases)
pytest tests/unit/ -m unit_test

# Property-based tests only (universal properties with generated inputs)
pytest tests/property/ -m property_test

# E2E tests only (complete user flows)
pytest tests/e2e/ -m e2e_test
```

### Run with Specific Browser

```bash
# Chromium (default)
pytest --browser chromium

# Firefox
pytest --browser firefox

# WebKit
pytest --browser webkit
```

### Advanced Test Execution

```bash
# Run tests in headed mode (see browser window)
pytest --headed

# Run tests in parallel (faster execution)
pytest -n auto

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_form_rendering.py

# Run specific test function
pytest tests/unit/test_form_rendering.py::test_form_fields_render

# Run with specific number of parallel workers
pytest -n 4
```

### Test Reports

```bash
# Generate HTML report with screenshots
pytest --html=tests/reports/test_report.html --self-contained-html

# Generate report with custom path
pytest --html=custom_report.html --self-contained-html

# Run tests and show slowest 10 tests
pytest --durations=10
```

## Code Quality & Formatting

### Frontend Code Quality

```bash
cd frontend

# Lint code with ESLint
npm run lint

# Format code with Prettier (if script is available)
npm run format

# Lint and format together
npm run lint && npm run format

# Fix ESLint issues automatically (where possible)
npx eslint . --fix
```

### Python Code Quality

```bash
# Format Python code with Black
black tests/

# Lint Python code with Flake8
flake8 tests/

# Format and lint together
black tests/ && flake8 tests/

# Format specific file
black tests/conftest.py

# Check formatting without modifying files
black --check tests/
```

### Pre-commit Hooks (Automated Code Quality)

Pre-commit hooks automatically run code quality checks before each commit:

```bash
# Install pre-commit hooks (run once after cloning)
pip install pre-commit
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run eslint --all-files

# Bypass hooks (not recommended)
git commit --no-verify
```

**Configured hooks:**
- ESLint for JavaScript/TypeScript files
- Prettier for code formatting
- Black for Python code formatting
- Flake8 for Python code linting

## Development Workflow

### Typical Development Cycle

1. **Start frontend and backend:**
   ```bash
   # Terminal 1: Start backend (if not already running)
   # Terminal 2: Start frontend
   cd frontend && npm run dev
   
   # Terminal 3: Run tests (watch mode)
   pytest --watch
   ```

2. **Make code changes**
   - Modify React components in `frontend/src/`
   - Modify tests in `tests/`

3. **Check code quality**
   ```bash
   # Frontend
   cd frontend && npm run lint
   
   # Tests
   black tests/ && flake8 tests/
   ```

4. **Run tests**
   ```bash
   # Run tests related to your changes
   pytest tests/unit/ --headed
   ```

5. **Commit changes**
   ```bash
   # Pre-commit hooks will automatically run checks
   git add .
   git commit -m "Describe your changes"
   ```

## Documentation

### Detailed Guides

- **[Test Suite Documentation](tests/README.md)** - Comprehensive guide to writing and running tests
- **[Testing Configuration Guide](TESTING_CONFIGURATION.md)** - Detailed test configuration
- **[Quick Start Testing](QUICK_START_TESTING.md)** - Quick reference for running tests
- **[API Client Documentation](frontend/src/api/README.md)** - How the frontend communicates with backend

### Specification Documents

- **[Requirements](/.kiro/specs/notification-e2e-suite/requirements.md)** - Complete feature requirements
- **[Design](/.kiro/specs/notification-e2e-suite/design.md)** - System design and architecture
- **[Implementation Tasks](/.kiro/specs/notification-e2e-suite/tasks.md)** - Implementation plan and tasks

## Troubleshooting

### Frontend Issues

#### Port 5173 already in use
```bash
# Kill process on port 5173
# On Windows (PowerShell)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# On macOS/Linux
lsof -i :5173
kill -9 <PID>

# Or use a different port
cd frontend && npm run dev -- --port 5174
```

#### Node modules corrupted or outdated
```bash
# Clean reinstall
cd frontend
rm -r node_modules package-lock.json
npm install
```

#### TypeScript compilation errors
```bash
# Check TypeScript version
npx tsc --version

# Rebuild type definitions
cd frontend
npx tsc --noEmit
```

#### ESLint errors when linting
```bash
# Check ESLint configuration
npx eslint --debug .

# Fix auto-fixable issues
npx eslint . --fix

# Show eslint version and plugins
npx eslint --version
```

### Testing Issues

#### Playwright browsers not found
```bash
# Reinstall Playwright browsers
playwright install

# Verify installation
playwright install-deps  # Install system dependencies

# Install specific browser
playwright install chromium
```

#### Tests fail with connection errors
```bash
# Check if backend is running
curl http://localhost:8081/api/v1/notifications

# Check if frontend is running
curl http://localhost:5173

# Common issues:
# - Backend on wrong port (should be 8081)
# - Frontend on wrong port (should be 5173)
# - Firewall blocking connections
```

#### pytest command not found
```bash
# Verify Python virtual environment is activated
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### Import errors in test files
```bash
# Add project root to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or use pytest with import mode
pytest --import-mode=importlib
```

#### Tests pass locally but fail in CI
```bash
# Run tests in headless mode (CI mode)
pytest --browser chromium

# Check environment variables
echo $PLAYWRIGHT_HEADLESS

# Run with same browser as CI
pytest --browser chromium --browser-channel chromium
```

#### Hypothesis tests are too slow
```bash
# Run with fewer examples
pytest tests/property/ --hypothesis-seed=0

# Run specific property test with verbose output
pytest tests/property/test_form_submission.py -v

# View Hypothesis database statistics
python -c "from hypothesis import settings; settings.print_stats()"
```

#### Screenshot capture not working
```bash
# Check screenshot directory permissions
ls -la tests/reports/

# Run with verbose screenshot info
pytest --verbose --capture=no

# Test screenshot manually
python -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.screenshot(path='test.png')
    browser.close()
"
```

### Python Environment Issues

#### Virtual environment issues
```bash
# Create fresh virtual environment
python -m venv .venv

# Activate it
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Reinstall requirements
pip install -r requirements.txt
```

#### Python version mismatch
```bash
# Check Python version
python --version

# Use specific Python version
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Code Quality Issues

#### Pre-commit hooks failing
```bash
# Run hooks manually to see errors
pre-commit run --all-files

# Fix issues and retry
black tests/
flake8 tests/

# Skip specific hook (not recommended)
pre-commit run --all-files --hook-stage=commit

# Uninstall hooks (if needed)
pre-commit uninstall
```

#### ESLint errors that won't fix
```bash
# Check for formatting conflicts between ESLint and Prettier
cd frontend
npm run lint -- --debug > eslint-debug.txt

# Disable specific ESLint rule temporarily
# Add comment above line:
// eslint-disable-next-line rule-name
```

#### Black and Flake8 conflicts
```bash
# Check line length configuration
cat pyproject.toml | grep line-length

# Format with Black then check with Flake8
black tests/
flake8 tests/ --max-line-length=100

# View specific file with line numbers
python -m py_compile tests/conftest.py
```

### Getting Help

If you encounter issues not covered in the troubleshooting section:

1. Check the [Test Suite Documentation](tests/README.md)
2. Review [TESTING_CONFIGURATION.md](TESTING_CONFIGURATION.md)
3. Check [Playwright documentation](https://playwright.dev/python/)
4. Review [pytest documentation](https://docs.pytest.org/)
5. Check [Hypothesis documentation](https://hypothesis.readthedocs.io/)

## CI/CD Integration

## Features

### Frontend Application

- **Notification Form**: Send notifications via EMAIL, SMS, or WHATSAPP
- **Notification Query**: View and filter notification history
- **Real-time Validation**: Client-side validation for all input fields
- **Error Handling**: Comprehensive error handling with user-friendly messages

### API Client Module

The frontend includes a robust API client module (`frontend/src/api/`) that handles all communication with the backend:

- Type-safe TypeScript interfaces
- Comprehensive error handling
- Silent failure for malformed responses
- Network error handling
- No authentication required

For detailed API client documentation, see [frontend/src/api/README.md](frontend/src/api/README.md)

### Test Suite

- **Page Object Models**: Maintainable test automation using POM pattern
- **Property-Based Testing**: Validates universal correctness properties with Hypothesis
- **Unit Tests**: Specific examples and edge cases
- **E2E Tests**: Complete user flow validation
- **HTML Reports**: Detailed test reports with screenshots
- **Multi-Browser Support**: Chromium, Firefox, and WebKit

## Backend Integration

The frontend communicates with the MultiChannelNotifier backend running on `http://localhost:8081`.

**API Endpoints:**
- `POST /api/v1/notifications` - Send notification
- `GET /api/v1/notifications` - Query notifications

Ensure the backend is running before testing the frontend or executing E2E tests.

## Documentation

- **Specifications**:
  - [Requirements](/.kiro/specs/notification-e2e-suite/requirements.md)
  - [Design](/.kiro/specs/notification-e2e-suite/design.md)
  - [Implementation Tasks](/.kiro/specs/notification-e2e-suite/tasks.md)

- **Testing**:
  - [Testing Configuration Guide](TESTING_CONFIGURATION.md)
  - [Quick Start Testing](QUICK_START_TESTING.md)
  - [Test Suite README](tests/README.md)

- **API**:
  - [API Client Documentation](frontend/src/api/README.md)

## Development

### Running the Frontend

```bash
cd frontend
npm run dev     # Development server
npm run build   # Production build
npm run preview # Preview production build
```

### Running Tests

```bash
# Run all tests with HTML report
pytest --html=reports/test_report.html

# Run tests in parallel (faster)
pytest -n auto

# Run with coverage
pytest --cov=tests --cov-report=html
```

### Code Quality

```bash
# Frontend
cd frontend
npm run lint    # ESLint
npm run format  # Prettier

# Tests
cd tests
black .         # Format Python code
flake8 .        # Lint Python code
```

## CI/CD Integration

The test suite is designed to run in CI/CD environments:

```bash
# Headless mode (default for CI)
PLAYWRIGHT_HEADLESS=1 pytest

# Generate artifacts for CI
pytest --html=reports/test_report.html --self-contained-html --json-report

# Run tests in parallel
pytest -n auto

# Set exit codes
# 0: All tests passed
# 1: One or more tests failed
# 3: Test collection error
# 5: No tests collected
```

Supported CI/CD platforms:
- GitHub Actions (`.github/workflows/e2e-tests.yml`)
- GitLab CI (`.gitlab-ci.yml`)
- Jenkins (`Jenkinsfile`)

## License

MIT
