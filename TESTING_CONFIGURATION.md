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

HTML reports are automatically generated after each test run using pytest-html plugin.

### Report Location

- **Path**: `tests/reports/test_report.html`
- **Format**: Self-contained HTML (includes all CSS, JavaScript, and resources inline)
- **Access**: Open in any web browser, no additional dependencies needed

### Report Features

The generated HTML report includes:

1. **Summary Statistics**
   - Total test count
   - Pass/Fail/Skip counts
   - Pass rate percentage

2. **Execution Time Tracking**
   - Individual test execution time (milliseconds precision)
   - Total test suite execution time
   - Average test execution time
   - Top 10 slowest tests list
   - Execution time breakdown by test marker (unit_test, property_test, e2e_test)

3. **Detailed Test Results**
   - Pass/Fail status for all tests
   - Test name and node ID
   - Test markers displayed
   - Execution duration for each test
   - Test category classification

4. **Failure Information**
   - Detailed error messages for failed tests
   - Full stack traces with line numbers
   - Error type and exception information
   - Assertion details (when applicable)
   - Complete Python traceback output

5. **Screenshots**
   - Screenshots captured for all tests (both passing and failing)
   - Screenshot files embedded in report or linked
   - Screenshot naming includes test status (passed/failed)
   - Visual failure verification

6. **Environment Information**
   - Python version
   - Platform and OS information
   - Pytest version
   - Plugin versions
   - Report generation timestamp

### Report Generation Process

The report generation is automated via multiple pytest hooks in `tests/conftest.py`:

1. **pytest_configure** - Sets up report directories and configures HTML plugin
2. **pytest_runtest_setup** - Initializes execution metrics before each test
3. **pytest_runtest_makereport** - Captures execution time and failure details during test
4. **pytest_sessionfinish** - Calculates summary statistics after all tests complete

### Execution Time Tracking

The test suite tracks execution time using multiple mechanisms:

#### Per-Test Tracking
- `start_time`: Recorded via `pytest_runtest_setup` hook
- `end_time`: Recorded via `pytest_runtest_makereport` hook during "call" phase
- `duration`: Calculated as `end_time - start_time` in seconds
- Stored in `test_metrics` dictionary accessible throughout session

#### Session-Level Statistics
Calculated in `pytest_sessionfinish`:
- `total_duration`: Sum of all individual test durations
- `avg_duration`: Average duration across all tests
- `slowest_tests`: Top 10 tests sorted by duration descending
- Generated timestamp: ISO 8601 format

#### Durations Report
The `--durations=10` flag displays the 10 slowest tests:
```
========================== slowest 10 durations ==========================
5.23s call tests/e2e/test_email_notification_flow.py::test_email_flow
3.45s call tests/e2e/test_sms_notification_flow.py::test_sms_flow
...
```

### Viewing Reports

```bash
# Run tests and automatically generate report
pytest

# Open report in browser (Windows)
start tests/reports/test_report.html

# Open report in browser (Linux/Mac)
open tests/reports/test_report.html

# Open report in browser (Linux with xdg-open)
xdg-open tests/reports/test_report.html
```

### Report Customization

#### Custom Report Location

```bash
# Generate report at custom path
pytest --html=custom_path/report.html
```

Or modify `pytest.ini`:
```ini
addopts = --html=path/to/custom_report.html
```

#### Report Title

```bash
# Set custom report title
pytest --html=tests/reports/test_report.html --html-title "Custom Test Report"
```

#### Additional Report Options

```bash
# Show captured output in report
pytest --show-capture=all

# Include markers in report
pytest --capture=sys

# More verbose tracebacks
pytest --tb=long
```

### Error Messages and Stack Traces in Reports

When tests fail, the HTML report includes:

1. **Error Summary**
   - Exception type (e.g., AssertionError, TimeoutError)
   - Error message on a single line

2. **Full Traceback**
   - Complete Python traceback from exception
   - Each frame shows filename, line number, and code
   - Local variable values at each frame (when available)

3. **Captured Output**
   - stdout captured during test execution
   - stderr captured during test execution
   - Print statements from test code
   - Logging output (if configured)

4. **Assertion Details**
   - Original assertion that failed
   - Expected vs actual values
   - Comparison output for complex objects

### Screenshots in Reports

Screenshots are automatically captured for all tests via the `auto_screenshot` fixture in `tests/conftest.py`:

