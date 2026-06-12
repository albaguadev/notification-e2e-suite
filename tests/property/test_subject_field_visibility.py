"""
Property-based tests for subject field visibility based on notification type.

This module tests that the subject field is hidden for non-EMAIL notification types
(SMS and WHATSAPP) and only visible for EMAIL notifications.

**Validates: Requirements 2.5**

Property 4: Subject Field Visibility
- For any non-EMAIL notification type selection (SMS or WHATSAPP), the React application 
  SHALL hide the subject field from the UI.
"""

import pytest
from hypothesis import given, settings, Verbosity, HealthCheck, assume
from playwright.sync_api import Page
from tests.utils.generators import valid_notifications


class TestSubjectFieldVisibility:
    """Test suite for verifying subject field visibility based on notification type."""
    
    @given(notification_data=valid_notifications())
    @settings(max_examples=25, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_subject_field_hidden_for_non_email_types(self, page: Page, notification_page, notification_data):
        """Property test: Subject field is hidden for SMS and WHATSAPP notification types.
        
        **Validates: Requirements 2.5**
        
        For any non-EMAIL notification type (SMS or WHATSAPP):
        1. Navigate to the application
        2. Select the non-EMAIL notification type (SMS or WHATSAPP)
        3. Verify the subject field is NOT visible in the UI
        4. Fill other form fields (recipient, message)
        5. Re-verify subject field remains hidden
        
        This property ensures that the subject field is exclusively shown for EMAIL 
        notifications and is hidden from SMS and WHATSAPP type notifications.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
                For non-EMAIL types:
                {
                    'type': 'SMS'|'WHATSAPP',
                    'recipient': str,
                    'message': str
                }
        """
        # Only test non-EMAIL notification types
        notification_type = notification_data['type']
        assume(notification_type in ['SMS', 'WHATSAPP'])
        
        # Navigate to the application
        notification_page.navigate()
        
        # Select the notification type
        notification_page.select_type(notification_type)
        
        # Assertion 1: Verify subject field is NOT visible after type selection
        assert not notification_page.is_subject_visible(), \
            f"Subject field should NOT be visible for {notification_type} type notification. " \
            f"But it was visible after selecting type {notification_type}."
        
        # Fill the form with non-EMAIL notification data
        recipient = notification_data['recipient']
        message = notification_data['message']
        
        notification_page.recipient_input.fill(recipient)
        notification_page.message_input.fill(message)
        
        # Assertion 2: Verify subject field is still NOT visible after filling other fields
        assert not notification_page.is_subject_visible(), \
            f"Subject field should NOT be visible for {notification_type} type notification " \
            f"even after filling recipient and message fields. " \
            f"Notification type: {notification_type}, recipient: {recipient}"
    
    @given(notification_data=valid_notifications())
    @settings(max_examples=25, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_subject_field_visible_for_email_type(self, page: Page, notification_page, notification_data):
        """Property test: Subject field is visible for EMAIL notification type.
        
        **Validates: Requirements 2.5**
        
        For any EMAIL notification type:
        1. Navigate to the application
        2. Select EMAIL notification type
        3. Verify the subject field IS visible in the UI
        4. Fill form including subject field
        5. Verify subject field remains visible
        
        This property ensures that the subject field is shown exclusively for EMAIL 
        notifications and can be properly filled by users.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
                For EMAIL type:
                {
                    'type': 'EMAIL',
                    'recipient': str,
                    'message': str,
                    'subject': str
                }
        """
        # Only test EMAIL notification type
        notification_type = notification_data['type']
        assume(notification_type == 'EMAIL')
        
        # Navigate to the application
        notification_page.navigate()
        
        # Select EMAIL notification type
        notification_page.select_type(notification_type)
        
        # Assertion 1: Verify subject field IS visible after type selection
        assert notification_page.is_subject_visible(), \
            f"Subject field SHOULD be visible for EMAIL notification type. " \
            f"But it was not visible after selecting type {notification_type}."
        
        # Fill the form with EMAIL notification data
        recipient = notification_data['recipient']
        message = notification_data['message']
        subject = notification_data['subject']
        
        notification_page.recipient_input.fill(recipient)
        notification_page.message_input.fill(message)
        notification_page.subject_input.fill(subject)
        
        # Assertion 2: Verify subject field is still visible after filling all fields
        assert notification_page.is_subject_visible(), \
            f"Subject field SHOULD remain visible for EMAIL type notification " \
            f"after filling all form fields. " \
            f"Notification type: {notification_type}, recipient: {recipient}"
    
    @given(notification_data=valid_notifications())
    @settings(max_examples=25, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_subject_field_visibility_consistency(self, page: Page, notification_page, notification_data):
        """Property test: Subject field visibility is consistent with notification type.
        
        **Validates: Requirements 2.5**
        
        For any notification type:
        1. Navigate to the application
        2. Select the notification type
        3. Verify subject visibility matches expected behavior:
           - EMAIL: subject field SHOULD be visible
           - SMS/WHATSAPP: subject field should NOT be visible
        4. Verify consistency remains after form interaction
        
        This comprehensive property test ensures that subject field visibility 
        is consistently tied to the notification type throughout the user interaction.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
        """
        notification_type = notification_data['type']
        is_email = notification_type == 'EMAIL'
        
        # Navigate to the application
        notification_page.navigate()
        
        # Select the notification type
        notification_page.select_type(notification_type)
        
        # Get actual visibility state
        is_subject_visible = notification_page.is_subject_visible()
        
        # Assertion 1: Verify visibility matches expected behavior
        if is_email:
            assert is_subject_visible, \
                f"Subject field should be visible for EMAIL type, but was hidden. " \
                f"Notification type: {notification_type}"
        else:
            assert not is_subject_visible, \
                f"Subject field should NOT be visible for {notification_type} type, but was visible. " \
                f"Notification type: {notification_type}"
        
        # Fill form with notification data
        recipient = notification_data['recipient']
        message = notification_data['message']
        
        notification_page.recipient_input.fill(recipient)
        notification_page.message_input.fill(message)
        
        # If EMAIL, also fill subject
        if is_email:
            subject = notification_data.get('subject', '')
            if subject:
                notification_page.subject_input.fill(subject)
        
        # Assertion 2: Verify visibility remains consistent after form filling
        is_subject_visible_after = notification_page.is_subject_visible()
        assert is_subject_visible == is_subject_visible_after, \
            f"Subject field visibility should remain consistent after form filling. " \
            f"Initial visibility: {is_subject_visible}, Final visibility: {is_subject_visible_after}, " \
            f"Notification type: {notification_type}"
        
        # Assertion 3: Final verification of expected state
        if is_email:
            assert is_subject_visible_after, \
                f"Subject field should remain visible for EMAIL type after form filling. " \
                f"Notification type: {notification_type}, recipient: {recipient}"
        else:
            assert not is_subject_visible_after, \
                f"Subject field should remain hidden for {notification_type} type after form filling. " \
                f"Notification type: {notification_type}, recipient: {recipient}"
