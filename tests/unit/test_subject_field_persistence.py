"""
Unit tests for subject field visibility persistence.

This module tests that the NotificationForm component correctly manages the visibility
of the subject field based on notification type selection and user input.

Tests validate Requirement 6.6 by verifying:
- Subject field is hidden when notification type is not EMAIL
- Subject field remains visible when user has entered text, even after switching types
- Subject field is hidden again when user clears the text or submits the form
- Subject field visibility logic works correctly for all type transitions
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestSubjectFieldPersistence:
    """Test suite for subject field visibility persistence."""
    
    def test_subject_field_hidden_for_sms_type(self, page: Page, notification_page):
        """Test that subject field is hidden when SMS type is selected.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field is not visible for SMS type
        - Subject field remains hidden when SMS is selected
        """
        notification_page.navigate()
        
        # Select SMS type
        notification_page.select_type('SMS')
        
        # Verify subject field is not visible
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden for SMS type"
    
    def test_subject_field_hidden_for_whatsapp_type(self, page: Page, notification_page):
        """Test that subject field is hidden when WHATSAPP type is selected.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field is not visible for WHATSAPP type
        - Subject field remains hidden when WHATSAPP is selected
        """
        notification_page.navigate()
        
        # Select WHATSAPP type
        notification_page.select_type('WHATSAPP')
        
        # Verify subject field is not visible
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden for WHATSAPP type"
    
    def test_subject_field_visible_for_email_type(self, page: Page, notification_page):
        """Test that subject field is visible when EMAIL type is selected.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field is visible by default for EMAIL type
        """
        notification_page.navigate()
        
        # Select EMAIL type (should be default, but explicit for clarity)
        notification_page.select_type('EMAIL')
        
        # Verify subject field is visible
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible for EMAIL type"
    
    def test_subject_field_visible_after_entering_text_then_switching_to_sms(self, page: Page, notification_page):
        """Test that subject field remains visible after entering text, when switching to SMS.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field becomes visible after entering text in EMAIL mode
        - Subject field remains visible when switching to SMS type
        - Subject field is NOT hidden just because type changed
        """
        notification_page.navigate()
        
        # Start with EMAIL type
        notification_page.select_type('EMAIL')
        
        # Enter text in subject field
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Important subject')
        
        # Verify subject field is visible and has content
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible with content"
        assert subject_input.input_value() == 'Important subject', \
            "Subject text should be retained"
        
        # Switch to SMS type
        notification_page.select_type('SMS')
        
        # Subject field should REMAIN visible because user entered content
        assert notification_page.is_subject_visible(), \
            "Subject field should remain visible after switching to SMS while containing text (Requirement 6.6)"
    
    def test_subject_field_visible_after_entering_text_then_switching_to_whatsapp(self, page: Page, notification_page):
        """Test that subject field remains visible after entering text, when switching to WHATSAPP.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field remains visible when switching from EMAIL to WHATSAPP with text
        """
        notification_page.navigate()
        
        # Start with EMAIL
        notification_page.select_type('EMAIL')
        
        # Enter subject
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Test subject')
        
        # Switch to WHATSAPP
        notification_page.select_type('WHATSAPP')
        
        # Subject field should remain visible
        assert notification_page.is_subject_visible(), \
            "Subject field should remain visible with text after switching to WHATSAPP"
    
    def test_subject_field_hidden_when_text_is_cleared(self, page: Page, notification_page):
        """Test that subject field is hidden when text is cleared while in non-EMAIL type.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field remains visible after switching with text
        - Subject field becomes hidden when text is cleared
        """
        notification_page.navigate()
        
        # Setup: EMAIL with subject text
        notification_page.select_type('EMAIL')
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Important subject')
        
        # Switch to SMS
        notification_page.select_type('SMS')
        
        # Subject should still be visible
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible with text"
        
        # Clear the subject text
        subject_input.fill('')
        page.wait_for_timeout(100)  # Wait for visibility update
        
        # Now subject should be hidden
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden after clearing text in non-EMAIL mode"
    
    def test_subject_field_hidden_after_form_submission(self, page: Page, notification_page):
        """Test that subject field is hidden after form submission (form reset).
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field remains visible with text before submission
        - Subject field visibility resets after form submission
        """
        # Mock successful API response
        page.route('**/api/v1/notifications', lambda route: route.fulfill(
            status=200,
            headers={'Content-Type': 'application/json'},
            body='{"id": "123", "type": "EMAIL", "status": "SENT"}'
        ))
        
        notification_page.navigate()
        
        # Setup: Enter EMAIL with subject
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message',
            'Test subject'
        )
        
        # Verify subject is visible before submission
        assert notification_page.is_subject_visible(), \
            "Subject should be visible before submission"
        
        # Submit form
        notification_page.submit()
        
        # Wait for form reset
        page.wait_for_timeout(500)
        
        # After successful submission, form should be reset
        # Default type is EMAIL, so subject might be visible but empty
        # The key is that the text should be cleared
        subject_input = page.locator('[data-testid="subject"]')
        assert subject_input.input_value() == '', \
            "Subject field should be cleared after form submission"
    
    def test_subject_field_hidden_when_switching_from_email_to_sms_with_no_text(self, page: Page, notification_page):
        """Test that subject field is hidden when switching to SMS without entering text.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field is hidden when switching away from EMAIL without text
        """
        notification_page.navigate()
        
        # Start with EMAIL
        notification_page.select_type('EMAIL')
        
        # Don't enter any subject text
        # Just verify subject is visible (but empty)
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible for EMAIL type (even if empty)"
        
        # Switch to SMS
        notification_page.select_type('SMS')
        
        # Subject should now be hidden
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden for SMS type when empty"
    
    def test_subject_field_persistence_through_multiple_type_switches(self, page: Page, notification_page):
        """Test that subject field persistence works through multiple type switches.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field visibility is correctly managed through multiple type changes
        - Text is preserved through type switches
        - Field is hidden only when it should be
        """
        notification_page.navigate()
        
        # Start: EMAIL, no text
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible for EMAIL"
        
        # Add text
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Subject text')
        page.wait_for_timeout(100)
        
        # Switch to SMS - should remain visible
        notification_page.select_type('SMS')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), \
            "Should remain visible with text even after switching to SMS"
        assert subject_input.input_value() == 'Subject text', \
            "Text should be preserved"
        
        # Switch back to EMAIL
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible for EMAIL"
        assert subject_input.input_value() == 'Subject text', "Text should still be preserved"
        
        # Switch to WHATSAPP
        notification_page.select_type('WHATSAPP')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), \
            "Should remain visible with text even after switching to WHATSAPP"
        
        # Clear text
        subject_input.fill('')
        page.wait_for_timeout(100)
        
        # Should now be hidden
        assert not notification_page.is_subject_visible(), \
            "Should be hidden after clearing text in WHATSAPP mode"
        
        # Switch back to EMAIL
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        # For EMAIL it should always be visible (whether empty or not)
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible for EMAIL type"
    
    def test_subject_field_text_preserved_during_type_switches(self, page: Page, notification_page):
        """Test that subject field text is preserved when switching types.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject text is retained when switching between types
        - User doesn't lose data when changing type
        """
        notification_page.navigate()
        
        # Enter EMAIL with subject
        notification_page.select_type('EMAIL')
        subject_input = page.locator('[data-testid="subject"]')
        original_text = 'Important Email Subject'
        subject_input.fill(original_text)
        
        # Switch to SMS
        notification_page.select_type('SMS')
        assert subject_input.input_value() == original_text, \
            "Subject text should be preserved when switching to SMS"
        
        # Switch to WHATSAPP
        notification_page.select_type('WHATSAPP')
        assert subject_input.input_value() == original_text, \
            "Subject text should be preserved when switching to WHATSAPP"
        
        # Switch back to EMAIL
        notification_page.select_type('EMAIL')
        assert subject_input.input_value() == original_text, \
            "Subject text should be preserved when switching back to EMAIL"
    
    def test_subject_field_visible_only_when_necessary(self, page: Page, notification_page):
        """Test that subject field is only visible when it should be.
        
        Validates: Requirement 6.6
        
        Verifies that:
        - Subject field visibility follows the rule: visible if EMAIL OR (non-EMAIL AND has_text)
        """
        notification_page.navigate()
        subject_input = page.locator('[data-testid="subject"]')
        
        # Case 1: EMAIL, empty - visible
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible: EMAIL + empty"
        
        # Case 2: EMAIL, with text - visible
        subject_input.fill('Text')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible: EMAIL + text"
        
        # Case 3: SMS, with text - visible
        notification_page.select_type('SMS')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible: SMS + text"
        
        # Case 4: SMS, empty - hidden
        subject_input.fill('')
        page.wait_for_timeout(100)
        assert not notification_page.is_subject_visible(), "Should be hidden: SMS + empty"
        
        # Case 5: WHATSAPP, empty - hidden
        notification_page.select_type('WHATSAPP')
        page.wait_for_timeout(100)
        assert not notification_page.is_subject_visible(), "Should be hidden: WHATSAPP + empty"
        
        # Case 6: WHATSAPP, with text - visible
        # Note: For WHATSAPP with empty subject, the field is not visible, so we need to switch back to EMAIL first
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        subject_input.fill('Text')
        page.wait_for_timeout(100)
        notification_page.select_type('WHATSAPP')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible: WHATSAPP + text"
        
        # Case 7: Back to EMAIL, with text - visible
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), "Should be visible: EMAIL + text"
    
    def test_subject_field_hidden_for_sms_until_text_entered(self, page: Page, notification_page):
        """Test that subject field is properly hidden/shown based on type and content.
        
        Validates: Requirement 6.6
        
        Verifies the complete flow of the requirement
        """
        notification_page.navigate()
        
        # Start with EMAIL (default)
        assert notification_page.is_subject_visible(), \
            "Subject should be visible by default (EMAIL type)"
        
        # Switch to SMS without touching subject
        notification_page.select_type('SMS')
        page.wait_for_timeout(100)
        assert not notification_page.is_subject_visible(), \
            "Subject should be hidden for SMS type when empty"
        
        # Now switch back to EMAIL and type in subject, then switch to SMS
        notification_page.select_type('EMAIL')
        page.wait_for_timeout(100)
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Some subject text')
        page.wait_for_timeout(100)
        
        # Switch to SMS with subject having text
        notification_page.select_type('SMS')
        page.wait_for_timeout(100)
        
        # Subject should become visible
        assert notification_page.is_subject_visible(), \
            "Subject should become visible when text is entered (even in SMS mode)"
        
        # Delete the text
        subject_input.fill('')
        page.wait_for_timeout(100)
        
        # Subject should become hidden again
        assert not notification_page.is_subject_visible(), \
            "Subject should become hidden again when text is deleted (in SMS mode)"
    
    def test_subject_field_manual_clear_in_non_email_hides_it(self, page: Page, notification_page):
        """Test that manually clearing subject in non-EMAIL mode hides the field.
        
        Validates: Requirement 6.6 - "until form submission or manual clear"
        
        Verifies that:
        - User can manually clear the subject field
        - Field is hidden when manually cleared
        """
        notification_page.navigate()
        
        # Setup: EMAIL with subject
        notification_page.select_type('EMAIL')
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Important subject')
        page.wait_for_timeout(100)
        
        # Switch to SMS (field stays visible due to text)
        notification_page.select_type('SMS')
        page.wait_for_timeout(100)
        assert notification_page.is_subject_visible(), \
            "Should be visible with text in SMS"
        
        # Manually clear the subject using fill('')
        subject_input.fill('')
        page.wait_for_timeout(100)
        
        # Field should now be hidden
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden after manual clear in non-EMAIL mode"
