# Testing Configuration Guide

## Overview

This document describes the pytest and Playwright configuration for the Notification E2E Test Suite.

## Configuration Files

### pytest.ini

The main pytest configuration file that defines:
- Test discovery patterns
- Test markers (unit_test, property_test, e2e_test)
- Default command-line options
- Browser engine selection
- HTML report generation
- Screenshot capture settings

### tests/conftest.py

Pytest fixtures and hooks that provide:
- Browser context configuration
- Automatic screenshot capture
- Test data fixtures
- Cleanup hooks

## Browser Engines

The test suite supports three browser engines:

1. **Chromium** (default) - Google Chrome/Microsoft Edge engine
2. **Firefox** - Mozilla Firefox engine
3. **WebKit** - Safari engine

### Running Tests with Different Browsers

```bash
# Run with Chromium (default)
pytest

# Run with Firefox
pytest --browser firefox

# Run with WebKit
pytest --browser webkit

# Run with multiple browsers
pytest --browser chromium --browser firefox --browser webkit
```

## Headless vs Headed Mode

### Headless Mode (Default)

Tests run without a visible browser window. This is the default mode and is suitable for CI/CD environments.

```bash
# Run in headless mode (default)
pytest
```

### Headed Mode

Tests run with a visible browser window. Useful for debugging and development.

```bash
# Run in headed mode
pytest --headed
```

## HTML Report Generation

HTML reports are automatically generated after each test run using pytest-html.

### Report Location

- **Path**: `reports/test_report.html`
- **Format**: Self-contained HTML (includes all CSS and JavaScript inline)

### Report Contents

- Test execution summary (pass/fail counts)
- Execution time for each test
- Detailed error messages and stack traces for failures
- Test markers and metadata

### Viewing Reports

```bash
# Run tests and generate report
pytest

# Open report in browser (Windows)
start reports/test_report.html

# Open report in browser (Linux/Mac)
open reports/test_report.html
```

## Screenshot Capture

Screenshots are automatically captured for **all tests** (both passing and failing) after test execution.

### Screenshot Location

- **Directory**: `reports/screenshots/`
- **Naming**: `{test_name}.png`

### Screenshot Configuration

- **Resolution**: 1280x720 (configured in conftest.py)
- **Format**: PNG
- **Timing**: Captured after each test completes

### Disabling Screenshots

To disable automatic screenshots, modify `tests/conftest.py` and remove or comment out the `auto_screenshot` fixture.

## Test Markers

The test suite uses three markers to categorize tests:

### 1. unit_test

Unit tests for specific examples and edge cases.

```python
@pytest.mark.unit_test
def test_email_validation():
    # Test code here
    pass
```

Run only unit tests:
```bash
pytest -m unit_test
```

### 2. property_test

Property-based tests using Hypothesis.

```python
@pytest.mark.property_test
def test_form_submission_property():
    # Test code here
    pass
```

Run only property tests:
```bash
pytest -m property_test
```

### 3. e2e_test

End-to-end user flow tests.

```python
@pytest.mark.e2e_test
def test_email_notification_flow():
    # Test code here
    pass
```

Run only E2E tests:
```bash
pytest -m e2e_test
```

### Running Multiple Marker Categories

```bash
# Run unit and property tests
pytest -m "unit_test or property_test"

# Run everything except E2E tests
pytest -m "not e2e_test"
```

## Common Test Commands

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/unit/test_validation.py
```

### Run Specific Test Function

```bash
pytest tests/unit/test_validation.py::test_email_validation
```

### Run Tests in Parallel

```bash
pytest -n auto
```

Note: Requires `pytest-xdist` plugin.

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Show Print Statements

```bash
pytest -s
```

### Run Tests with Coverage

```bash
pytest --cov=tests --cov-report=html
```

Note: Requires `pytest-cov` plugin.

## CI/CD Configuration

### Headless Mode for CI

The default configuration runs in headless mode, which is suitable for CI/CD environments.

```yaml
# Example GitHub Actions configuration
- name: Run tests
  run: pytest
```

### Generating Artifacts

```yaml
# Example GitHub Actions configuration
- name: Run tests
  run: pytest

- name: Upload test reports
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: test-reports
    path: reports/
```

## Troubleshooting

### Issue: Browser not found

**Solution**: Install Playwright browsers:
```bash
playwright install
```

### Issue: Screenshots not captured

**Solution**: Ensure the `reports/screenshots/` directory exists and has write permissions.

### Issue: HTML report not generated

**Solution**: Ensure the `reports/` directory exists and has write permissions. Check that `pytest-html` is installed:
```bash
pip install pytest-html
```

### Issue: Tests fail with "viewport" error

**Solution**: Ensure the `browser_context_args` fixture in `conftest.py` is properly configured.

## Advanced Configuration

### Custom Viewport Size

Edit `tests/conftest.py`:

```python
@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},  # Custom size
    }
```

### Enable Video Recording

Edit `tests/conftest.py`:

```python
@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": "reports/videos",  # Enable video recording
    }
```

### Custom Screenshot Timing

Modify the `auto_screenshot` fixture in `tests/conftest.py` to capture screenshots at different times (e.g., only on failure).

## References

- [Playwright Python Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
- [pytest-html Plugin](https://github.com/pytest-dev/pytest-html)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
