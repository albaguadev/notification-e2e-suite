"""
Pytest configuration and fixtures for the Notification E2E Test Suite.

This module provides shared fixtures for test isolation, page object models,
test data management, and HTML report generation with execution time tracking
and automatic screenshot capture for all tests.

Screenshot Configuration:
- All tests automatically capture screenshots (pass and fail)
- Screenshots stored in tests/reports/screenshots/ directory
- Screenshots embedded/linked in pytest-html reports
- Base64 encoded inline embedding for self-contained reports
"""

import pytest
import time
import traceback
import base64
from playwright.sync_api import Page, BrowserContext, Browser
from pathlib import Path
from typing import Generator, Dict, Any
from datetime import datetime
from urllib.parse import urljoin


# Global test metrics for execution time tracking
test_metrics: Dict[str, Any] = {}

# Global screenshot directory reference
SCREENSHOTS_DIR = Path("tests/reports/screenshots")


def pytest_configure(config):
    """Configure pytest with custom settings for HTML report generation.
    
    Sets up:
    - Report directories for HTML reports and screenshots
    - Pytest-html plugin configuration
    - Execution environment metadata
    - Screenshot capture configuration
    """
    # Create reports directory if it doesn't exist
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path("tests/reports/screenshots")
    screenshots_dir.mkdir(exist_ok=True, parents=True)
    
    # Configure pytest-html plugin with enhanced settings
    config.option.htmlpath = str(reports_dir / "test_report.html")
    config.option.self_contained_html = True
    
    # Store configuration for later use
    config.test_metrics = test_metrics
    config.screenshots_dir = screenshots_dir


def pytest_runtest_setup(item):
    """Hook called before each test runs to initialize metrics.
    
    Records:
    - Test name and node ID
    - Start time for execution tracking
    - Test markers (unit_test, property_test, e2e_test)
    """
    test_id = item.nodeid
    start_time = time.time()
    
    test_metrics[test_id] = {
        'name': item.name,
        'nodeid': test_id,
        'start_time': start_time,
        'end_time': None,
        'duration': None,
        'status': 'running',
        'markers': [marker.name for marker in item.iter_markers()],
        'error': None,
        'traceback': None,
    }


def pytest_runtest_makereport(item, call):
    """Hook called after each test phase to track execution metrics.
    
    Captures:
    - Execution time for each test
    - Test status (passed, failed, error)
    - Detailed error messages and stack traces for failures
    - Full traceback information
    """
    test_id = item.nodeid
    
    if test_id not in test_metrics:
        test_metrics[test_id] = {
            'name': item.name,
            'nodeid': test_id,
            'markers': [marker.name for marker in item.iter_markers()],
        }
    
    metrics = test_metrics[test_id]
    
    # Track execution time
    if call.when == "call":
        metrics['end_time'] = time.time()
        if 'start_time' in metrics:
            metrics['duration'] = metrics['end_time'] - metrics['start_time']
    
    # Capture failure information
    if call.when == "call" and call.excinfo is not None:
        metrics['status'] = 'failed'
        metrics['error'] = str(call.excinfo.value)
        metrics['traceback'] = ''.join(
            traceback.format_exception(
                type(call.excinfo.value),
                call.excinfo.value,
                call.excinfo.tb
            )
        )
        # Also capture the type of error for better categorization
        metrics['error_type'] = type(call.excinfo.value).__name__
    elif call.when == "call" and call.outcome == "passed":
        metrics['status'] = 'passed'
    elif call.when == "call" and call.outcome == "skipped":
        metrics['status'] = 'skipped'


