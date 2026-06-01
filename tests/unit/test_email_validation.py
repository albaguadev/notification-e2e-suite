"""
Unit tests for email validation in NotificationForm component.

This module tests that email validation works correctly, including:
- Valid email formats are accepted
- Invalid email formats show error messages
- Error messages display in real-time

Tests validate Requirements 6.2 and 6.4 by verifying:
- Real-time validation on input change
- Appropriate error messages for invalid inputs
- Validation error display
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestEmailValidation:
    """Test suite for email validation in NotificationForm."""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, page: Page):
        """Set up network mocks for API calls."""
        # Mock the API endpoint to prevent actual network calls
        page.route('**/api/v1/notifications', lambda route: route.abort())
    
    def test_valid_email_accepted(self, page: Page, notification_page):
        """Test that valid email formats are accepted without error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Valid email is accepted
        - No error message is displayed
        - Input does not have error class
        """
        notification_page.navigate()
        
        # Select EMAIL type (should be default)
        notification_page.select_type('EMAIL')
        
        # Enter valid email
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        
        # Verify no error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert not error_message.is_visible(), "No error message should be displayed for valid email"
        
        # Verify input does not have error class
        assert 'error' not in recipient_input.get_attribute('class') or recipient_input.get_attribute('class') == '', \
            "Input should not have error class for valid email"
    
    def test_invalid_email_shows_error(self, page: Page, notification_page):
        """Test that invalid email formats show error message.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Invalid email shows error message
        - Error message is visible
        - Input has error class
        """
        notification_page.navigate()
        
        # Select EMAIL type
        notification_page.select_type('EMAIL')
        
        # Enter invalid email (missing @)
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('userexample.com')
        
        # Wait a moment for validation to trigger
        page.wait_for_timeout(100)
        
        # Verify error message is displayed
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for invalid email"
        assert 'Invalid email format' in error_message.text_content(), \
            "Error message should indicate invalid email format"
        
        # Verify input has error class
        assert 'error' in recipient_input.get_attribute('class'), \
            "Input should have error class for invalid email"
    
    def test_email_without_domain_shows_error(self, page: Page, notification_page):
        """Test that email without domain shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email without domain shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for email without domain"
    
    def test_email_without_local_part_shows_error(self, page: Page, notification_page):
        """Test that email without local part shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email without local part shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('@example.com')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for email without local part"
    
    def test_email_with_spaces_shows_error(self, page: Page, notification_page):
        """Test that email with spaces shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email with spaces shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user @example.com')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for email with spaces"
    
    def test_email_validation_real_time(self, page: Page, notification_page):
        """Test that email validation happens in real-time as user types.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Error appears immediately when invalid email is entered
        - Error disappears when valid email is entered
        - Validation is real-time (onChange)
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Type invalid email
        recipient_input.fill('invalid')
        assert error_message.is_visible(), "Error should appear for invalid email"
        
        # Continue typing to make it valid
        recipient_input.fill('invalid@example.com')
        assert not error_message.is_visible(), "Error should disappear when email becomes valid"
    
    def test_empty_email_shows_required_error(self, page: Page, notification_page):
        """Test that empty email field shows required error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Empty email shows required error
        - Error message indicates field is required
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        
        # Focus and blur to trigger validation
        recipient_input.focus()
        recipient_input.blur()
        
        # Try to submit with empty field
        submit_button = page.locator('[data-testid="submit"]')
        submit_button.click()
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for empty email"
        assert 'required' in error_message.text_content().lower(), \
            "Error message should indicate field is required"
    
    def test_email_with_multiple_at_signs_shows_error(self, page: Page, notification_page):
        """Test that email with multiple @ signs shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email with multiple @ signs shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@@example.com')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for email with multiple @ signs"
    
    def test_email_with_special_characters_shows_error(self, page: Page, notification_page):
        """Test that email with invalid special characters shows error.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email with invalid special characters shows error
        - Error message is visible
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user#name@example.com')
        
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be displayed for email with invalid special characters"
    
    def test_valid_email_variations_accepted(self, page: Page, notification_page):
        """Test that various valid email formats are accepted.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Email with numbers is accepted
        - Email with dots in local part is accepted
        - Email with hyphens in domain is accepted
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Test email with numbers
        recipient_input.fill('user123@example.com')
        assert not error_message.is_visible(), "Email with numbers should be valid"
        
        # Test email with dots in local part
        recipient_input.fill('first.last@example.com')
        assert not error_message.is_visible(), "Email with dots in local part should be valid"
        
        # Test email with hyphens in domain
        recipient_input.fill('user@example-domain.com')
        assert not error_message.is_visible(), "Email with hyphens in domain should be valid"
    
    def test_error_message_content_is_helpful(self, page: Page, notification_page):
        """Test that error messages are helpful and specific.
        
        Validates: Requirements 6.2, 6.4
        
        Verifies that:
        - Error message clearly indicates the problem
        - Error message is user-friendly
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Enter invalid email
        recipient_input.fill('invalid-email')
        
        # Verify error message is helpful
        assert error_message.is_visible(), "Error message should be visible"
        error_text = error_message.text_content()
        assert 'email' in error_text.lower(), "Error message should mention 'email'"
        assert 'invalid' in error_text.lower() or 'format' in error_text.lower(), \
            "Error message should indicate format issue"
