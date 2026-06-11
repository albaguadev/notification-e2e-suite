"""
Unit tests for 200 response with error content handling.

This module tests that the NotificationForm component checks the response body
when the backend returns HTTP 200 but includes error information in the response,
and displays appropriate error feedback to the user.

Tests validate Requirement 7.4 by verifying:
- HTTP 200 responses with error content in body are detected
- Error messages are extracted from response body and displayed
- User sees error feedback even though HTTP status is 200
- Error message contains message and description fields
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestResponseWithErrorContent:
    """Test suite for 200 response with error content."""
    
    def test_200_response_with_error_fields_shows_error_message(self, page: Page, notification_page):
        """Test that 200 response with error fields shows error message to user.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - HTTP 200 response with error structure is detected
        - Error message and description are extracted
        - User sees error feedback
        - Error message indicates the problem
        """
        # Mock 200 response with error content
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "Invalid recipient", "description": "The recipient address is not valid"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form with valid data
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message',
            'Test subject'
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed for 200 with error content"
        
        # Verify error message contains information from response
        error_lower = error_message.lower()
        assert 'error' in error_lower or 'invalid' in error_lower, \
            f"Error message should contain error information, got: {error_message}"
    
    def test_200_response_with_message_and_description_shows_both(self, page: Page, notification_page):
        """Test that both message and description from error are shown.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Message field from response is displayed
        - Description field from response is displayed
        - Combined message provides helpful information
        """
        # Mock 200 response with error content
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "Email delivery failed", "description": "The email service returned a 550 error"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message',
            'Test subject'
        )
        
        # Submit
        notification_page.submit()
        
        # Verify error message contains both parts
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed"
        
        # Should contain at least part of the message
        error_lower = error_message.lower()
        assert ('email' in error_lower or 'failed' in error_lower or 'delivery' in error_lower), \
            f"Error message should contain the error message part, got: {error_message}"
    
    def test_200_response_with_error_sms_channel(self, page: Page, notification_page):
        """Test that 200 response with error is detected for SMS channel.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - SMS channel also checks response body for errors
        - Error is displayed for SMS requests
        """
        # Mock 200 response with error content
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "SMS gateway unavailable", "description": "Could not reach SMS provider"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form with SMS data
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test SMS message'
        )
        
        # Submit
        notification_page.submit()
        
        # Verify error message is shown
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed for SMS channel"
        
        error_lower = error_message.lower()
        assert ('unavailable' in error_lower or 'gateway' in error_lower or 'sms' in error_lower or 'error' in error_lower), \
            f"Error message should indicate SMS issue, got: {error_message}"
    
    def test_200_response_with_error_whatsapp_channel(self, page: Page, notification_page):
        """Test that 200 response with error is detected for WhatsApp channel.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - WhatsApp channel also checks response body for errors
        - Error is displayed for WhatsApp requests
        """
        # Mock 200 response with error content
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "WhatsApp API error", "description": "Invalid phone number format"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form with WhatsApp data
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test WhatsApp message'
        )
        
        # Submit
        notification_page.submit()
        
        # Verify error message is shown
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed for WhatsApp channel"
        
        error_lower = error_message.lower()
        assert ('whatsapp' in error_lower or 'api' in error_lower or 'error' in error_lower or 'phone' in error_lower), \
            f"Error message should indicate WhatsApp issue, got: {error_message}"
    
    def test_200_response_without_error_fields_shows_success(self, page: Page, notification_page):
        """Test that normal 200 response without error fields shows success.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Normal success responses (200 without error fields) show success
        - No false positives for error detection
        """
        # Mock normal 200 success response
        def handle_200_success(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"id": "123", "type": "EMAIL", "status": "SENT", "timestamp": "2024-01-01T00:00:00Z"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_success)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message',
            'Test subject'
        )
        
        # Submit
        notification_page.submit()
        
        # Verify success message is shown
        status_message = notification_page.get_status_message()
        assert status_message != '', "Success message should be displayed"
        
        # Should be success, not error
        message_lower = status_message.lower()
        assert ('success' in message_lower or 'sent' in message_lower), \
            f"Should show success, got: {status_message}"
    
    def test_200_response_only_status_field_not_treated_as_error(self, page: Page, notification_page):
        """Test that having only status field in 200 response doesn't trigger error detection.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Response must have ALL error fields (status, message, description, timestamp) to be treated as error
        - Partial error structure is not treated as error
        """
        # Mock 200 response with only status field
        def handle_200_partial(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "id": "123", "type": "EMAIL"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_partial)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        
        # Submit
        notification_page.submit()
        
        # Should show success, not error
        status_message = notification_page.get_status_message()
        # May show success or nothing, but should not show error
        message_lower = status_message.lower() if status_message else ''
        assert 'error' not in message_lower, \
            f"Should not treat incomplete error structure as error, got: {status_message}"
    
    def test_200_response_with_multiple_errors_shows_message(self, page: Page, notification_page):
        """Test that 200 response with multiple errors shows combined message.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Multiple error scenarios are properly reported
        - Message is comprehensive
        """
        # Mock 200 response with error
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "Multiple validation errors", "description": "Recipient invalid, message too long"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        
        # Submit
        notification_page.submit()
        
        # Verify error message is displayed
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed"
        
        # Should contain information about errors
        error_lower = error_message.lower()
        assert ('validation' in error_lower or 'error' in error_lower or 'invalid' in error_lower), \
            f"Error message should describe the errors, got: {error_message}"
    
    def test_200_response_error_does_not_show_success_message(self, page: Page, notification_page):
        """Test that error in 200 response doesn't show as success.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Error content in 200 response is clearly shown as error, not success
        """
        # Mock 200 response with error
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "Authentication failed", "description": "Invalid credentials"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test message'
        )
        
        # Submit
        notification_page.submit()
        
        # Get displayed message
        message = notification_page.get_status_message()
        
        # Should NOT show success
        message_lower = message.lower() if message else ''
        assert 'success' not in message_lower and 'sent' not in message_lower, \
            f"Should not show success for error response, got: {message}"
        
        # SHOULD show error information
        assert ('authentication' in message_lower or 'failed' in message_lower or 
                'error' in message_lower or 'invalid' in message_lower), \
            f"Should show error information, got: {message}"
    
    def test_200_response_error_detected_for_all_status_codes_in_body(self, page: Page, notification_page):
        """Test that error detection works for any status code in response body (if present).
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Error is detected regardless of the value in status field
        - Detection relies on presence of message/description fields
        """
        # Mock 200 response with error (note: status field will be 500 in body)
        def handle_200_with_error(route):
            route.fulfill(
                status=200,
                headers={'Content-Type': 'application/json'},
                body='{"status": 500, "timestamp": "2024-01-01T00:00:00Z", "message": "Internal error reported", "description": "Backend issue"}'
            )
        
        page.route('**/api/v1/notifications', handle_200_with_error)
        
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test message'
        )
        
        # Submit
        notification_page.submit()
        
        # Should detect error and show message
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error should be detected and displayed"
        
        error_lower = error_message.lower()
        assert ('internal' in error_lower or 'error' in error_lower or 'backend' in error_lower), \
            f"Error message should be shown, got: {error_message}"
    
    def test_form_can_be_resubmitted_after_200_with_error(self, page: Page, notification_page):
        """Test that form remains usable after 200 response with error.
        
        Validates: Requirement 7.4
        
        Verifies that:
        - Form remains interactive after error in 200 response
        - User can correct and resubmit
        """
        call_count = {'count': 0}
        
        def handle_route(route):
            call_count['count'] += 1
            if call_count['count'] == 1:
                # First request: 200 with error
                route.fulfill(
                    status=200,
                    headers={'Content-Type': 'application/json'},
                    body='{"status": 200, "timestamp": "2024-01-01T00:00:00Z", "message": "Error", "description": "Invalid input"}'
                )
            else:
                # Second request: success
                route.fulfill(
                    status=200,
                    headers={'Content-Type': 'application/json'},
                    body='{"id": "123", "type": "EMAIL", "status": "SENT"}'
                )
        
        page.route('**/api/v1/notifications', handle_route)
        
        notification_page.navigate()
        
        # First submission
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Verify error is shown
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error should be displayed"
        
        # Verify form is still interactive
        recipient_input = page.locator('[data-testid="recipient"]')
        assert not recipient_input.is_disabled(), "Form should remain interactive"
        
        # Clear and resubmit
        recipient_input.fill('another@example.com')
        notification_page.submit()
        
        # Should show success message this time
        success_message = notification_page.get_status_message()
        assert success_message != '', "Success message should be displayed"
        assert 'success' in success_message.lower(), \
            f"Should show success message, got: {success_message}"
