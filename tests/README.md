# Notification E2E Test Suite

This directory contains the Playwright-based E2E test suite for the Notification React frontend application.

## Directory Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── pages/                      # Page Object Models
│   └── __init__.py
├── unit/                       # Unit tests for specific examples and edge cases
│   └── __init__.py
├── property/                   # Property-based tests using Hypothesis
│   └── __init__.py
├── e2e/                        # End-to-end user flow tests
│   └── __init__.py
├── data/                       # Test data files (JSON)
│   └── __init__.py
└── utils/                      # Test utilities and helpers
    └── __init__.py
```

## Prerequisites

- Python 3.8 or higher
- Node.js (for running the React frontend)
- MultiChannelNotifier backend running on http://localhost:8081

## Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Playwright browsers:
   ```bash
   playwright install
   ```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test categories
```bash
# Unit tests only
pytest tests/unit/

# Property-based tests only
pytest tests/property/

# E2E tests only
pytest tests/e2e/
```

### Run with specific browser
```bash
# Chromium (default)
pytest --browser chromium

# Firefox
pytest --browser firefox

# WebKit
pytest --browser webkit
```

### Run in headless mode
```bash
pytest --browser chromium
```

### Run in headed mode (see browser)
```bash
pytest --browser chromium --headed
```

### Generate HTML report
```bash
pytest --html=report.html --self-contained-html
```

### Run tests with specific markers
```bash
# Run only unit tests
pytest -m unit_test

# Run only property-based tests
pytest -m property_test

# Run only E2E tests
pytest -m e2e_test
```

## Test Markers

- `unit_test`: Unit tests for specific examples and edge cases
- `property_test`: Property-based tests using Hypothesis
- `e2e_test`: End-to-end user flow tests

## Configuration

Test configuration is managed in:
- `pytest.ini`: Pytest configuration (test discovery, markers, default options)
- `pyproject.toml`: Project metadata and tool configuration
- `conftest.py`: Shared fixtures and test setup

## Writing Tests

### Unit Tests

Unit tests verify specific examples and edge cases:

```python
import pytest

@pytest.mark.unit_test
async def test_specific_scenario(notification_page):
    await notification_page.navigate()
    # Test implementation
```

### Property-Based Tests

Property-based tests use Hypothesis to verify universal properties:

```python
from hypothesis import given, strategies as st
import pytest

@given(
    notification_type=st.sampled_from(['EMAIL', 'SMS', 'WHATSAPP']),
    recipient=st.emails()
)
@pytest.mark.property_test
async def test_property(notification_page, notification_type, recipient):
    # Test implementation
```

### E2E Tests

E2E tests verify complete user flows:

```python
import pytest

@pytest.mark.e2e_test
async def test_user_flow(notification_page):
    await notification_page.navigate()
    # Test implementation
```

## Troubleshooting

### Playwright browsers not found
Run `playwright install` to download browser binaries.

### Tests fail with connection errors
Ensure the React frontend is running on http://localhost:3000 and the backend is running on http://localhost:8081.

### Import errors
Ensure all dependencies are installed: `pip install -r requirements.txt`

## CI/CD Integration

The test suite supports CI/CD environments:

```bash
# Run in headless mode with exit codes
pytest --browser chromium --html=report.html --self-contained-html
```

Exit codes:
- 0: All tests passed
- 1: One or more tests failed

## Code Quality

### Linting
```bash
flake8 tests/
```

### Formatting
```bash
black tests/
```