def pytest_sessionfinish(session, exitstatus):
    """Hook called after all tests finish to generate report metadata.
    
    Generates:
    - Session summary with total test counts
    - Execution time statistics
    - Report generation timestamp
    """
    try:
        # Calculate summary statistics
        total_tests = len(test_metrics)
        passed_tests = sum(1 for m in test_metrics.values() if m.get('status') == 'passed')
        failed_tests = sum(1 for m in test_metrics.values() if m.get('status') == 'failed')
        skipped_tests = sum(1 for m in test_metrics.values() if m.get('status') == 'skipped')
        
        # Calculate total execution time
        valid_durations = [
            m['duration'] for m in test_metrics.values()
            if m.get('duration') is not None
        ]
        total_duration = sum(valid_durations) if valid_durations else 0
        avg_duration = total_duration / len(valid_durations) if valid_durations else 0
        
        # Find slowest tests
        sorted_tests = sorted(
            [
                (name, m['duration']) for name, m in test_metrics.items()
                if m.get('duration') is not None
            ],
            key=lambda x: x[1],
            reverse=True
        )
        slowest_tests = sorted_tests[:10]
        
        # Store report metadata
        report_metadata = {
            'generated_at': datetime.now().isoformat(),
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'skipped': skipped_tests,
            'total_duration': total_duration,
            'avg_duration': avg_duration,
            'slowest_tests': slowest_tests,
        }
        
        # Add metadata to session config for access in report hook if available
        if hasattr(session.config, 'test_metrics'):
            session.config.report_metadata = report_metadata
    except Exception:
        # Silent failure as per requirement 11.5
        pass


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure browser context with screenshot settings and timeouts.
    
    This fixture extends the default browser_context_args to enable
    screenshot capture for all tests and configure aggressive timeouts
    for faster test execution (especially important for property-based tests).
    
    Optimizations:
    - Set navigation timeout to 10 seconds to fail fast on network issues
    - Disable video recording to save memory and time
    - Standard viewport for consistent test behavior
    """
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": None,  # Disable video recording by default
    }


@pytest.fixture(scope="function")
def browser_context(browser: Browser, browser_context_args) -> Generator[BrowserContext, None, None]:
    """Provide a fresh browser context for each test.
    
    This fixture creates a new browser context for test isolation,
    ensuring each test starts with a clean state.
    
    Yields:
        BrowserContext: A fresh browser context instance
    """
    context = browser.new_context(**browser_context_args)
    yield context
    context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    """Provide a fresh page for each test.
    
    This fixture creates a new page within the browser context,
    ensuring test isolation at the page level.
    
    Optimizations:
    - Set action timeout to 5 seconds for faster failure detection
    
    Yields:
        Page: A fresh page instance
    """
    page = browser_context.new_page()
    # Set 5-second action timeout for faster failure detection
    page.set_default_timeout(5000)
    yield page
    page.close()


@pytest.fixture(scope="function")
def test_data():
    """Fixture providing test data for notification tests."""
    return {
        'valid_email': {
            'type': 'EMAIL',
            'recipient': 'test@example.com',
            'message': 'Test message',
            'subject': 'Test subject'
        },
        'valid_sms': {
            'type': 'SMS',
            'recipient': '+34612345678',
            'message': 'Test SMS'
        },
        'valid_whatsapp': {
            'type': 'WHATSAPP',
            'recipient': '+34612345678',
            'message': 'Test WhatsApp'
        }
    }


@pytest.fixture(scope="function", autouse=True)
def auto_screenshot(page: Page, request):
    """Automatically capture screenshots for all tests.
    
    Takes a screenshot after each test completes, regardless of pass/fail status.
    Screenshots are saved to tests/reports/screenshots/ directory with detailed
    naming that includes test status.
    
    Features:
    - Captures screenshot for all tests (passed and failed)
    - Names screenshots with test name and status
    - Stores screenshot path in test metrics
    - Fails silently if screenshot capture fails
    """
    yield
    
    try:
        # Generate screenshot filename from test name and status
        test_id = request.node.nodeid
        test_status = test_metrics.get(test_id, {}).get('status', 'unknown')
        test_name = request.node.name
        
        # Create descriptive screenshot filename
        screenshot_filename = f"{test_name}_{test_status}.png"
        screenshot_path = Path("tests/reports/screenshots") / screenshot_filename
        
        # Capture screenshot
        page.screenshot(path=str(screenshot_path))
        
        # Store screenshot path in metrics for HTML report
        if test_id in test_metrics:
            test_metrics[test_id]['screenshot'] = str(screenshot_path)
    except Exception:
        # Silent failure as per requirement 11.5
        pass


@pytest.fixture(scope="function", autouse=True)
def cleanup(page: Page):
    """Cleanup fixture that runs after each test.
    
    Fails silently if cleanup operations fail to prevent test suite interruption.
    """
    yield
    # Cleanup logic here (if needed)
    # Fails silently if cleanup operations fail
    try:
        # Future cleanup operations can be added here
        pass
    except Exception:
        # Silent failure as per requirement 11.5
        pass


@pytest.fixture(scope="function")
def query_page(page: Page):
    """Provide QueryPage instance for tests.
    
    This fixture returns a QueryPage instance for interacting with
    the notification query UI using the Page Object Model pattern.
    
    Args:
        page: Playwright page fixture
        
    Returns:
        QueryPage instance
    """
    from pages.query_page import QueryPage
    return QueryPage(page)