```python
@pytest.fixture(scope="function", autouse=True)
def auto_screenshot(page: Page, request):
    """Automatically capture screenshots for all tests"""
    yield
    
    # Screenshot captured after test completes
    # Named as: {test_name}_{status}.png
    # Stored in: tests/reports/screenshots/
```

Screenshot naming convention:
- `test_email_validation_passed.png` - Passed test
- `test_email_validation_failed.png` - Failed test
- `test_form_submission_passed.png` - Passed test

### Self-Contained Reports

The `--self-contained-html` flag ensures reports are fully self-contained:

- All CSS and JavaScript are embedded inline
- No external dependencies required
- Single HTML file can be shared via email or stored as artifact
- Works in any web browser without additional files

### CI/CD Integration

#### GitHub Actions Example

```yaml
- name: Run tests and generate report
  run: pytest

- name: Upload test reports
  uses: actions/upload-artifact@v3
  if: always()
  with:
    name: test-reports
    path: tests/reports/
    retention-days: 30

- name: Publish test report
  uses: daun/pytest-report-comment@v3
  if: always()
  with:
    pytest-html-report: tests/reports/test_report.html
```

#### GitLab CI Example

```yaml
test:
  script:
    - pytest
  artifacts:
    paths:
      - tests/reports/
    reports:
      junit: tests/reports/test_report.html
    when: always
    expire_in: 30 days
```

### Report Storage and Access

#### Local Development
- Reports stored in `tests/reports/` directory
- Accessible immediately after test execution
- Can be opened directly in browser

#### CI/CD Artifacts
- Reports stored as build artifacts
- Retention period configurable
- Downloadable from CI/CD platform
- Accessible after pipeline completion

#### Test History
- Each test run generates timestamped report
- Can be archived for historical comparison
- Useful for tracking test stability over time

### Advanced Report Configuration

#### Environment-Specific Reports

Create multiple pytest configurations for different environments:

**pytest-local.ini** (Development):
```ini
addopts = 
    --html=tests/reports/test_report.html
    --self-contained-html
    -v
```

**pytest-ci.ini** (CI/CD):
```ini
addopts = 
    --html=tests/reports/test_report_${BUILD_NUMBER}.html
    --self-contained-html
    -v
```

#### Conditional Screenshot Capture

Modify `auto_screenshot` fixture to capture only on failure:
```python
@pytest.fixture(scope="function", autouse=True)
def auto_screenshot(page: Page, request):
    yield
    
    # Only capture on failure
    test_id = request.node.nodeid
    test_status = test_metrics.get(test_id, {}).get('status')
    if test_status == 'failed':
        # Capture screenshot
```

### Troubleshooting Report Generation

## Screenshot Capture

Screenshots are automatically captured for **all tests** (both passing and failing) after test execution.

### Screenshot Location

- **Directory**: `tests/reports/screenshots/`
- **Naming Convention**: `{test_name}_{status}.png`
  - Example: `test_email_validation_passed.png`, `test_form_submission_failed.png`

### Screenshot Configuration

- **Resolution**: 1280x720 (configured in conftest.py)
- **Format**: PNG
- **Timing**: Captured after each test completes (via `auto_screenshot` fixture)
- **Coverage**: All tests (passed and failed)
- **Availability**: Stored locally and accessible in HTML report

### Screenshot Features

- **Automatic capture**: No manual configuration needed
- **Status tracking**: Screenshots named with pass/fail status
- **Integrated with reports**: Path stored in test metrics for report inclusion
- **Silent failures**: Screenshot capture failures don't affect test results
- **Storage**: Persistent local storage for review and analysis

### Disabling Screenshots

To disable automatic screenshots, modify `tests/conftest.py` and remove or comment out the `auto_screenshot` fixture:

```python
# Comment out or remove the entire auto_screenshot fixture
# @pytest.fixture(scope="function", autouse=True)
# def auto_screenshot(page: Page, request):
#     ...
```

### Viewing Screenshots

#### In HTML Report
Screenshots are referenced in the HTML report for easy access:
- Click on failed test for detailed failure information
- Screenshots may be embedded or linked in report

#### In File System
```bash
# View screenshots directory
ls tests/reports/screenshots/

# Open a specific screenshot
# Windows
start tests/reports/screenshots/test_email_validation_passed.png

# Linux/Mac
open tests/reports/screenshots/test_email_validation_passed.png
```

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

### Issue: HTML report not generated (see "Report Generation" section above for more details)

