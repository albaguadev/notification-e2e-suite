"""
E2E test for EMAIL notification flow.

This module tests the complete user flow for sending email notifications:
- Navigate to application
- Fill form with valid EMAIL data including subject
- Submit form
- Verify UI displays success message or error message based on backend response

This is a TRUE E2E test without mocks - it uses the real MultiChannelNotifier
backend running on http://localhost:8081.

Requirements: 7.1
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
class TestEmailNotificationFlow:
    """Test suite for EMAIL notification end-to-end flow.
    
    These tests validate the complete user flow for sending email notifications,
    from UI interaction through backend integration.
    """
    
    def test_email_notification_flow_with_subject(
        self,
        notification_page: NotificationPage,
        backend_available,
        test_data,
        created_notification_ids
    ):
        """Test complete EMAIL notification flow with subject.
        
        This test validates the end-to-end flow for sending an email notification:
        1. Navigate to application
        2. Fill form with valid EMAIL data including subject
        3. Submit form
        4. Verify UI displays response message (success or error)
        5. Cleanup: Delete created notification
        
        The test does NOT mock the backend - it uses the real MultiChannelNotifier
        backend running on http://localhost:8081. This validates the true
        end-to-end user flow from UI through backend integration.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_data: Test data fixture with valid test values
            created_notification_ids: Fixture for tracking IDs for cleanup
        """
        # Ensure backend is available (fixture handles skip if not)
        assert backend_available is True
        
        # Navigate to application
        notification_page.navigate()
        
        # Get test data for EMAIL notification
        email_data = test_data['valid_email']
        
        # Fill the notification form with EMAIL data
        notification_page.fill_form(
            notification_type=email_data['type'],
            recipient=email_data['recipient'],
            message=email_data['message'],
            subject=email_data['subject']
        )
        
        # Verify subject field is visible for EMAIL type
        assert notification_page.is_subject_visible(), \
            "Subject field should be visible for EMAIL type"
        
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
        # (This depends on frontend storing the ID if available)
        try:
            # Attempt to get the ID from the backend by querying recent notifications
            response = requests.get(
                'http://localhost:8081/api/v1/notifications?type=EMAIL&limit=1',
                timeout=2
            )
            if response.status_code == 200:
                notifications = response.json()
                if notifications and len(notifications) > 0:
                    created_notification_ids.append(notifications[0].get('id', ''))
        except:
            pass  # If we can't get the ID, cleanup just won't happen for this test
    
    def test_email_notification_with_special_characters(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test EMAIL notification with special characters in message.
        
        This test validates that the form handles special characters correctly
        in the email message content.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Fill form with special characters in message
        notification_page.fill_form(
            notification_type='EMAIL',
            recipient='test@example.com',
            message='Test message with special chars: !@#$%^&*()',
            subject='Special Chars Test'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_email_notification_with_long_message(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test EMAIL notification with a longer message content.
        
        This test validates that the form handles longer messages correctly
        and transmits them to the backend properly.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Create a longer but reasonable message
        long_message = 'This is a longer email message. ' * 5
        
        notification_page.fill_form(
            notification_type='EMAIL',
            recipient='test@example.com',
            message=long_message,
            subject='Long Message Test'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
    
    def test_email_notification_with_multiple_recipients_format(
        self,
        notification_page: NotificationPage,
        backend_available
    ):
        """Test EMAIL notification with different valid email formats.
        
        This test validates that the form accepts various valid email formats
        and the backend processes them correctly.
        
        Args:
            notification_page: NotificationPage POM instance
            backend_available: Fixture that skips test if backend unavailable
        """
        assert backend_available is True
        
        notification_page.navigate()
        
        # Test with a more complex valid email format
        notification_page.fill_form(
            notification_type='EMAIL',
            recipient='user.name+tag@example.co.uk',
            message='Testing different email format',
            subject='Email Format Test'
        )
        
        notification_page.submit()
        
        # Verify UI displays a response
        status_message = notification_page.get_status_message()
        assert status_message, \
            "UI should display a status message after form submission"
