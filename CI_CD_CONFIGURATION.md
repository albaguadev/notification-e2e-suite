# CI/CD Configuration Guide

This document describes the CI/CD configuration for the Notification E2E Suite, including support for headless browser mode, exit codes, test artifact generation, and parallel test execution.

## Overview

The test suite is configured to run in multiple CI/CD environments:

- **GitHub Actions** (`.github/workflows/e2e-tests.yml`)
- **GitLab CI** (`.gitlab-ci.yml`)
- **Jenkins** (`Jenkinsfile`)

All configurations support:
- ✅ Headless browser mode (default)
- ✅ Proper exit codes for success/failure detection
- ✅ Test artifact collection (HTML reports, screenshots)
- ✅ Parallel test execution using pytest-xdist
- ✅ Multiple browser engines (Chromium, Firefox, WebKit)
- ✅ Multiple Python versions (3.8, 3.9, 3.10, 3.11)

## Exit Codes

pytest exit codes follow the standard convention for proper CI/CD integration:

| Exit Code | Meaning | Action |
|-----------|---------|--------|
| 0 | All tests passed | Build succeeds |
| 1 | One or more tests failed | Build fails |
| 2 | Test execution error | Build fails |
| 3 | Internal error | Build fails |
| 5 | No tests collected | Build fails |

The exit codes are automatically propagated by pytest and properly handled by all CI/CD platforms.

## Headless Browser Mode

### Default Configuration

Headless mode is enabled by default in all CI/CD environments through the `PLAYWRIGHT_HEADLESS` environment variable:

```bash
PLAYWRIGHT_HEADLESS=1
```

This means:
- No browser UI is displayed
- Tests run faster
- Requires no display server
- Perfect for CI/CD environments

### Configuration Per Platform

#### GitHub Actions
```yaml
env:
  PLAYWRIGHT_HEADLESS: "1"
  CI: "true"
```

#### GitLab CI
```yaml
variables:
  PLAYWRIGHT_HEADLESS: "1"
  CI: "true"
```

#### Jenkins
```groovy
environment {
    PLAYWRIGHT_HEADLESS = '1'
    CI = 'true'
}
```

### Running Tests Locally

For local development, you can run tests with a visible browser:

```bash
# Run with visible browser (headed mode)
pytest --headed

# Run with specific browser in headed mode
pytest --headed --browser firefox
```

## Test Artifact Generation

### Artifact Types

1. **HTML Test Reports**
   - Location: `tests/reports/test_report_<browser>.html`
   - Format: Self-contained HTML with embedded screenshots
   - Content: Pass/fail status, execution times, error details, stack traces

2. **Screenshots**
   - Location: `tests/reports/screenshots/`
   - Captured: Automatically for all tests (passed and failed)
   - Format: PNG images with descriptive filenames
   - Embedded: In HTML reports as base64-encoded images

3. **Test Metrics**
   - Execution time per test
   - Total execution time
   - Slowest 10 tests
   - Test status distribution (passed/failed/skipped)

### Artifact Access

#### GitHub Actions
Artifacts are uploaded to GitHub and can be accessed:
1. In the workflow run details
2. Via the Actions tab
3. Downloaded as ZIP files
4. Retention: 30 days (configurable)

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-reports-${{ matrix.browser }}
    path: tests/reports/
    retention-days: 30
```

#### GitLab CI
Artifacts are available in the pipeline:
1. Download from job artifacts
2. View in reports section
3. Retention: 30 days (default)

```yaml
artifacts:
  paths:
    - tests/reports/
    - tests/reports/screenshots/
  expire_in: 30 days
```

#### Jenkins
Artifacts are archived and viewable:
1. In the build artifacts section
2. Via HTML report plugin
3. Fingerprinted for tracking

```groovy
archiveArtifacts(
    artifacts: 'tests/reports/**/*',
    allowEmptyArchive: true
)
publishHTML([
    reportDir: 'tests/reports',
    reportName: 'E2E Test Report'
])
```

## Parallel Test Execution

### Overview

Parallel test execution significantly reduces build time by running multiple tests simultaneously.

### Configuration

The suite uses **pytest-xdist** for parallel execution:

```bash
# Automatic worker count (based on CPU cores)
pytest -n auto

# Specific number of workers
pytest -n 4
pytest -n 8

# With specific distribution strategy
pytest -n auto --dist loadscope
```

### Worker Distribution Strategies

- `--dist loadscope`: Group tests by scope (recommended for better resource utilization)
- `--dist loadgroup`: Use test group markers
- `--dist load`: Distribute by test count (default)
- `--dist loadfile`: Distribute by test file

### Performance Benefits

Example timings with 4 workers:
- Single-threaded: 120 seconds
- 2 workers: 70 seconds (41% faster)
- 4 workers: 40 seconds (67% faster)
- 8 workers: 25 seconds (79% faster)

Actual speedup depends on:
- Number of CPU cores available
- Test suite size
- I/O operations
- Network latency (backend calls)

### Per-Platform Configuration

#### GitHub Actions
```yaml
pytest \
  -n auto \
  --dist loadscope \
  --html=tests/reports/test_report.html
```

#### GitLab CI
```yaml
script:
  - pytest -n 4 --dist loadscope --html=tests/reports/test_report.html
