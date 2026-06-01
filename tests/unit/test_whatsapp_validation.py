"""
Unit tests for WhatsApp validation in NotificationForm component.

This module tests that WhatsApp phone number validation works correctly, including:
- Valid E.164 format numbers are accepted
- Numbers without + prefix show error messages
- International format is enforced

Tests validate Requirements 6.2 and 6.4 by verifying:
- Real-time validation on input change
- Appropriate error messages for invalid inputs
- Validation error display
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestWhatsAppValidation:
    """Test suite for WhatsApp validation in NotificationForm."""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, page: Page):
        """Set up network mocks for API calls."""
        # Mock the API endpoint to prevent actual network calls
        page.route('**/api/v1/notifications', lambda route: route.abort())
    
    def test_valid_whatsapp_number_accepted(self, page: Page, notification_page):
        """Test that valid E.164 format WhatsApp numbers are accepted without error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Valid WhatsApp number is accepted
        - No error message is displayed
        - Input does not have error class
        """
        notification_page.navigate()
        
        # Select WHATSAPP type
        notification_page.select_type('WHATSAPP')
        
        # Enter valid WhatsApp number (E.164 format)
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345678')
        
        # Verify no error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert not error_message.is_visible(), "No error message should be displayed for valid WhatsApp number"
        
        # Verify input does not have error class
        assert 'error' not in recipient_input.get_attribute('class') or recipient_input.get_attribute('class') == '', \
            "Input should not have error class for valid WhatsApp number"
    
    def test_whatsapp_without_plus_prefix_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number without + prefix shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number without + prefix shows error
        - Error message is visible
        - Input has error class
        """
        notification_page.navigate()
        
        # Select WHATSAPP type
        notification_page.select_type('WHATSAPP')
        
        # Enter WhatsApp number without + prefix
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('34612345678')
        
        # Wait a moment for validation to trigger
        page.wait_for_timeout(100)
        
        # Verify error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp without + prefix"
        assert '+' in error_message.text_content() or 'E.164' in error_message.text_content() or 'format' in error_message.text_content().lower(), \
            "Error message should indicate E.164 format requirement"
        
        # Verify input has error class
        assert 'error' in recipient_input.get_attribute('class'), \
            "Input should have error class for WhatsApp without + prefix"
    
    def test_whatsapp_with_spaces_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number with spaces shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with spaces shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34 612 345 678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp with spaces"
    
    def test_whatsapp_validation_real_time(self, page: Page, notification_page):
        """Test that WhatsApp validation happens in real-time as user types.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Error appears immediately when invalid WhatsApp is entered
        - Error disappears when valid WhatsApp is entered
        - Validation is real-time (onChange)
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Type invalid WhatsApp (no + prefix)
        recipient_input.fill('34612345678')
        assert error_message.is_visible(), "Error should appear for WhatsApp without + prefix"
        
        # Add + prefix to make it valid
        recipient_input.fill('+34612345678')
        assert not error_message.is_visible(), "Error should disappear when + prefix is added"
    
    def test_whatsapp_with_letters_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number with letters shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with letters shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345ABC')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp with letters"
    
    def test_whatsapp_with_special_characters_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number with special characters shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with special characters shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345-678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp with special characters"
    
    def test_valid_whatsapp_variations_accepted(self, page: Page, notification_page):
        """Test that various valid WhatsApp formats are accepted.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Spanish WhatsApp number is accepted
        - US WhatsApp number is accepted
        - UK WhatsApp number is accepted
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Test Spanish number
        recipient_input.fill('+34612345678')
        assert not error_message.is_visible(), "Spanish WhatsApp number should be valid"
        
        # Test US number
        recipient_input.fill('+12025551234')
        assert not error_message.is_visible(), "US WhatsApp number should be valid"
        
        # Test UK number
        recipient_input.fill('+442071838750')
        assert not error_message.is_visible(), "UK WhatsApp number should be valid"
    
    def test_whatsapp_too_short_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number that is too short shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with fewer than 2 digits shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+3')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp that is too short"
    
    def test_whatsapp_too_long_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number that is too long shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with more than 15 digits shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+346123456789012345')  # Too many digits
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp that is too long"
    
    def test_whatsapp_only_plus_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number with only + prefix shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with only + prefix shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp with only + prefix"
    
    def test_whatsapp_with_parentheses_shows_error(self, page: Page, notification_page):
        """Test that WhatsApp number with parentheses shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - WhatsApp number with parentheses shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34 (612) 345-678')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for WhatsApp with parentheses"
