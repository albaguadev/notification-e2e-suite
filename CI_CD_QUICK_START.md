# CI/CD Quick Start Guide

This guide provides quick setup instructions for running the E2E test suite in CI/CD environments.

## Quick Facts

- **Headless Mode**: Enabled by default (no display needed)
- **Exit Codes**: Standard pytest behavior (0 = success, 1 = failure)
- **Artifacts**: HTML reports + screenshots in `tests/reports/`
- **Parallel**: Run tests with `-n auto` for parallel execution
- **Browsers**: Support for Chromium, Firefox, WebKit

## 5-Minute Setup

### 1. GitHub Actions (Recommended for GitHub)

Already configured in `.github/workflows/e2e-tests.yml`

Just push to main/develop/feature branches:

```bash
git push origin feature/my-feature
```

Tests will run automatically ✨

### 2. GitLab CI

Already configured in `.gitlab-ci.yml`

Just push to repository:

```bash
git push origin feature/my-feature
```

Check pipeline in GitLab UI → CI/CD → Pipelines

### 3. Jenkins

Already configured in `Jenkinsfile`

Configure new pipeline job:

1. Create new Pipeline job in Jenkins
2. Set SCM to your Git repository
3. Set Pipeline script from SCM → Jenkinsfile
4. Save and build

## Running Tests Locally (CI Mode)

```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest-xdist

# Install Playwright browsers
playwright install

# Run in CI/CD mode (headless)
PLAYWRIGHT_HEADLESS=1 pytest

# Run in parallel (faster)
PLAYWRIGHT_HEADLESS=1 pytest -n auto

# Run specific browser
PLAYWRIGHT_HEADLESS=1 pytest --browser firefox
```

## Command Reference

### Basic Commands

```bash
# All tests, single browser (Chromium)
pytest

# All tests, parallel (auto-detect workers)
pytest -n auto

# All tests, specific worker count
pytest -n 4

# Unit tests only
pytest tests/unit/

# Property tests only
pytest tests/property/

# E2E tests only
pytest tests/e2e/
```

### Generate Reports

```bash
# Generate HTML report with embedded screenshots
pytest --html=report.html --self-contained-html

# Specify browser in report name
pytest --browser firefox --html=report_firefox.html --self-contained-html

# With timing information
pytest --durations=10 --html=report.html
```

### Multi-Browser Testing

```bash
# Run on all browsers sequentially
pytest --browser chromium --html=chromium.html --self-contained-html
pytest --browser firefox --html=firefox.html --self-contained-html
pytest --browser webkit --html=webkit.html --self-contained-html

# Or use matrix in CI/CD (see configurations)
```

## Artifact Locations

All test artifacts are saved to `tests/reports/`:

```
tests/reports/
├── test_report_chromium.html    # HTML report with screenshots
├── test_report_firefox.html
├── test_report_webkit.html
├── property_report.html          # Property-based tests report
├── parallel_report.html          # Parallel execution report
└── screenshots/
    ├── test_email_notification_flow_passed.png
    ├── test_sms_notification_flow_failed.png
    └── ...
```

### View Reports

- **Local**: Open `tests/reports/test_report.html` in browser
- **GitHub Actions**: Download artifact from workflow run
- **GitLab CI**: Download from job artifacts or view in Reports section
- **Jenkins**: View in HTML Report Publisher

## Environment Variables

Key environment variables for CI/CD:

```bash
# Enable headless mode (required for CI/CD)
PLAYWRIGHT_HEADLESS=1

# Mark as running in CI environment
CI=true

# Python version (if needed)
PYTHON_VERSION=3.11

# Number of parallel workers
PARALLEL_WORKERS=4
```

## Exit Codes

- **0**: All tests passed ✅
- **1**: One or more tests failed ❌
- **2**: Test execution error ⚠️
- **5**: No tests collected ⚠️

## Performance Tips

### Fastest Configuration

```bash
# 4-8 workers (depending on available CPU cores)
# Chromium browser (fastest)
# Headless mode (default)
PLAYWRIGHT_HEADLESS=1 pytest -n 4 --browser chromium
```

### Expected Times

- Single worker, Chromium: 2-3 minutes
- 4 workers, Chromium: 30-45 seconds
- All browsers, single worker: 6-9 minutes

## Troubleshooting

### "No tests collected"

```bash
# Check if test files exist
ls tests/
ls tests/unit/
ls tests/property/
ls tests/e2e/

# Run with verbose output
pytest -v
```

### Tests fail locally but pass in CI

Usually means environment difference:

```bash
# Run exactly as CI would
export PLAYWRIGHT_HEADLESS=1
export CI=true
pytest -n auto --browser chromium
```

### Artifacts not generated

```bash
# Check if tests are actually running
pytest -v

# Manually create reports directory
mkdir -p tests/reports

# Ensure pytest-html is installed
pip install pytest-html

# Try with explicit report path
pytest --html=tests/reports/report.html --self-contained-html
```

### Parallel execution issues

```bash
# Try with fewer workers
pytest -n 2

# Try without parallel
pytest

# With verbose output
pytest -n 4 -v
```

## Example CI/CD Workflows

### GitHub Actions Example

```yaml
- name: Run tests
  run: |
    pytest \
      --browser chromium \
      --html=tests/reports/report.html \
      --self-contained-html \
      -n auto
  env:
    PLAYWRIGHT_HEADLESS: "1"
```

### GitLab CI Example

```yaml
test_job:
  script:
    - pytest --browser chromium --html=tests/reports/report.html --self-contained-html -n auto
  variables:
    PLAYWRIGHT_HEADLESS: "1"
  artifacts:
    paths:
      - tests/reports/
```

### Jenkins Example

```groovy
stage('Test') {
    steps {
        sh '''
            export PLAYWRIGHT_HEADLESS=1
            pytest --browser chromium --html=tests/reports/report.html --self-contained-html -n auto
        '''
    }
}
```

## Next Steps

1. **Check Requirements.md**: Understand what's being tested
2. **Read Design.md**: Learn the architecture
3. **Read CI_CD_CONFIGURATION.md**: Detailed configuration guide
4. **Run tests locally**: `pytest` or `PLAYWRIGHT_HEADLESS=1 pytest -n auto`
5. **Push to repository**: Trigger CI/CD pipeline

## FAQ

**Q: How do I skip certain tests?**
```bash
pytest -m "not slow"
```

**Q: How do I run a single test?**
```bash
pytest tests/unit/test_email_validation.py::test_valid_email_format
```

**Q: How do I increase parallelism?**
```bash
pytest -n 8  # Use 8 workers instead of 4
```

**Q: How do I see browser UI (headed mode)?**
```bash
# Local only
pytest --headed --browser firefox
```

**Q: Can I run tests on my machine as CI/CD would?**
```bash
export PLAYWRIGHT_HEADLESS=1
export CI=true
pytest -n auto --browser chromium
```

## Support

For detailed information, see:
- **CI_CD_CONFIGURATION.md**: Full CI/CD configuration details
- **README.md**: Project overview and setup
- **pytest.ini**: Pytest configuration
- **pyproject.toml**: Project dependencies

Happy testing! 🚀