**Solution**: Ensure `pytest-html` is installed and configured:
```bash
pip install pytest-html>=4.1.0
```

### Issue: Screenshots not captured (see "Screenshot Capture" section above for more details)

**Solution**: Ensure the `tests/reports/screenshots/` directory exists and has write permissions:
```bash
mkdir -p tests/reports/screenshots/
chmod 755 tests/reports/screenshots/
```

### Issue: HTML report not generated

**Solution**: Ensure the `tests/reports/` directory exists and has write permissions. Check that `pytest-html` is installed:
```bash
pip install pytest-html>=4.1.0
```

### Issue: Tests fail with "viewport" error

**Solution**: Ensure the `browser_context_args` fixture in `conftest.py` is properly configured.

### Troubleshooting Report Generation

#### Issue: HTML report not generated

**Symptoms**: `pytest --html=...` command fails or no report file created

**Solutions**:
1. Verify pytest-html is installed:
   ```bash
   pip install pytest-html>=4.1.0
   ```

2. Check directory permissions:
   ```bash
   # Ensure tests/reports/ directory exists and is writable
   mkdir -p tests/reports/
   chmod 755 tests/reports/
   ```

3. Verify pytest configuration:
   ```bash
   pytest --co -q  # Verify pytest finds tests
   pytest --version  # Verify pytest version
   ```

#### Issue: Execution time not tracked correctly

**Symptoms**: Duration shows as 0 or N/A for tests

**Solutions**:
1. Verify conftest.py hooks are present:
   - `pytest_runtest_setup` should be defined
   - `pytest_runtest_makereport` should be defined
   - `pytest_sessionfinish` should be defined

2. Check for fixture conflicts that might prevent hooks from running

3. Verify system clock is accurate:
   ```bash
   date  # Check system time
   ```

#### Issue: Screenshots not captured

**Symptoms**: Screenshots directory exists but is empty after tests run

**Solutions**:
1. Verify auto_screenshot fixture is not disabled in conftest.py

2. Check page visibility - some tests may fail before screenshot capture

3. Ensure tests/reports/screenshots/ directory exists:
   ```bash
   mkdir -p tests/reports/screenshots/
   chmod 755 tests/reports/screenshots/
   ```

4. Verify no exceptions in auto_screenshot fixture:
   ```python
   # Add debugging (temporary)
   print(f"Capturing screenshot for {test_name}")
   ```

#### Issue: Stack traces incomplete in report

**Symptoms**: Failed test shows error message but no traceback

**Solutions**:
1. Increase traceback verbosity:
   ```bash
   pytest --tb=long
   ```

2. Verify pytest.ini has `--tb=short` (or appropriate level):
   ```ini
   addopts = --tb=short
   ```

3. Check for exceptions being caught and suppressed in test code

#### Issue: Report file is too large

**Symptoms**: HTML report file size is very large (>100MB)

**Solutions**:
1. Disable video recording if enabled:
   ```python
   "record_video_dir": None,  # in browser_context_args
   ```

2. Limit screenshot capture to failures only:
   ```python
   if test_status == 'failed':
       page.screenshot(...)
   ```

3. Disable screenshot capture entirely:
   ```python
   # Comment out auto_screenshot fixture
   ```

4. Use separate storage for screenshots:
   ```bash
   pytest --html=tests/reports/test_report.html --screenshot=on --screenshot-dir=/path/to/storage
   ```

#### Issue: Report styling looks broken

**Symptoms**: HTML report displays with missing CSS or misformatted layout

**Solutions**:
1. Verify --self-contained-html flag is set:
   ```bash
   pytest --self-contained-html
   ```

2. Try opening report with different browser (Chrome, Firefox, Safari)

3. Check browser JavaScript is enabled (Report uses JavaScript for interactivity)

4. Regenerate report:
   ```bash
   rm -rf tests/reports/test_report.html
   pytest
   ```

#### Issue: Report generation is slow

**Symptoms**: Tests complete quickly but report generation takes minutes

**Solutions**:
1. Reduce screenshot resolution:
   ```python
   page.screenshot(scale="device")  # Lower resolution
   ```

2. Disable video recording completely

3. Reduce test durations sampling:
   ```bash
   pytest --durations=5  # Show only 5 slowest tests
   ```

4. Consider separate report generation:
   ```bash
   # Run tests without HTML plugin, generate report separately
   pytest --no-html
   ```

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
        "record_video_dir": "tests/reports/videos",  # Enable video recording
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
