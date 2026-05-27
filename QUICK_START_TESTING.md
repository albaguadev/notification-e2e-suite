# Quick Start: Running Tests

## Prerequisites

1. Activate the virtual environment:
   ```bash
   # Windows
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source .venv/bin/activate
   ```

2. Ensure Playwright browsers are installed:
   ```bash
   playwright install
   ```

## Basic Test Commands

### Run All Tests (Default: Chromium, Headless)
```bash
pytest
```

### Run Tests in Headed Mode (See Browser)
```bash
pytest --headed
```

### Run Tests with Specific Browser
```bash
# Firefox
pytest --browser firefox

# WebKit (Safari)
pytest --browser webkit

# Multiple browsers
pytest --browser chromium --browser firefox --browser webkit
```

### Run Tests by Marker
```bash
# Unit tests only
pytest -m unit_test

# Property-based tests only
pytest -m property_test

# E2E tests only
pytest -m e2e_test

# Multiple markers
pytest -m "unit_test or property_test"
```

### Run Specific Test File
```bash
pytest tests/unit/test_validation.py
```

### Run Specific Test Function
```bash
pytest tests/unit/test_validation.py::test_email_validation
```

## Test Reports

### HTML Report
- **Location**: `reports/test_report.html`
- **Generated**: Automatically after each test run
- **Contents**: Test results, execution times, error details

### Screenshots
- **Location**: `reports/screenshots/`
- **Captured**: Automatically for all tests (pass or fail)
- **Format**: PNG files named after test functions

## Common Scenarios

### Debug a Failing Test
```bash
# Run in headed mode with verbose output
pytest tests/unit/test_validation.py::test_email_validation --headed -v -s
```

### Run Tests Quickly (Skip Screenshots)
```bash
# Modify conftest.py to disable auto_screenshot fixture
# Or run specific tests without the fixture
```

### Generate Coverage Report
```bash
# Install pytest-cov first: pip install pytest-cov
pytest --cov=tests --cov-report=html
```

### Run Tests in Parallel
```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest -n auto
```

## Troubleshooting

### Browser Not Found
```bash
playwright install
```

### Permission Denied on Reports Directory
```bash
# Windows
Remove-Item -Recurse -Force reports
mkdir reports

# Linux/Mac
rm -rf reports
mkdir reports
```

### Tests Hanging
- Check if frontend is running on http://localhost:3000
- Check if backend is running on http://localhost:8081
- Use `--headed` mode to see what's happening

## Configuration Files

- **pytest.ini**: Main pytest configuration
- **tests/conftest.py**: Fixtures and hooks
- **pyproject.toml**: Project dependencies and settings

For detailed configuration options, see [TESTING_CONFIGURATION.md](TESTING_CONFIGURATION.md).
