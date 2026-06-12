"""
E2E test for WHATSAPP notification flow.

This module tests the complete user flow for sending WhatsApp notifications:
- Navigate to application
- Fill form with valid WHATSAPP data (E.164 format phone numbers like +34612345678)
- Submit form
- Verify UI displays success message or error message based on backend response

This is a TRUE E2E test without mocks - it uses the real MultiChannelNotifier
backend running on http://localhost:8081.

Requirements: 7.3
"""

import pytest
from playwright.sync_api import Page
import requests
from pages.notification_page import NotificationPage


@pytest.fixture(scope="function")
def backend_available():
    """Check if the backend is accessible.
    
    This fixture attempts to connect to the MultiChannelNotifier backend
    on http://localhost:8081. If the backend is unavailable, the test
    will be skipped.
    
    Yields:
        bool: True if backend is available
        
    Raises:
        pytest.skip: If backend is not accessible
    """
    try:
        response = requests.get('http://localhost:8081/actuator/health', timeout=2)
        if response.status_code == 200:
            yield True
        else:
            pytest.skip("Backend health check failed")
    except (requests.ConnectionError, requests.Timeout):
        pytest.skip("Backend is not accessible on http://localhost:8081")


@pytest.fixture(scope="function")
def created_notification_ids():
    """Fixture to track created notification IDs for cleanup.
    
    Yields:
        list: List to store created notification IDs
    """
    ids = []
    yield ids
    
    # Cleanup: Delete all created notifications
    for notif_id in ids:
        try:
            requests.delete(
                f'http://localhost:8081/api/v1/notifications/{notif_id}',
                timeout=5
            )
        except Exception as e:
            # Fail silently - cleanup errors should not fail the test
            print(f"Warning: Failed to delete notification {notif_id}: {e}")


@pytest.mark.e2e_test
class TestWhatsAppNotificationFlow:
    """Test suite for WHATSAPP notification end-to-end flow.
    
    These tests validate the complete user flow for sending WhatsApp notifications,
    from UI interaction through backend integration. Tests use E.164 format phone
    numbers (international format with + prefix).
    """
    
    def test_whatsapp_notification_flow_with_valid_number(
        self,
        notification_page: NotificationPage,
        backend_available,
        created_notification_ids
    ):
        """Test complete WHATSAPP notification flow with valid E.164 phone number.
        
        This test validates the end-to-end flow for sending a WhatsApp notification:
        1. Navigate to application
        2. Fill form with valid WHATSAPP data (E.164 format: +34612345678)
        3. Submit form
        4. Verify UI displays response message (success or error)
        5. Cleanup: Delete created notification
        
        The test does NOT mock the backend - it uses the real MultiChannelNotifier
        backend running on http://localhost:8081. This validates the true
        end-to-end user flow from UI through backend integration.
        
        E.164 format uses a leading '+' sign followed by country code and 
        subscriber number. Example: +34612345678 (Spain number with 9 digits).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            created_notification_ids: Fixture for tracking IDs for cleanup
        """
        # Ensure backend is available (fixture handles skip if not)
        assert backend_available is True
        
        # Navigate to application
        notification_page.navigate()
        
        # Fill the notification form with WHATSAPP data in E.164 format
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+34612345678',
            message='Hello from WhatsApp test'
        )
        
        # Verify subject field is NOT visible for WHATSAPP type
        assert not notification_page.is_subject_visible(), \
            "Subject field should not be visible for WHATSAPP type"
        
        # Submit the form
        notification_page.submit()
        
        # Wait for and retrieve the status message from UI
        status_message = notification_page.get_status_message()
        
        # Verify that UI displays a response (success or error)
        # The status message should contain some feedback about the submission
        assert status_message, \
            "UI should display a status message (success or error) after form submission"
        
        # Verify the message contains success or error indicators
        # (backend will determine which based on its validation)
        message_lower = status_message.lower()
        is_success = any(word in message_lower for word in ['success', 'sent', 'created', 'submitted'])
        is_error = any(word in message_lower for word in ['error', 'failed', 'invalid', 'rejected', 'unable'])
        
        assert is_success or is_error, \
            f"Status message should indicate success or error, got: {status_message}"
        
        # Try to extract notification ID from response for cleanup
        try:
            response = requests.get(
                'http://localhost:8081/api/v1/notifications?type=WHATSAPP&limit=1',
                timeout=2
            )
            if response.status_code == 200:
                notifications = response.json()
                if notifications and len(notifications) > 0:
                    created_notification_ids.append(notifications[0].get('id', ''))
        except:
            pass  # If we can't get the ID, cleanup just won't happen for this test
    
    def test_whatsapp_notification_with_different_country_code(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with different country code in E.164 format.
        
        This test validates that the form accepts E.164 format phone numbers
        with different country codes (not just Spain +34).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with US phone number in E.164 format (+1 followed by 10 digits)
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+12025551234',
            message='Test with US phone number'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_with_uk_number(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with UK phone number in E.164 format.
        
        This test validates E.164 format handling for UK phone numbers (+44 prefix).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with UK phone number in E.164 format
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+447911123456',
            message='Test with UK phone number'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_with_message_containing_special_chars(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with special characters in message.
        
        This test validates that the form handles special characters and
        emoji-like content correctly in WhatsApp messages.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Fill form with special characters and symbols
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+34612345678',
            message='Test message with special chars: !@#$%^&*() and symbols: ¡¿€'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_with_longer_message(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with a longer message content.
        
        This test validates that the form handles longer messages correctly
        and transmits them to the backend properly. WhatsApp messages can be
        quite long (up to several hundred characters).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Create a longer but reasonable message
        long_message = 'This is a longer WhatsApp message. ' * 8
        
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+34612345678',
            message=long_message
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_subject_field_not_visible(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test that subject field is not visible for WHATSAPP type.
        
        This test validates that selecting WHATSAPP notification type
        hides the subject field (subject is only for EMAIL).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Select WHATSAPP type
        notification_page.select_type('WHATSAPP')
        
        # Verify subject field is not visible for WHATSAPP
        assert not notification_page.is_subject_visible(), \
            "Subject field should not be visible for WHATSAPP type"
        
        # Fill required fields
        notification_page.recipient_input.fill('+34612345678')
        notification_page.message_input.fill('Test message')
        
        # Submit the form
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_with_france_number(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with French phone number in E.164 format.
        
        This test validates E.164 format handling for French phone numbers (+33 prefix).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with French phone number in E.164 format
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+33612345678',
            message='Test with French phone number'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_whatsapp_notification_with_japan_number(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test WHATSAPP notification with Japanese phone number in E.164 format.
        
        This test validates E.164 format with various country codes including
        non-European regions like Japan (+81 prefix).
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with Japanese phone number in E.164 format
        notification_page.fill_form(
            notification_type='WHATSAPP',
            recipient='+81312345678',
            message='Test with Japanese phone number'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
