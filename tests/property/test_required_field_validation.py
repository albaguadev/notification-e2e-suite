"""
Property-based tests for required field validation.

This module tests that required field validation prevents form submission
and displays appropriate validation errors when required fields are missing.

**Validates: Requirements 2.4, 2.6**

Property 3: Required Field Validation
- For any form submission attempt with one or more missing required fields (type, recipient, or message),
  the React application SHALL prevent submission and display validation errors.
"""

import pytest
from hypothesis import given, settings, Verbosity, HealthCheck, strategies as st
from playwright.sync_api import Page


class TestRequiredFieldValidation:
    """Test suite for verifying required field validation prevents submission."""
    
    @given(
        notification_type=st.sampled_from(['EMAIL', 'SMS', 'WHATSAPP']),
        recipient=st.one_of(st.just(''), st.just('   ')),  # Generate empty or whitespace recipient
        message=st.text(min_size=1, max_size=100)
    )
    @settings(max_examples=15, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_missing_recipient_field_prevents_submission(self, page: Page, notification_page, notification_type, recipient, message):
        """Property test: Missing recipient field prevents form submission and shows error.
        
        **Validates: Requirements 2.4, 2.6**
        
        For any notification type with missing (empty or whitespace) recipient field:
        1. Navigate to the application
        2. Select the notification type
        3. Leave recipient field empty or whitespace-only
        4. Fill message field
        5. Verify validation error is displayed for recipient
        6. Verify form submission is prevented
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_type: Type of notification (EMAIL, SMS, WHATSAPP)
            recipient: Empty or whitespace recipient (invalid)
            message: Valid message content
        """
        # Navigate to the application
        notification_page.navigate()
        
        # Select notification type
        notification_page.select_type(notification_type)
        
        # Set up route handler to track if form submission is attempted
        submission_attempted = []
        
        def handle_route(route):
            """Intercept API requests to track submission attempts."""
            if '/api/v1/notifications' in route.request.url:
                submission_attempted.append(True)
            route.abort()
        
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with missing recipient
        recipient_input = page.locator('[data-testid="recipient"]')
        message_input = page.locator('[data-testid="message"]')
        
        # Set recipient to empty or whitespace
        recipient_input.fill(recipient)
        recipient_input.blur()
        
        # Fill message
        message_input.fill(message)
        
        # Wait a bit for validation to occur
        page.wait_for_timeout(200)
        
        # Try to submit the form
        notification_page.submit()
        
        # Wait a bit to see if submission occurs
        page.wait_for_timeout(500)
        
        # Verify validation error is displayed for recipient
        recipient_error = page.locator('[data-testid="recipient-error"]')
        assert recipient_error.is_visible(), \
            f"Recipient error should be visible for {notification_type} with empty recipient. " \
            f"Recipient value: '{recipient}'"
        
        # Verify API request was NOT sent (form submission was prevented)
        assert len(submission_attempted) == 0, \
            f"Form submission should be prevented when recipient is missing for {notification_type}. " \
            f"Expected 0 API requests, got {len(submission_attempted)}"
    
    @given(
        notification_type=st.sampled_from(['EMAIL', 'SMS', 'WHATSAPP']),
        recipient=st.one_of(
            st.emails(),
            st.from_regex(r'\+34[67]\d{8}', fullmatch=True),
            st.from_regex(r'\+\d{7,15}', fullmatch=True)
        ),
        message=st.one_of(st.just(''), st.just('   '))  # Generate empty or whitespace message
    )
    @settings(max_examples=15, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_missing_message_field_prevents_submission(self, page: Page, notification_page, notification_type, recipient, message):
        """Property test: Missing message field prevents form submission and shows error.
        
        **Validates: Requirements 2.4, 2.6**
        
        For any notification type with missing (empty or whitespace) message field:
        1. Navigate to the application
        2. Select the notification type
        3. Fill recipient field
        4. Leave message field empty or whitespace-only
        5. Verify validation error is displayed for message
        6. Verify form submission is prevented
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_type: Type of notification (EMAIL, SMS, WHATSAPP)
            recipient: Valid recipient address/phone
            message: Empty or whitespace message (invalid)
        """
        # Navigate to the application
        notification_page.navigate()
        
        # Select notification type
        notification_page.select_type(notification_type)
        
        # Set up route handler to track if form submission is attempted
        submission_attempted = []
        
        def handle_route(route):
            """Intercept API requests to track submission attempts."""
            if '/api/v1/notifications' in route.request.url:
                submission_attempted.append(True)
            route.abort()
        
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with missing message
        recipient_input = page.locator('[data-testid="recipient"]')
        message_input = page.locator('[data-testid="message"]')
        
        # Fill recipient
        recipient_input.fill(recipient)
        
        # Set message to empty or whitespace
        message_input.fill(message)
        message_input.blur()
        
        # Wait a bit for validation to occur
        page.wait_for_timeout(200)
        
        # Try to submit the form
        notification_page.submit()
        
        # Wait a bit to see if submission occurs
        page.wait_for_timeout(500)
        
        # Verify validation error is displayed for message
        message_error = page.locator('[data-testid="message-error"]')
        assert message_error.is_visible(), \
            f"Message error should be visible for {notification_type} with empty message. " \
            f"Message value: '{message}'"
        
        # Verify API request was NOT sent (form submission was prevented)
        assert len(submission_attempted) == 0, \
            f"Form submission should be prevented when message is missing for {notification_type}. " \
            f"Expected 0 API requests, got {len(submission_attempted)}"
    
    @given(
        recipient=st.one_of(st.just(''), st.just('   ')),  # Missing recipient
        message=st.one_of(st.just(''), st.just('   '))    # Missing message
    )
    @settings(max_examples=10, verbosity=Verbosity.quiet, suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], deadline=None)
    @pytest.mark.property_test
    def test_multiple_missing_fields_prevents_submission(self, page: Page, notification_page, recipient, message):
        """Property test: Multiple missing fields prevent form submission and show multiple errors.
        
        **Validates: Requirements 2.4, 2.6**
        
        For any form submission attempt with multiple missing required fields:
        1. Navigate to the application
        2. Select a notification type
        3. Leave multiple required fields empty or whitespace-only
        4. Verify validation errors are displayed for all missing fields
        5. Verify form submission is prevented
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            recipient: Empty or whitespace recipient (invalid)
            message: Empty or whitespace message (invalid)
        """
        # Navigate to the application
        notification_page.navigate()
        
        # Select a type
        notification_page.select_type('EMAIL')
        
        # Set up route handler to track if form submission is attempted
        submission_attempted = []
        
        def handle_route(route):
            """Intercept API requests to track submission attempts."""
            if '/api/v1/notifications' in route.request.url:
                submission_attempted.append(True)
            route.abort()
        
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with multiple missing fields
        recipient_input = page.locator('[data-testid="recipient"]')
        message_input = page.locator('[data-testid="message"]')
        
        # Leave both empty
        recipient_input.fill(recipient)
        recipient_input.blur()
        
        message_input.fill(message)
        message_input.blur()
        
        # Wait a bit for validation to occur
        page.wait_for_timeout(200)
        
        # Try to submit the form
        notification_page.submit()
        
        # Wait a bit to see if submission occurs
        page.wait_for_timeout(500)
        
        # Verify both validation errors are displayed
        recipient_error = page.locator('[data-testid="recipient-error"]')
        message_error = page.locator('[data-testid="message-error"]')
        
        assert recipient_error.is_visible(), \
            f"Recipient error should be visible when missing (value: '{recipient}')"
        assert message_error.is_visible(), \
            f"Message error should be visible when missing (value: '{message}')"
        
        # Verify API request was NOT sent (form submission was prevented)
        assert len(submission_attempted) == 0, \
            f"Form submission should be prevented with multiple missing fields. " \
            f"Expected 0 API requests, got {len(submission_attempted)}"
    

