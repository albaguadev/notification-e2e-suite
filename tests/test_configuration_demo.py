"""
Configuration demonstration tests.

This module demonstrates all the pytest and Playwright configuration features:
- Multiple browser engines (Chromium, Firefox, WebKit)
- Test markers (unit_test, property_test, e2e_test)
- Automatic screenshot capture
- HTML report generation
- Browser context configuration
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
def test_unit_example(page: Page):
    """Example unit test demonstrating marker usage."""
    # This test demonstrates the unit_test marker
    assert page is not None
    assert page.viewport_size["width"] == 1280
    assert page.viewport_size["height"] == 720


@pytest.mark.property_test
def test_property_example(page: Page):
    """Example property test demonstrating marker usage."""
    # This test demonstrates the property_test marker
    # In real tests, this would use Hypothesis for property-based testing
    assert page is not None


@pytest.mark.e2e_test
def test_e2e_example(page: Page):
    """Example E2E test demonstrating marker usage."""
    # This test demonstrates the e2e_test marker
    # In real tests, this would test complete user flows
    assert page is not None


@pytest.mark.unit_test
def test_screenshot_capture(page: Page):
    """Test that demonstrates automatic screenshot capture.
    
    A screenshot will be automatically captured after this test completes,
    regardless of pass/fail status.
    """
    # Navigate to a simple page to make the screenshot more interesting
    page.goto("about:blank")
    page.set_content("<h1>Screenshot Test</h1><p>This page will be captured.</p>")
    
    # Verify content
    assert page.locator("h1").text_content() == "Screenshot Test"


@pytest.mark.unit_test
def test_browser_context_viewport(page: Page):
    """Test that browser context has correct viewport configuration."""
    viewport = page.viewport_size
    
    assert viewport is not None
    assert viewport["width"] == 1280
    assert viewport["height"] == 720


@pytest.mark.unit_test
def test_test_data_fixture(test_data):
    """Test that test_data fixture provides expected data."""
    assert "valid_email" in test_data
    assert "valid_sms" in test_data
    assert "valid_whatsapp" in test_data
    
    # Verify email data structure
    email_data = test_data["valid_email"]
    assert email_data["type"] == "EMAIL"
    assert email_data["recipient"] == "test@example.com"
    assert email_data["message"] == "Test message"
    assert email_data["subject"] == "Test subject"
    
    # Verify SMS data structure
    sms_data = test_data["valid_sms"]
    assert sms_data["type"] == "SMS"
    assert sms_data["recipient"] == "+34612345678"
    assert sms_data["message"] == "Test SMS"
    
    # Verify WhatsApp data structure
    whatsapp_data = test_data["valid_whatsapp"]
    assert whatsapp_data["type"] == "WHATSAPP"
    assert whatsapp_data["recipient"] == "+34612345678"
    assert whatsapp_data["message"] == "Test WhatsApp"


@pytest.mark.unit_test
def test_multiple_assertions(page: Page):
    """Test with multiple assertions to demonstrate detailed error reporting."""
    # Create a simple page
    page.goto("about:blank")
    page.set_content("""
        <html>
            <body>
                <h1 id="title">Test Page</h1>
                <p id="content">This is test content.</p>
                <button id="btn">Click Me</button>
            </body>
        </html>
    """)
    
    # Multiple assertions
    assert page.locator("#title").is_visible()
    assert page.locator("#title").text_content() == "Test Page"
    assert page.locator("#content").is_visible()
    assert page.locator("#content").text_content() == "This is test content."
    assert page.locator("#btn").is_visible()
    assert page.locator("#btn").text_content() == "Click Me"
