"""
Unit tests for NotificationForm component rendering.

This module tests that the NotificationForm component renders correctly,
including all form fields, dropdown options, button states, and initial state.

Tests validate Requirements 6.1 and 11.1 by verifying:
- All form fields render correctly
- Type dropdown contains EMAIL, SMS, WHATSAPP options
- Submit button is present and enabled
- Initial component state is correct
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestNotificationFormRendering:
    """Test suite for NotificationForm component rendering."""
    
    def test_form_renders_correctly(self, page: Page, notification_page):
        """Test that the notification form renders correctly.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The form container is visible
        - The form heading is displayed
        - The form element exists
        """
        notification_page.navigate()
        
        # Verify form container is visible
        form_container = page.locator('.notification-form-container')
        assert form_container.is_visible(), "Form container should be visible"
        
        # Verify form heading is displayed
        heading = page.locator('.notification-form-container h2')
        assert heading.is_visible(), "Form heading should be visible"
        assert heading.text_content() == "Send Notification", "Form heading should display 'Send Notification'"
        
        # Verify form element exists
        form = page.locator('.notification-form')
        assert form.is_visible(), "Form element should be visible"
    
    def test_notification_type_field_renders(self, page: Page, notification_page):
        """Test that the notification type dropdown field renders correctly.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The type dropdown is visible
        - The label is displayed
        - The dropdown has the correct data-testid attribute
        """
        notification_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="notification-type"]')
        assert label.is_visible(), "Type field label should be visible"
        assert "Notification Type" in label.text_content(), "Label should display 'Notification Type'"
        
        # Verify required indicator is shown
        required_indicator = label.locator('.required')
        assert required_indicator.is_visible(), "Required indicator should be visible"
        
        # Verify dropdown is visible
        type_select = page.locator('[data-testid="notification-type"]')
        assert type_select.is_visible(), "Type dropdown should be visible"
    
    def test_type_dropdown_contains_all_options(self, page: Page, notification_page):
        """Test that the type dropdown contains EMAIL, SMS, and WHATSAPP options.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - EMAIL option is available
        - SMS option is available
        - WHATSAPP option is available
        """
        notification_page.navigate()
        
        type_select = page.locator('[data-testid="notification-type"]')
        
        # Get all option values
        options = type_select.locator('option').all()
        option_values = [option.get_attribute('value') for option in options]
        
        # Verify all required options are present
        assert 'EMAIL' in option_values, "EMAIL option should be available"
        assert 'SMS' in option_values, "SMS option should be available"
        assert 'WHATSAPP' in option_values, "WHATSAPP option should be available"
        
        # Verify we have exactly 3 options
        assert len(option_values) == 3, "Should have exactly 3 notification type options"
    
    def test_recipient_field_renders(self, page: Page, notification_page):
        """Test that the recipient input field renders correctly.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The recipient input is visible
        - The label is displayed
        - The input has the correct data-testid attribute
        - The input is empty initially
        """
        notification_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="recipient"]')
        assert label.is_visible(), "Recipient field label should be visible"
        assert "Recipient" in label.text_content(), "Label should display 'Recipient'"
        
        # Verify required indicator is shown
        required_indicator = label.locator('.required')
        assert required_indicator.is_visible(), "Required indicator should be visible"
        
        # Verify input is visible
        recipient_input = page.locator('[data-testid="recipient"]')
        assert recipient_input.is_visible(), "Recipient input should be visible"
        
        # Verify input is empty initially
        assert recipient_input.input_value() == "", "Recipient input should be empty initially"
    
    def test_message_field_renders(self, page: Page, notification_page):
        """Test that the message textarea field renders correctly.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The message textarea is visible
        - The label is displayed
        - The textarea has the correct data-testid attribute
        - The textarea is empty initially
        """
        notification_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="message"]')
        assert label.is_visible(), "Message field label should be visible"
        assert "Message" in label.text_content(), "Label should display 'Message'"
        
        # Verify required indicator is shown
        required_indicator = label.locator('.required')
        assert required_indicator.is_visible(), "Required indicator should be visible"
        
        # Verify textarea is visible
        message_input = page.locator('[data-testid="message"]')
        assert message_input.is_visible(), "Message textarea should be visible"
        
        # Verify textarea is empty initially
        assert message_input.input_value() == "", "Message textarea should be empty initially"
    
    def test_subject_field_visible_for_email_type(self, page: Page, notification_page):
        """Test that the subject field is visible when EMAIL type is selected.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The subject field is visible for EMAIL type
        - The label is displayed
        - The subject input has the correct data-testid attribute
        """
        notification_page.navigate()
        
        # EMAIL is the default type, so subject should be visible
        subject_input = page.locator('[data-testid="subject"]')
        assert subject_input.is_visible(), "Subject field should be visible for EMAIL type"
        
        # Verify label is displayed
        label = page.locator('label[for="subject"]')
        assert label.is_visible(), "Subject field label should be visible"
        assert "Subject" in label.text_content(), "Label should display 'Subject'"
        
        # Verify optional indicator is shown (not required for EMAIL)
        optional_indicator = label.locator('.optional')
        assert optional_indicator.is_visible(), "Optional indicator should be visible for subject"
    
    def test_subject_field_hidden_for_sms_type(self, page: Page, notification_page):
        """Test that the subject field is hidden when SMS type is selected.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The subject field is hidden for SMS type
        """
        notification_page.navigate()
        
        # Select SMS type
        notification_page.select_type('SMS')
        
        # Verify subject field is hidden
        subject_input = page.locator('[data-testid="subject"]')
        assert not subject_input.is_visible(), "Subject field should be hidden for SMS type"
    
    def test_subject_field_hidden_for_whatsapp_type(self, page: Page, notification_page):
        """Test that the subject field is hidden when WHATSAPP type is selected.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The subject field is hidden for WHATSAPP type
        """
        notification_page.navigate()
        
        # Select WHATSAPP type
        notification_page.select_type('WHATSAPP')
        
        # Verify subject field is hidden
        subject_input = page.locator('[data-testid="subject"]')
        assert not subject_input.is_visible(), "Subject field should be hidden for WHATSAPP type"
    
    def test_submit_button_present_and_enabled(self, page: Page, notification_page):
        """Test that the submit button is present and enabled initially.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The submit button is visible
        - The submit button is enabled
        - The submit button has the correct data-testid attribute
        - The submit button displays the correct text
        """
        notification_page.navigate()
        
        submit_button = page.locator('[data-testid="submit"]')
        
        # Verify button is visible
        assert submit_button.is_visible(), "Submit button should be visible"
        
        # Verify button is enabled
        assert not submit_button.is_disabled(), "Submit button should be enabled initially"
        
        # Verify button text
        button_text = submit_button.text_content()
        assert button_text == "Send Notification", "Submit button should display 'Send Notification'"
    
    def test_initial_component_state(self, page: Page, notification_page):
        """Test that the initial component state is correct.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - The default notification type is EMAIL
        - All form fields are empty
        - No error messages are displayed
        - No status message is displayed
        """
        notification_page.navigate()
        
        # Verify default type is EMAIL
        type_select = page.locator('[data-testid="notification-type"]')
        assert type_select.input_value() == "EMAIL", "Default notification type should be EMAIL"
        
        # Verify all form fields are empty
        recipient_input = page.locator('[data-testid="recipient"]')
        message_input = page.locator('[data-testid="message"]')
        subject_input = page.locator('[data-testid="subject"]')
        
        assert recipient_input.input_value() == "", "Recipient field should be empty initially"
        assert message_input.input_value() == "", "Message field should be empty initially"
        assert subject_input.input_value() == "", "Subject field should be empty initially"
        
        # Verify no error messages are displayed
        error_messages = page.locator('.error-message')
        assert error_messages.count() == 0, "No error messages should be displayed initially"
        
        # Verify no status message is displayed
        status_message = page.locator('[data-testid="status-message"]')
        assert not status_message.is_visible(), "Status message should not be visible initially"
    
    def test_form_fields_are_interactive(self, page: Page, notification_page):
        """Test that all form fields are interactive and accept input.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - Type dropdown can be changed
        - Recipient input accepts text
        - Message textarea accepts text
        - Subject input accepts text
        """
        notification_page.navigate()
        
        # Test type dropdown is interactive
        type_select = page.locator('[data-testid="notification-type"]')
        type_select.select_option('SMS')
        assert type_select.input_value() == "SMS", "Type dropdown should accept selection"
        
        # Test recipient input is interactive
        recipient_input = page.locator('[data-testid="recipient"]')
        recipient_input.fill('+34612345678')
        assert recipient_input.input_value() == "+34612345678", "Recipient input should accept text"
        
        # Test message textarea is interactive
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Test message')
        assert message_input.input_value() == "Test message", "Message textarea should accept text"
        
        # Switch back to EMAIL to test subject field
        type_select.select_option('EMAIL')
        subject_input = page.locator('[data-testid="subject"]')
        subject_input.fill('Test subject')
        assert subject_input.input_value() == "Test subject", "Subject input should accept text"
    
    def test_form_group_structure(self, page: Page, notification_page):
        """Test that form groups are properly structured.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - Each form field is wrapped in a form-group div
        - Form groups are visible
        """
        notification_page.navigate()
        
        form_groups = page.locator('.form-group')
        
        # Should have at least 4 form groups (type, recipient, subject, message)
        # Subject may be hidden for non-EMAIL types, but the form-group should still exist
        assert form_groups.count() >= 4, "Should have at least 4 form groups"
        
        # Verify all visible form groups are visible
        for i in range(form_groups.count()):
            form_group = form_groups.nth(i)
            # Form groups should be visible or hidden based on their content
            # At minimum, type, recipient, and message should be visible
            if i < 3:  # First 3 should always be visible
                assert form_group.is_visible(), f"Form group {i} should be visible"
    
    def test_recipient_placeholder_changes_with_type(self, page: Page, notification_page):
        """Test that the recipient input placeholder changes based on notification type.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - EMAIL type shows email placeholder
        - SMS type shows phone number placeholder
        - WHATSAPP type shows phone number placeholder
        """
        notification_page.navigate()
        
        recipient_input = page.locator('[data-testid="recipient"]')
        
        # Check EMAIL placeholder
        notification_page.select_type('EMAIL')
        email_placeholder = recipient_input.get_attribute('placeholder')
        assert 'example.com' in email_placeholder, "EMAIL type should show email placeholder"
        
        # Check SMS placeholder
        notification_page.select_type('SMS')
        sms_placeholder = recipient_input.get_attribute('placeholder')
        assert '+34' in sms_placeholder, "SMS type should show phone number placeholder"
        
        # Check WHATSAPP placeholder
        notification_page.select_type('WHATSAPP')
        whatsapp_placeholder = recipient_input.get_attribute('placeholder')
        assert '+34' in whatsapp_placeholder, "WHATSAPP type should show phone number placeholder"
    
    def test_form_has_no_initial_errors(self, page: Page, notification_page):
        """Test that the form has no error states initially.
        
        Validates: Requirements 6.1, 11.1
        
        Verifies that:
        - No form fields have error class
        - No error messages are displayed
        """
        notification_page.navigate()
        
        # Check that no form fields have error class
        error_inputs = page.locator('input.error, textarea.error, select.error')
        assert error_inputs.count() == 0, "No form fields should have error class initially"
        
        # Check that no error messages are displayed
        error_messages = page.locator('.error-message')
        assert error_messages.count() == 0, "No error messages should be displayed initially"
