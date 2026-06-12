"""
Property-based tests for channel type support.

This module tests that the React application correctly handles all supported
notification channel types (EMAIL, SMS, WHATSAPP) and submits them to the
backend with the appropriate channel-specific format.

**Validates: Requirements 3.2**

Property 5: Channel Type Support
- For any valid notification data of type EMAIL, SMS, or WHATSAPP, the React 
  application SHALL handle the submission correctly and communicate with the 
  backend using the appropriate channel-specific format.
"""

import pytest
import json
from hypothesis import given, settings, Verbosity, HealthCheck, assume, strategies as st
from playwright.sync_api import Page
from tests.utils.generators import (
    valid_notifications,
    valid_emails,
    valid_sms_numbers,
    valid_whatsapp_numbers,
    valid_messages,
    valid_subjects
)


class TestChannelTypeSupport:
    """Test suite for verifying channel type support across EMAIL, SMS, and WHATSAPP."""
    
    @given(
        email_data=valid_notifications(notification_type='EMAIL'),
        sms_data=valid_notifications(notification_type='SMS'),
        whatsapp_data=valid_notifications(notification_type='WHATSAPP')
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_all_channel_types_submission(self, page: Page, notification_page, email_data, sms_data, whatsapp_data):
        """Property test: All channel types (EMAIL, SMS, WHATSAPP) are supported and submitted correctly.
        
        **Validates: Requirements 3.2**
        
        For any valid notification data of each channel type:
        1. Generate valid notification data for EMAIL, SMS, and WHATSAPP types
        2. For each type, submit the notification through the UI
        3. Intercept the network request to verify:
           - The notification is submitted to the correct endpoint
           - The channel-specific format is correct:
             * EMAIL: includes type, recipient (email), message, and optional subject
             * SMS: includes type, recipient (ES phone), message, NO subject
             * WHATSAPP: includes type, recipient (E.164 phone), message, NO subject
           - No authentication headers are present
        4. Verify all three channel types work correctly across multiple iterations
        
        This comprehensive property test ensures that the React application
        correctly supports all three notification channel types and formats
        each request appropriately for the backend.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            email_data: Valid EMAIL notification data from Hypothesis
            sms_data: Valid SMS notification data from Hypothesis
            whatsapp_data: Valid WHATSAPP notification data from Hypothesis
        """
        # Collect test data for all three types
        test_data_sets = [
            ('EMAIL', email_data),
            ('SMS', sms_data),
            ('WHATSAPP', whatsapp_data)
        ]
        
        for channel_type, notification_data in test_data_sets:
            # List to capture intercepted requests for this channel
            intercepted_requests = []
            
            def handle_route(route):
                """Intercept and capture API requests."""
                if '/api/v1/notifications' in route.request.url:
                    intercepted_requests.append({
                        'url': route.request.url,
                        'method': route.request.method,
                        'headers': dict(route.request.headers),
                        'body': route.request.post_data_json if route.request.method == 'POST' else None
                    })
                
                # Mock a successful response
                route.abort()
            
            # Navigate to the application
            notification_page.navigate()
            
            # Set up route handler to intercept requests
            page.route('**/api/v1/notifications', handle_route)
            
            # Extract notification data
            notif_type = notification_data['type']
            recipient = notification_data['recipient']
            message = notification_data['message']
            subject = notification_data.get('subject')
            
            # Verify the data type matches expected channel
            assert notif_type == channel_type, \
                f"Generated notification type {notif_type} should match expected channel type {channel_type}"
            
            # Fill the form with notification data
            notification_page.fill_form(notif_type, recipient, message, subject)
            
            # Submit the form
            notification_page.submit()
            
            # Verify a request was intercepted
            assert len(intercepted_requests) > 0, \
                f"Expected POST request for {channel_type} notification, but got none. " \
                f"Recipient: {recipient}, Message: {message[:50]}..."
            
            # Get the first request (the form submission)
            request_data = intercepted_requests[0]
            request_body = request_data['body']
            
            # Assertion 1: Verify correct endpoint
            assert '/api/v1/notifications' in request_data['url'], \
                f"Request URL should contain /api/v1/notifications for {channel_type}, got: {request_data['url']}"
            
            # Assertion 2: Verify correct HTTP method
            assert request_data['method'] == 'POST', \
                f"Request method should be POST for {channel_type}, got: {request_data['method']}"
            
            # Assertion 3: Verify Content-Type header
            content_type = request_data['headers'].get('content-type', '').lower()
            assert 'application/json' in content_type or content_type == 'application/json', \
                f"Content-Type should be application/json for {channel_type}, got: {request_data['headers'].get('content-type')}"
            
            # Assertion 4: Verify request body structure and required fields
            assert request_body is not None, \
                f"Request body should not be None for {channel_type}"
            
            assert isinstance(request_body, dict), \
                f"Request body should be JSON object for {channel_type}, got: {type(request_body)}"
            
            # Assertion 5: Verify type field
            assert 'type' in request_body, \
                f"Request body should contain 'type' field for {channel_type}. Got: {request_body}"
            assert request_body['type'] == channel_type, \
                f"Request type should be {channel_type}, got: {request_body['type']}"
            
            # Assertion 6: Verify recipient field
            assert 'recipient' in request_body, \
                f"Request body should contain 'recipient' field for {channel_type}. Got: {request_body}"
            assert request_body['recipient'] == recipient, \
                f"Request recipient should match input for {channel_type}. " \
                f"Expected: {recipient}, Got: {request_body['recipient']}"
            
            # Assertion 7: Verify message field
            assert 'message' in request_body, \
                f"Request body should contain 'message' field for {channel_type}. Got: {request_body}"
            assert request_body['message'] == message, \
                f"Request message should match input for {channel_type}. " \
                f"Expected: {message}, Got: {request_body['message']}"
            
            # Assertion 8: Verify channel-specific format
            if channel_type == 'EMAIL':
                # EMAIL channel may include subject if provided
                if subject and subject.strip():
                    assert 'subject' in request_body, \
                        f"EMAIL request should include non-empty subject field. Got: {request_body}"
                    assert request_body['subject'] == subject, \
                        f"EMAIL subject should match input. Expected: {subject}, Got: {request_body['subject']}"
            else:
                # SMS and WHATSAPP should NOT include subject
                assert 'subject' not in request_body, \
                    f"{channel_type} request should NOT include subject field. Got: {request_body}"
            
            # Assertion 9: Verify recipient format is correct for channel type
            recipient_value = request_body['recipient']
            
            if channel_type == 'EMAIL':
                # EMAIL recipient should be a valid email address (must contain @)
                assert '@' in recipient_value, \
                    f"EMAIL recipient should contain @. Got: {recipient_value}"
                assert '.' in recipient_value.split('@')[1], \
                    f"EMAIL recipient should have valid domain. Got: {recipient_value}"
            elif channel_type == 'SMS':
                # SMS recipient should be in +34 format (ES region)
                assert recipient_value.startswith('+34'), \
                    f"SMS recipient should start with +34 (ES region). Got: {recipient_value}"
                assert len(recipient_value) == 12, \
                    f"SMS recipient should be 12 characters (+34 + 9 digits). Got: {recipient_value} (length: {len(recipient_value)})"
                assert recipient_value[3] in ['6', '7'], \
                    f"SMS recipient should start with +346 or +347. Got: {recipient_value}"
            elif channel_type == 'WHATSAPP':
                # WHATSAPP recipient should be in E.164 format (+ prefix)
                assert recipient_value.startswith('+'), \
                    f"WHATSAPP recipient should start with +. Got: {recipient_value}"
                assert len(recipient_value) >= 8 and len(recipient_value) <= 16, \
                    f"WHATSAPP recipient should be 8-16 characters (E.164 format). Got: {recipient_value} (length: {len(recipient_value)})"
            
            # Assertion 10: Verify no authentication headers
            auth_headers = ['authorization', 'auth', 'x-auth-token', 'x-api-key', 'cookie', 'x-csrf-token']
            for auth_header in auth_headers:
                assert auth_header not in [h.lower() for h in request_data['headers'].keys()], \
                    f"Request should not contain authentication header '{auth_header}' for {channel_type}. " \
                    f"Got headers: {request_data['headers']}"
    
    @given(
        recipient=valid_emails(),
        message=valid_messages(),
        subject=valid_subjects()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_email_channel_specific_format(self, page: Page, notification_page, recipient, message, subject):
        """Property test: EMAIL channel correctly includes email-specific fields.
        
        **Validates: Requirements 3.2**
        
        For any valid EMAIL notification data:
        1. Generate valid email address, message, and subject
        2. Submit EMAIL notification through the UI
        3. Verify the request contains:
           - type: 'EMAIL'
           - recipient: valid email address
           - message: notification message
           - subject: email subject (if provided)
        4. Verify recipient format is a valid email address
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            recipient: Valid email address from Hypothesis
            message: Valid message content from Hypothesis
            subject: Valid email subject from Hypothesis
        """
        intercepted_requests = []
        
        def handle_route(route):
            if '/api/v1/notifications' in route.request.url:
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'body': route.request.post_data_json
                })
            route.abort()
        
        notification_page.navigate()
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with EMAIL data
        notification_page.fill_form('EMAIL', recipient, message, subject)
        
        # Submit the form
        notification_page.submit()
        
        # Verify request
        assert len(intercepted_requests) > 0, "Expected POST request for EMAIL notification"
        
        request_body = intercepted_requests[0]['body']
        
        # Verify EMAIL-specific format
        assert request_body['type'] == 'EMAIL', \
            f"Type should be EMAIL, got: {request_body['type']}"
        
        assert request_body['recipient'] == recipient, \
            f"Recipient should match email address, got: {request_body['recipient']}"
        
        assert '@' in request_body['recipient'], \
            f"EMAIL recipient should contain @, got: {request_body['recipient']}"
        
        assert request_body['message'] == message, \
            f"Message should match, got: {request_body['message']}"
        
        # Subject should be included for EMAIL
        if subject and subject.strip():
            assert 'subject' in request_body, \
                f"EMAIL request should include subject when provided, got: {request_body}"
            assert request_body['subject'] == subject, \
                f"Subject should match, got: {request_body['subject']}"
    
    @given(
        recipient=valid_sms_numbers(),
        message=valid_messages()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_sms_channel_specific_format(self, page: Page, notification_page, recipient, message):
        """Property test: SMS channel correctly formats phone number and excludes subject.
        
        **Validates: Requirements 3.2**
        
        For any valid SMS notification data:
        1. Generate valid Spanish phone number (+34) and message
        2. Submit SMS notification through the UI
        3. Verify the request contains:
           - type: 'SMS'
           - recipient: valid ES phone number (+34)
           - message: notification message
           - NO subject field
        4. Verify recipient format starts with +34 (Spain region code)
        5. Verify subject field is not included in request
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            recipient: Valid ES phone number from Hypothesis
            message: Valid message content from Hypothesis
        """
        intercepted_requests = []
        
        def handle_route(route):
            if '/api/v1/notifications' in route.request.url:
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'body': route.request.post_data_json
                })
            route.abort()
        
        notification_page.navigate()
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with SMS data (no subject)
        notification_page.fill_form('SMS', recipient, message)
        
        # Submit the form
        notification_page.submit()
        
        # Verify request
        assert len(intercepted_requests) > 0, "Expected POST request for SMS notification"
        
        request_body = intercepted_requests[0]['body']
        
        # Verify SMS-specific format
        assert request_body['type'] == 'SMS', \
            f"Type should be SMS, got: {request_body['type']}"
        
        assert request_body['recipient'] == recipient, \
            f"Recipient should match phone number, got: {request_body['recipient']}"
        
        # SMS recipient must be in +34 format (Spain)
        assert recipient.startswith('+34'), \
            f"SMS recipient should start with +34 for Spain region, got: {recipient}"
        
        assert len(recipient) == 12, \
            f"SMS recipient should be +34 + 9 digits, got: {recipient} (length: {len(recipient)})"
        
        assert request_body['message'] == message, \
            f"Message should match, got: {request_body['message']}"
        
        # SMS should NOT include subject field
        assert 'subject' not in request_body, \
            f"SMS request should NOT include subject field, got: {request_body}"
    
    @given(
        recipient=valid_whatsapp_numbers(),
        message=valid_messages()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_whatsapp_channel_specific_format(self, page: Page, notification_page, recipient, message):
        """Property test: WHATSAPP channel correctly uses E.164 format and excludes subject.
        
        **Validates: Requirements 3.2**
        
        For any valid WHATSAPP notification data:
        1. Generate valid E.164 phone number and message
        2. Submit WHATSAPP notification through the UI
        3. Verify the request contains:
           - type: 'WHATSAPP'
           - recipient: valid E.164 phone number (+ prefix)
           - message: notification message
           - NO subject field
        4. Verify recipient format is E.164 (+ followed by 7-15 digits)
        5. Verify subject field is not included in request
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            recipient: Valid E.164 phone number from Hypothesis
            message: Valid message content from Hypothesis
        """
        intercepted_requests = []
        
        def handle_route(route):
            if '/api/v1/notifications' in route.request.url:
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'body': route.request.post_data_json
                })
            route.abort()
        
        notification_page.navigate()
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill form with WHATSAPP data (no subject)
        notification_page.fill_form('WHATSAPP', recipient, message)
        
        # Submit the form
        notification_page.submit()
        
        # Verify request
        assert len(intercepted_requests) > 0, "Expected POST request for WHATSAPP notification"
        
        request_body = intercepted_requests[0]['body']
        
        # Verify WHATSAPP-specific format
        assert request_body['type'] == 'WHATSAPP', \
            f"Type should be WHATSAPP, got: {request_body['type']}"
        
        assert request_body['recipient'] == recipient, \
            f"Recipient should match phone number, got: {request_body['recipient']}"
        
        # WHATSAPP recipient must be in E.164 format (+ followed by digits)
        assert recipient.startswith('+'), \
            f"WHATSAPP recipient should start with + (E.164 format), got: {recipient}"
        
        # Should have 8-16 characters total (+ plus 7-15 digits)
        assert len(recipient) >= 8 and len(recipient) <= 16, \
            f"WHATSAPP recipient should be 8-16 characters (E.164 format), got: {recipient} (length: {len(recipient)})"
        
        # All characters after + should be digits
        digits_part = recipient[1:]
        assert digits_part.isdigit(), \
            f"WHATSAPP recipient digits should be numeric, got: {recipient}"
        
        assert request_body['message'] == message, \
            f"Message should match, got: {request_body['message']}"
        
        # WHATSAPP should NOT include subject field
        assert 'subject' not in request_body, \
            f"WHATSAPP request should NOT include subject field, got: {request_body}"

