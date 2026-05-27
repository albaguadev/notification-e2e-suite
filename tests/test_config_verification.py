"""
Configuration verification test.

This test verifies that the pytest and Playwright configuration is working correctly.
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
def test_browser_context_configured(page: Page):
    """Verify that browser context is properly configured."""
    # Check that page is available
    assert page is not None
    
    # Check viewport size
    viewport_size = page.viewport_size
    assert viewport_size is not None
    assert viewport_size["width"] == 1280
    assert viewport_size["height"] == 720


@pytest.mark.unit_test
def test_screenshot_directory_exists():
    """Verify that screenshot directory is created."""
    from pathlib import Path
    
    screenshots_dir = Path("reports/screenshots")
    assert screenshots_dir.exists()
    assert screenshots_dir.is_dir()


@pytest.mark.unit_test
def test_reports_directory_exists():
    """Verify that reports directory is created."""
    from pathlib import Path
    
    reports_dir = Path("reports")
    assert reports_dir.exists()
    assert reports_dir.is_dir()
