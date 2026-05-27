"""
Pytest configuration and fixtures for the Notification E2E Test Suite.

This module provides shared fixtures for test isolation, page object models,
and test data management.
"""

import pytest
from playwright.sync_api import Page, BrowserContext, Browser
from pathlib import Path
from typing import Generator


def pytest_configure(config):
    """Configure pytest with custom settings."""
    # Create reports directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Create screenshots directory if it doesn't exist
    screenshots_dir = Path("reports/screenshots")
    screenshots_dir.mkdir(exist_ok=True)


@pytest.fixture(scope="function")
def browser_context_args(browser_context_args):
    """Configure browser context with screenshot settings.
    
    This fixture extends the default browser_context_args to enable
    screenshot capture for all tests.
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
    
    Yields:
        Page: A fresh page instance
    """
    page = browser_context.new_page()
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
    Screenshots are saved to reports/screenshots/ directory.
    """
    yield
    
    try:
        # Generate screenshot filename from test name
        test_name = request.node.name
        screenshot_path = Path("reports/screenshots") / f"{test_name}.png"
        
        # Capture screenshot
        page.screenshot(path=str(screenshot_path))
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
def notification_page(page: Page):
    """Provide NotificationPage instance for tests.
    
    This fixture returns a NotificationPage instance for interacting with
    the notification form UI using the Page Object Model pattern.
    
    Args:
        page: Playwright page fixture
        
    Returns:
        NotificationPage instance
    """
    from pages.notification_page import NotificationPage
    return NotificationPage(page)


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
