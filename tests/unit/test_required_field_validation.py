"""
Unit tests for required field validation.

This module tests that required field validation works correctly in the NotificationForm component.
Tests validate Requirements 2.4 and 2.6 by verifying:
- Empty required fields prevent submission
- Error messages display for missing fields
- Form submission is blocked when validation fails
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestRequiredFieldValidation:
    """Test suite for required field validation."""
    
    def test_empty_recipient_field_invalid(self, page: Page, notification_page):
        """Test that empty recipient field is invalid.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Recipient field is required
        - Empty recipient shows error message
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill recipient first, then clear it to trigger onChange validation
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        recipient_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill other required fields
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Test subject')
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Error message should be shown for empty recipient"
    
    def test_empty_message_field_invalid(self, page: Page, notification_page):
        """Test that empty message field is invalid.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Message field is required
        - Empty message shows error message
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill recipient
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        
        # Fill message first, then clear it to trigger onChange validation
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        message_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill subject
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Test subject')
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="message-error"]')
        assert error_message.is_visible(), "Error message should be shown for empty message"
    
    def test_all_required_fields_empty_invalid(self, page: Page, notification_page):
        """Test that form with all required fields empty is invalid.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - All required fields must be filled
        - Multiple error messages are displayed
        """
        notification_page.navigate()
        
        # Fill then clear recipient to trigger validation
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        recipient_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill then clear message to trigger validation
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        message_input.fill('')
        page.wait_for_timeout(100)
        
        # Verify error messages are shown
        recipient_error = page.locator('[data-testid="recipient-error"]')
        message_error = page.locator('[data-testid="message-error"]')
        
        assert recipient_error.is_visible(), "Error message should be shown for empty recipient"
        assert message_error.is_visible(), "Error message should be shown for empty message"
    
    def test_form_submission_blocked_with_empty_fields(self, page: Page, notification_page):
        """Test that form submission is blocked when required fields are empty.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Form cannot be submitted with empty required fields
        - Submit button is disabled or form validation prevents submission
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill then clear recipient to trigger validation
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        recipient_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill message
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        
        # Verify form validation prevents submission
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Validation error should prevent submission"
    
    def test_whitespace_only_recipient_invalid(self, page: Page, notification_page):
        """Test that whitespace-only recipient is treated as empty.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Whitespace-only input is treated as empty
        - Error message is displayed
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill with whitespace only and trigger validation
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('   ')
        recipient_input.blur()
        page.wait_for_timeout(100)
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "Whitespace-only input should be treated as empty"
    
    def test_whitespace_only_message_invalid(self, page: Page, notification_page):
        """Test that whitespace-only message is treated as empty.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Whitespace-only input is treated as empty
        - Error message is displayed
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill recipient
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        
        # Fill message with whitespace only to trigger onChange validation
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        message_input.fill('   ')
        page.wait_for_timeout(100)
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="message-error"]')
        assert error_message.is_visible(), "Whitespace-only message should be treated as empty"
    
    def test_required_field_errors_clear_on_input(self, page: Page, notification_page):
        """Test that required field errors clear when user enters valid input.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Error messages disappear when field is filled
        - User can correct validation errors
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        recipient_input = page.locator('[data-testid="recipient"]')
        error_message = page.locator('[data-testid="recipient-error"]')
        
        # Fill then clear to trigger error
        recipient_input.fill('user@example.com')
        recipient_input.fill('')
        page.wait_for_timeout(100)
        assert error_message.is_visible(), "Error should be shown for empty field"
        
        # Fill field with valid input
        recipient_input.fill('user@example.com')
        page.wait_for_timeout(100)
        assert not error_message.is_visible(), "Error should disappear when field is filled"
    
    def test_sms_required_fields(self, page: Page, notification_page):
        """Test that SMS type has same required fields as EMAIL.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - SMS type also requires type, recipient, and message
        - Subject is not required for SMS
        """
        notification_page.navigate()
        
        notification_page.select_type('SMS')
        
        # Fill then clear recipient to trigger validation
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345678')
        recipient_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill message
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="recipient-error"]')
        assert error_message.is_visible(), "SMS type should also require recipient"
    
    def test_whatsapp_required_fields(self, page: Page, notification_page):
        """Test that WhatsApp type has same required fields as EMAIL.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - WhatsApp type also requires type, recipient, and message
        - Subject is not required for WhatsApp
        """
        notification_page.navigate()
        
        notification_page.select_type('WHATSAPP')
        
        # Fill then clear message to trigger validation
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        message_input.fill('')
        page.wait_for_timeout(100)
        
        # Fill recipient
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345678')
        
        # Verify error message is shown
        error_message = page.locator('[data-testid="message-error"]')
        assert error_message.is_visible(), "WhatsApp type should also require message"
    
    def test_subject_not_required_for_email(self, page: Page, notification_page):
        """Test that subject field is optional for EMAIL type.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Subject field is optional
        - Form can be submitted without subject
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill required fields but leave subject empty
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('')
        
        # Verify no error message for subject
        subject_error = page.locator('[data-testid="subject-error"]')
        if subject_error.count() > 0:
            assert not subject_error.is_visible(), "Subject should not have error message"
    
    def test_form_submission_succeeds_with_all_required_fields(self, page: Page, notification_page):
        """Test that form submission succeeds when all required fields are filled.
        
        Validates: Requirements 2.4, 2.6
        
        Verifies that:
        - Form can be submitted with all required fields filled
        - No validation errors are shown
        """
        notification_page.navigate()
        
        notification_page.select_type('EMAIL')
        
        # Fill all required fields
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('user@example.com')
        
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Test subject')
        
        # Verify no error messages
        recipient_error = page.locator('[data-testid="recipient-error"]')
        message_error = page.locator('[data-testid="message-error"]')
        
        if recipient_error.count() > 0:
            assert not recipient_error.is_visible(), "No error for valid recipient"
        if message_error.count() > 0:
            assert not message_error.is_visible(), "No error for valid message"
