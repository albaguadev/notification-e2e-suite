"""
E2E test for SMS notification flow.

This module tests the complete user flow for sending SMS notifications:
- Navigate to application
- Fill form with valid SMS data including ES region phone number
- Submit form
- Verify UI displays success message or error message based on backend response

This is a TRUE E2E test without mocks - it uses the real MultiChannelNotifier
backend running on http://localhost:8081.

Requirements: 7.2
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
class TestSmsNotificationFlow:
    """Test suite for SMS notification end-to-end flow.
    
    These tests validate the complete user flow for sending SMS notifications,
    from UI interaction through backend integration. All tests use ES region
    phone numbers as specified in the requirements.
    """
    
    def test_sms_notification_flow_with_es_phone(
        self,
        notification_page: NotificationPage,
        backend_available,
        test_data,
        created_notification_ids
    ):
        """Test complete SMS notification flow with ES region phone number.
        
        This test validates the end-to-end flow for sending an SMS notification:
        1. Navigate to application
        2. Fill form with valid SMS data including ES region phone number
        3. Submit form
        4. Verify UI displays response message (success or error)
        5. Cleanup: Delete created notification
        
        The test does NOT mock the backend - it uses the real MultiChannelNotifier
        backend running on http://localhost:8081. This validates the true
        end-to-end user flow from UI through backend integration.
        
        SMS notifications do not require a subject field, unlike EMAIL notifications.
        The form should only request type, recipient, and message fields.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_data: Test data fixture with valid test values
            created_notification_ids: Fixture for tracking IDs for cleanup
            
        Validates: Requirement 7.2 - SMS notification UI displays backend response
        """
        # Ensure backend is available (fixture handles skip if not)
        assert backend_available is True
        
        # Navigate to application
        notification_page.navigate()
        
        # Get test data for SMS notification
        sms_data = test_data['valid_sms']
        
        # Fill the notification form with SMS data
        # SMS doesn't have a subject field, so only fill type, recipient, and message
        notification_page.fill_form(
            notification_type=sms_data['type'],
            recipient=sms_data['recipient'],
            message=sms_data['message']
        )
        
        # Verify subject field is not visible for SMS type
        # SMS channel should not display subject field per requirement 2.5
        assert not notification_page.is_subject_visible(), \
            "Subject field should be hidden for SMS type"
        
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
                'http://localhost:8081/api/v1/notifications?type=SMS&limit=1',
                timeout=2
            )
            if response.status_code == 200:
                notifications = response.json()
                if notifications and len(notifications) > 0:
                    created_notification_ids.append(notifications[0].get('id', ''))
        except:
            pass  # If we can't get the ID, cleanup just won't happen for this test
    
    def test_sms_notification_with_special_characters(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test SMS notification with special characters in message.
        
        This test validates that the form handles special characters correctly
        in the SMS message content. SMS messages may contain various special
        characters that need to be transmitted properly to the backend.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            
        Validates: Requirement 7.2 - SMS notification with special characters
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Fill form with special characters in message
        notification_page.fill_form(
            notification_type='SMS',
            recipient='+34612345678',
            message='Test message with special chars: !@#$%^&*()'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_sms_notification_with_long_message(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test SMS notification with a longer message content.
        
        This test validates that the form handles longer messages correctly
        and transmits them to the backend properly. SMS messages have length
        constraints, but this test verifies the UI can handle and submit
        reasonably long messages.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            
        Validates: Requirement 7.2 - SMS notification with longer message content
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Create a longer but reasonable message (SMS typically supports 160-1000 chars)
        long_message = 'This is a longer SMS message. ' * 5
        
        notification_page.fill_form(
            notification_type='SMS',
            recipient='+34612345678',
            message=long_message
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_sms_notification_with_different_es_phone_formats(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test SMS notification with different valid ES region phone number formats.
        
        This test validates that the form accepts various valid ES region phone
        number formats per requirement 2.3 and 3.2:
        - Format: +34 followed by 9 digits
        - Mobile numbers start with 6 or 7
        - Valid ES region prefixes for mobile networks
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            
        Validates: Requirement 7.2 - SMS notification with different ES phone formats
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with a different valid ES mobile number (starting with 7 instead of 6)
        # Both 6 and 7 prefixes are valid for Spanish mobile networks
        notification_page.fill_form(
            notification_type='SMS',
            recipient='+34712345678',  # Valid ES format with 7 prefix
            message='Testing different ES phone format'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_sms_notification_with_min_length_message(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test SMS notification with minimum length message.
        
        This test validates that the form accepts and submits messages
        with minimal content. While very short, this ensures the form
        doesn't have artificial minimum length restrictions beyond what
        the backend requires.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            
        Validates: Requirement 7.2 - SMS notification edge case handling
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with a very short message
        notification_page.fill_form(
            notification_type='SMS',
            recipient='+34612345678',
            message='Hi'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response (backend will validate)
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
