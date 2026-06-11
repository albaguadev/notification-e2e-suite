"""
Unit tests for malformed error response handling.

This module tests that the NotificationForm component handles malformed error responses
gracefully, failing silently without showing errors to the user or crashing the application.

Tests validate Requirement 3.6 by verifying:
- Malformed JSON responses are handled silently
- Responses with missing required error fields fail silently
- UI does not display error messages for malformed responses
- Application continues to function normally
- No technical details or error messages are exposed
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestMalformedErrorResponse:
    """Test suite for malformed error response handling."""
    
    def test_malformed_json_response_fails_silently(self, page: Page, notification_page):
        """Test that malformed JSON responses fail silently with no error message.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Malformed JSON response is handled gracefully
        - UI fails silently (no error message shown)
        - Application doesn't crash
        - No technical error is exposed to user
        """
        # Mock malformed JSON response
        def handle_malformed_json(route):
            route.fulfill(
                status=500,
                headers={'Content-Type': 'text/plain'},
                body='Internal Server Error: Malformed Request'  # Not JSON
            )
        
        page.route('**/api/v1/notifications', handle_malformed_json)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message',
            'Test subject'
        )
        notification_page.submit()
        
        # Wait for any potential response
        page.wait_for_timeout(1000)
        
        # Get status message - should be empty (silent failure)
        status_element = page.locator('[data-testid="status-message"]')
        
        # For silent failure, the status should be idle or no message should be visible
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            # If visible, should be empty for silent failure
            assert error_message.strip() == '', \
                f"Malformed JSON should fail silently, got: {error_message}"
        else:
            # Not visible is also acceptable for silent failure
            pass
    
    def test_missing_status_field_fails_silently(self, page: Page, notification_page):
        """Test that error response missing status field fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Response missing status field is treated as malformed
        - No error message is shown to user
        - Application continues normally
        """
        # Mock error response missing status field
        def handle_missing_status(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"timestamp": "2024-01-01T00:00:00Z", "message": "Bad Request", "description": "Invalid input"}'
            )
        
        page.route('**/api/v1/notifications', handle_missing_status)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently - no error message shown
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Missing status field should fail silently, got: {error_message}"
    
    def test_missing_message_field_fails_silently(self, page: Page, notification_page):
        """Test that error response missing message field fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Response missing message field is treated as malformed
        - No error message is shown to user
        """
        # Mock error response missing message field
        def handle_missing_message(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"status": 400, "timestamp": "2024-01-01T00:00:00Z", "description": "Invalid input"}'
            )
        
        page.route('**/api/v1/notifications', handle_missing_message)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Missing message field should fail silently, got: {error_message}"
    
    def test_missing_description_field_fails_silently(self, page: Page, notification_page):
        """Test that error response missing description field fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Response missing description field is treated as malformed
        - No error message is shown to user
        """
        # Mock error response missing description field
        def handle_missing_description(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"status": 400, "timestamp": "2024-01-01T00:00:00Z", "message": "Bad Request"}'
            )
        
        page.route('**/api/v1/notifications', handle_missing_description)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Missing description field should fail silently, got: {error_message}"
    
    def test_missing_timestamp_field_fails_silently(self, page: Page, notification_page):
        """Test that error response missing timestamp field fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Response missing timestamp field is treated as malformed
        - No error message is shown to user
        """
        # Mock error response missing timestamp field
        def handle_missing_timestamp(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"status": 400, "message": "Bad Request", "description": "Invalid input"}'
            )
        
        page.route('**/api/v1/notifications', handle_missing_timestamp)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Missing timestamp field should fail silently, got: {error_message}"
    
    def test_invalid_json_syntax_fails_silently(self, page: Page, notification_page):
        """Test that response with invalid JSON syntax fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Response with invalid JSON syntax is handled gracefully
        - No error message is shown
        - Application doesn't crash
        """
        # Mock invalid JSON syntax
        def handle_invalid_json(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"status": 400, "message": "Bad Request", "description": "Invalid input"'  # Missing closing brace
            )
        
        page.route('**/api/v1/notifications', handle_invalid_json)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Invalid JSON syntax should fail silently, got: {error_message}"
    
    def test_status_mismatch_fails_silently(self, page: Page, notification_page):
        """Test that error response with mismatched status field fails silently.
        
        Validates: Requirement 3.6 (related to 3.5 validation)
        
        Verifies that:
        - Response status field that doesn't match HTTP status code is rejected
        - No error message is shown (silent failure)
        - Application continues normally
        """
        # Mock error response with mismatched status
        def handle_status_mismatch(route):
            route.fulfill(
                status=400,  # HTTP status
                headers={'Content-Type': 'application/json'},
                body='{"status": 500, "timestamp": "2024-01-01T00:00:00Z", "message": "Error", "description": "Mismatch"}'
                # Response says 500 but HTTP status is 400
            )
        
        page.route('**/api/v1/notifications', handle_status_mismatch)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently due to status mismatch
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Status mismatch should fail silently, got: {error_message}"
    
    def test_null_response_fails_silently(self, page: Page, notification_page):
        """Test that null response fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Null response is handled gracefully
        - No error message is shown
        """
        # Mock null response
        def handle_null(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='null'
            )
        
        page.route('**/api/v1/notifications', handle_null)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Null response should fail silently, got: {error_message}"
    
    def test_empty_object_response_fails_silently(self, page: Page, notification_page):
        """Test that empty object response fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Empty JSON object is handled gracefully
        - No error message is shown
        """
        # Mock empty object response
        def handle_empty_object(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{}'
            )
        
        page.route('**/api/v1/notifications', handle_empty_object)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Empty object should fail silently, got: {error_message}"
    
    def test_partial_error_response_fails_silently(self, page: Page, notification_page):
        """Test that partially complete error response fails silently.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Partially complete response (only some fields) is rejected
        - No error message is shown
        """
        # Mock partially complete response
        def handle_partial(route):
            route.fulfill(
                status=400,
                headers={'Content-Type': 'application/json'},
                body='{"status": 400, "timestamp": "2024-01-01T00:00:00Z"}'
                # Missing message and description
            )
        
        page.route('**/api/v1/notifications', handle_partial)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Should fail silently
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
            assert error_message.strip() == '', \
                f"Partial response should fail silently, got: {error_message}"
    
    def test_application_remains_functional_after_malformed_response(self, page: Page, notification_page):
        """Test that application remains functional after malformed response.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - Application doesn't crash after malformed response
        - UI remains interactive
        - User can attempt another action
        """
        # First request gets malformed response
        call_count = {'count': 0}
        
        def handle_route(route):
            call_count['count'] += 1
            if call_count['count'] == 1:
                # First request: malformed response
                route.fulfill(
                    status=500,
                    headers={'Content-Type': 'text/plain'},
                    body='Internal Server Error'
                )
            else:
                # Second request: same malformed response
                route.fulfill(
                    status=500,
                    headers={'Content-Type': 'text/plain'},
                    body='Internal Server Error'
                )
        
        page.route('**/api/v1/notifications', handle_route)
        
        notification_page.navigate()
        
        # First submission with malformed response
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        page.wait_for_timeout(1000)
        
        # Verify application is still responsive
        recipient_input = page.locator('[data-testid="recipient"]')
        assert not recipient_input.is_disabled(), "Form should remain interactive"
        
        # Try another submission - should work the same way
        recipient_input.fill('another@example.com')
        notification_page.submit()
        page.wait_for_timeout(1000)
        
        # Application should still be functional
        assert not page.is_closed(), "Page should remain open"
        assert recipient_input.is_enabled(), "Form should remain enabled"
    
    def test_malformed_response_does_not_show_technical_details(self, page: Page, notification_page):
        """Test that malformed responses don't expose technical details.
        
        Validates: Requirement 3.6
        
        Verifies that:
        - No JSON parsing errors are shown
        - No technical error messages appear
        - No raw response body is displayed
        """
        # Mock malformed response
        def handle_malformed(route):
            route.fulfill(
                status=500,
                headers={'Content-Type': 'application/json'},
                body='{"error": "Server error", "stack": "at error handler"}'  # Malformed error format
            )
        
        page.route('**/api/v1/notifications', handle_malformed)
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test message'
        )
        notification_page.submit()
        
        # Wait for response
        page.wait_for_timeout(1000)
        
        # Get any visible message
        status_element = page.locator('[data-testid="status-message"]')
        if status_element.is_visible():
            error_message = status_element.text_content() or ''
        else:
            error_message = ''
        
        # Verify no technical details are exposed
        assert 'stack' not in error_message.lower(), \
            f"Stack trace should not be exposed in: {error_message}"
        assert 'JSON' not in error_message, \
            f"JSON error should not be exposed in: {error_message}"
        assert 'parse' not in error_message.lower(), \
            f"Parse error should not be exposed in: {error_message}"