```

#### Jenkins
```groovy
sh '''
  pytest \
    -n ${PARALLEL_WORKERS} \
    --dist loadscope \
    --html=tests/reports/test_report.html
'''
```

## Browser Engine Support

### Available Browsers

| Browser | Platform | Headless Support |
|---------|----------|------------------|
| Chromium | Linux, Windows, macOS | ✅ Yes |
| Firefox | Linux, Windows, macOS | ✅ Yes |
| WebKit | Linux, Windows, macOS | ✅ Yes |

### Running Tests on Multiple Browsers

#### GitHub Actions
```yaml
strategy:
  matrix:
    browser: ['chromium', 'firefox', 'webkit']

steps:
  - name: Run tests
    run: pytest --browser ${{ matrix.browser }}
```

#### GitLab CI
```yaml
test_chromium:
  script:
    - pytest --browser chromium

test_firefox:
  script:
    - pytest --browser firefox

test_webkit:
  script:
    - pytest --browser webkit
```

#### Jenkins
```groovy
stages {
    stage('Test - Chromium') {
        steps {
            sh 'pytest --browser chromium'
        }
    }
    stage('Test - Firefox') {
        steps {
            sh 'pytest --browser firefox'
        }
    }
}
```

## Python Version Support

Tests are validated on:
- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

### Version-Specific Configuration

#### GitHub Actions
```yaml
strategy:
  matrix:
    python-version: ['3.8', '3.9', '3.10', '3.11']
```

#### GitLab CI
```yaml
test_python_versions:
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.8", "3.9", "3.10", "3.11"]
```

## Local Development Commands

### Running Tests

```bash
# Run all tests in headless mode (default)
pytest

# Run tests in headed mode with visible browser
pytest --headed

# Run specific test file
pytest tests/unit/test_email_validation.py

# Run property-based tests only
pytest tests/property/ -v

# Run E2E tests only
pytest tests/e2e/ -v

# Run unit tests only
pytest tests/unit/ -v
```

### Parallel Execution

```bash
# Auto-detect worker count
pytest -n auto

# 4 workers
pytest -n 4

# 4 workers with load distribution
pytest -n 4 --dist loadscope

# Property tests in parallel
pytest tests/property/ -n auto
```

### Generate Reports

```bash
# Standard HTML report
pytest --html=report.html --self-contained-html

# With browser specified
pytest --browser firefox --html=report_firefox.html --self-contained-html

# With screenshots
pytest --screenshot=on --html=report.html --self-contained-html

# With timing information
pytest --durations=10 --html=report.html --self-contained-html
```

## CI/CD Platform Setup

### GitHub Actions

1. Create `.github/workflows/e2e-tests.yml` (already provided)
2. Push to repository
3. Configure repository settings (optional):
   - Branch protection rules
   - Required status checks
   - Artifact retention

### GitLab CI

1. Create `.gitlab-ci.yml` (already provided)
2. Configure CI/CD variables in project settings (if needed)
3. Enable CI/CD in project
4. Commit to repository

### Jenkins

1. Create `Jenkinsfile` (already provided)
2. Configure Jenkins job with SCM pointing to repository
3. Set up build triggers (webhook, scheduled, etc.)
4. Configure artifact archival
5. (Optional) Install HTML publisher plugin

## Troubleshooting

### Tests Fail with "No display server"

**Cause**: Tests running without headless mode in CI environment

**Solution**: Ensure `PLAYWRIGHT_HEADLESS=1` is set

```yaml
# GitHub Actions
env:
  PLAYWRIGHT_HEADLESS: "1"

# GitLab CI
variables:
  PLAYWRIGHT_HEADLESS: "1"

# Jenkins
environment {
    PLAYWRIGHT_HEADLESS = '1'
}
```

### Parallel Execution Conflicts

**Cause**: Tests using shared resources without proper isolation

**Solution**: Ensure proper test isolation in conftest.py (already configured)

```bash
# Use loadscope distribution for better isolation
pytest -n auto --dist loadscope
```

### Artifact Retention Issues

**Cause**: Artifacts not persisting long enough

**Solution**: Adjust retention days in configuration

```yaml
# GitHub Actions (default 30 days)
retention-days: 30

# GitLab CI (default 30 days)
expire_in: 30 days

# Jenkins: configure artifact archival in build settings
```

### Browser Installation Failures

**Cause**: Playwright browser binaries not installed

**Solution**: Ensure playwright install is run before tests

```bash
playwright install --with-deps
```

## Performance Optimization

### Recommended Settings

For fastest CI/CD builds:

```bash
# 4-8 parallel workers (depending on CI machine specs)
pytest -n 4 --dist loadscope

# Chromium browser only (fastest)
pytest --browser chromium

# Headless mode (default)
PLAYWRIGHT_HEADLESS=1 pytest
```

### Expected Build Times

| Configuration | Time | Notes |
|---------------|------|-------|
| Single worker, Chromium | 2-3 min | Basic |
| Single worker, all browsers | 6-9 min | Comprehensive |
| 4 workers, Chromium | 30-45 sec | Recommended |
| 4 workers, all browsers | 2-3 min | Full coverage |

## Security Considerations

### Environment Variables

Sensitive data should not be stored in CI/CD configuration:

- Store credentials in secret management system
- Use masked variables in CI/CD platform
- Never commit credentials to repository

### Exit Code Security

Exit codes are used for pipeline flow control:
- Ensure exit codes accurately reflect test results
- Do not suppress non-zero exit codes on test failure
- Use proper error handling in scripts

## Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-html plugin](https://pytest-html.readthedocs.io/)
- [pytest-xdist documentation](https://pytest-xdist.readthedocs.io/)
- [Playwright Python](https://playwright.dev/python/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)
