"""
Unit tests for SMS validation in NotificationForm component.

This module tests that SMS phone number validation works correctly, including:
- Valid ES region phone numbers are accepted
- Invalid phone numbers show error messages
- Error messages display in real-time

Tests validate Requirements 6.2 and 6.4 by verifying:
- Real-time validation on input change
- Appropriate error messages for invalid inputs
- Validation error display
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestSMSValidation:
    """Test suite for SMS validation in NotificationForm."""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, page: Page):
        """Set up network mocks for API calls."""
        # Mock the API endpoint to prevent actual network calls
        page.route('**/api/v1/notifications', lambda route: route.abort())
    
    def test_valid_sms_number_accepted(self, page: Page, notification_page):
        """Test that valid ES region SMS numbers are accepted without error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Valid SMS number is accepted
        - No error message is displayed
        - Input does not have error class
        """
        notification_page.navigate()
        
        # Select SMS type
        notification_page.select_type('SMS')
        
        # Enter valid SMS number (+34 followed by 9 digits starting with 6 or 7)
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345678')
        
        # Verify no error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert not error_message.is_visible(), "No error message should be displayed for valid SMS number"
        
        # Verify input does not have error class
        assert 'error' not in recipient_input.get_attribute('class') or recipient_input.get_attribute('class') == '', \
            "Input should not have error class for valid SMS number"
    
    def test_invalid_sms_number_shows_error(self, page: Page, notification_page):
        """Test that invalid SMS numbers show error message.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Invalid SMS number shows error message
        - Error message is visible
        - Input has error class
        """
        notification_page.navigate()
        
        # Select SMS type
        notification_page.select_type('SMS')
        
        # Enter invalid SMS number (missing +34 prefix)
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('612345678')
        
        # Wait a moment for validation to trigger
        page.wait_for_timeout(100)
        
        # Verify error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for invalid SMS number"
        assert 'SMS' in error_message.text_content() or 'phone' in error_message.text_content().lower(), \
            "Error message should indicate SMS phone number issue"
        
        # Verify input has error class
        assert 'error' in recipient_input.get_attribute('class'), \
            "Input should have error class for invalid SMS number"
    
    def test_sms_without_plus_prefix_shows_error(self, page: Page, notification_page):
        """Test that SMS number without + prefix shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number without + prefix shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('34612345678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS without + prefix"
    
    def test_sms_with_wrong_country_code_shows_error(self, page: Page, notification_page):
        """Test that SMS number with wrong country code shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number with wrong country code shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+33612345678')  # French number instead of Spanish
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for wrong country code"
    
    def test_sms_with_invalid_prefix_digit_shows_error(self, page: Page, notification_page):
        """Test that SMS number with invalid prefix digit shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number starting with 8 or 9 shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        # Valid format but starts with 8 (should start with 6 or 7)
        recipient_input.fill('+34812345678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS starting with 8"
    
    def test_sms_validation_real_time(self, page: Page, notification_page):
        """Test that SMS validation happens in real-time as user types.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Error appears immediately when invalid SMS is entered
        - Error disappears when valid SMS is entered
        - Validation is real-time (onChange)
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Type invalid SMS
        recipient_input.fill('+3461234')
        assert error_message.is_visible(), "Error should appear for incomplete SMS"
        
        # Continue typing to make it valid
        recipient_input.fill('+34612345678')
        assert not error_message.is_visible(), "Error should disappear when SMS becomes valid"
    
    def test_sms_with_spaces_shows_error(self, page: Page, notification_page):
        """Test that SMS number with spaces shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number with spaces shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34 612 345 678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS with spaces"
    
    def test_valid_sms_variations_accepted(self, page: Page, notification_page):
        """Test that various valid SMS formats are accepted.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS starting with +346 is accepted
        - SMS starting with +347 is accepted
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Test SMS starting with 6
        recipient_input.fill('+34612345678')
        assert not error_message.is_visible(), "SMS starting with +346 should be valid"
        
        # Test SMS starting with 7
        recipient_input.fill('+34712345678')
        assert not error_message.is_visible(), "SMS starting with +347 should be valid"
    
    def test_sms_too_short_shows_error(self, page: Page, notification_page):
        """Test that SMS number that is too short shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number with fewer than 12 digits shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+3461234567')  # Only 11 digits
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS that is too short"
    
    def test_sms_too_long_shows_error(self, page: Page, notification_page):
        """Test that SMS number that is too long shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number with more than 12 digits shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+346123456789')  # 13 digits
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS that is too long"
    
    def test_sms_with_letters_shows_error(self, page: Page, notification_page):
        """Test that SMS number with letters shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - SMS number with letters shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345ABC')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for SMS with letters"
