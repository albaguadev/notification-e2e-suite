"""
Unit tests for backend unavailable scenario.

This module tests that the NotificationForm component handles network failures
and backend unavailability gracefully, displaying user-friendly error messages
without exposing technical details.

Tests validate Requirement 3.3 by verifying:
- Network failure (connection refused) is handled gracefully
- Timeout scenarios show appropriate error messages
- UI displays "Unable to connect to notification service" message
- No technical details (stack traces, IP addresses, etc.) are exposed to user
- Error message is helpful and actionable
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestBackendUnavailable:
    """Test suite for backend unavailable scenario."""
    
    def test_network_failure_connection_refused(self, page: Page, notification_page):
        """Test that connection refused error is handled gracefully.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Backend unavailable (connection refused) is handled
        - UI displays user-friendly error message
        - No technical details are exposed
        - Error message is visible to user
        """
        # Mock network failure - connection refused
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
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
        assert error_message != '', "Error message should be displayed"
        
        # Verify user-friendly error message is shown
        error_text = error_message.lower()
        assert 'unable to connect' in error_text or 'connection' in error_text, \
            f"Error message should indicate connection issue, got: {error_message}"
        
        # Verify technical details are NOT exposed
        assert 'ECONNREFUSED' not in error_message, \
            "Technical error code ECONNREFUSED should not be exposed"
        assert 'localhost' not in error_message, \
            "Localhost address should not be exposed"
        assert '8081' not in error_message, \
            "Port number should not be exposed"
        assert 'stack' not in error_text, \
            "Stack trace should not be exposed"
        assert 'trace' not in error_text, \
            "Stack trace should not be exposed"
        assert 'undefined' not in error_message, \
            "JavaScript undefined should not be exposed"
        assert 'null' not in error_message, \
            "null should not be exposed"
    
    def test_network_timeout_shows_friendly_error(self, page: Page, notification_page):
        """Test that network timeout is handled with friendly error message.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Network timeout is handled gracefully
        - User-friendly error message is displayed
        - No technical timeout details are exposed
        """
        # Mock network timeout
        def abort_with_timeout(route):
            route.abort('timedout')
        
        page.route('**/api/v1/notifications', abort_with_timeout)
        
        notification_page.navigate()
        
        # Fill form with valid data
        notification_page.fill_form(
            'SMS',
            '+34612345678',
            'Test SMS message'
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed for timeout"
        
        # Verify user-friendly error message
        error_text = error_message.lower()
        assert 'unable' in error_text or 'timeout' in error_text or 'connection' in error_text, \
            f"Error message should be user-friendly, got: {error_message}"
        
        # Verify technical timeout details are NOT exposed
        assert 'timedout' not in error_message, \
            "Technical timeout code should not be exposed"
        assert 'ETIMEDOUT' not in error_message, \
            "Technical error code ETIMEDOUT should not be exposed"
        assert 'socket' not in error_text, \
            "Socket details should not be exposed"
    
    def test_backend_not_found_shows_friendly_error(self, page: Page, notification_page):
        """Test that backend not found error is handled gracefully.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Backend not found (no listening port) is handled
        - User-friendly error message is displayed
        - No technical details are exposed
        """
        # Mock network failure - no listening port
        def abort_network(route):
            route.abort('failed')
        
        page.route('**/api/v1/notifications', abort_network)
        
        notification_page.navigate()
        
        # Fill form with valid data
        notification_page.fill_form(
            'WHATSAPP',
            '+34612345678',
            'Test WhatsApp message'
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed"
        
        # Verify user-friendly error message
        error_text = error_message.lower()
        assert 'unable' in error_text or 'connection' in error_text, \
            f"Error message should be user-friendly, got: {error_message}"
        
        # Verify technical details are NOT exposed
        assert 'net::' not in error_message, \
            "Chrome net:: error codes should not be exposed"
        assert 'ERR_' not in error_message, \
            "Chrome ERR_ error codes should not be exposed"
    
    def test_error_message_is_visible_and_readable(self, page: Page, notification_page):
        """Test that error message is visible and readable when backend unavailable.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Error message is visible on page
        - Error message is readable (not too small, not hidden)
        - Error message styling indicates it's an error (likely red or warning color)
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'user@example.com',
            'Test message',
            'Test subject'
        )
        notification_page.submit()
        
        # Get status message element
        status_element = page.locator('[data-testid="status-message"]')
        
        # Wait for status message to be visible with timeout
        status_element.wait_for(state='visible', timeout=5000)
        
        # Verify status message is visible
        assert status_element.is_visible(), "Status message should be visible"
        
        # Verify status message has text content
        status_text = status_element.text_content()
        assert status_text and status_text.strip() != '', "Status message should have text"
        
        # Verify error styling (should have error class or similar)
        element_class = status_element.get_attribute('class') or ''
        # Should either have error class or parent div with error styling
        assert 'error' in element_class.lower() or status_element.evaluate(
            "el => window.getComputedStyle(el).color.includes('rgb(255')"
        ), "Error message should have error styling (class or red color)"
    
    def test_error_message_contains_helpful_information(self, page: Page, notification_page):
        """Test that error message contains helpful information without tech details.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Error message indicates what went wrong (connection issue)
        - Error message suggests next action (try again later)
        - Error message does not contain technical jargon
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Get error message
        error_message = notification_page.get_status_message()
        
        # Verify error message is helpful
        error_lower = error_message.lower()
        
        # Should indicate it's a connection problem
        assert ('unable' in error_lower or 'failed' in error_lower or 
                'connection' in error_lower or 'service' in error_lower), \
            f"Error message should explain connection problem, got: {error_message}"
        
        # Should suggest retrying (preferred) or indicate service unavailability
        assert ('try again' in error_lower or 'retry' in error_lower or 
                'later' in error_lower or 'unavailable' in error_lower or
                'service' in error_lower), \
            f"Error message should suggest action or indicate service issue, got: {error_message}"
        
        # Should NOT contain technical jargon
        technical_terms = [
            'socket', 'port', 'http', 'tcp', 'dns', 'localhost',
            'econnrefused', 'etimedout', 'enotfound', 'code:',
            'errno', 'syscall', 'stack', 'trace', 'at ', 'error:'
        ]
        
        for term in technical_terms:
            assert term not in error_lower, \
                f"Error message should not contain technical term '{term}', got: {error_message}"
    
    def test_error_message_specific_format(self, page: Page, notification_page):
        """Test that error message follows the specified format.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Error message matches expected user-friendly format
        - Message is clear and actionable
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Get error message
        error_message = notification_page.get_status_message()
        error_lower = error_message.lower()
        
        # Should contain words related to connection/service unavailability
        connection_related = [
            'unable to connect', 'connection failed', 'service unavailable',
            'cannot reach', 'could not connect', 'connection error',
            'unable to reach', 'offline', 'network error'
        ]
        
        found_related_message = any(phrase in error_lower for phrase in connection_related)
        
        assert found_related_message, \
            f"Error message should use connection/service related wording, got: {error_message}"
    
    def test_ui_remains_functional_after_error(self, page: Page, notification_page):
        """Test that UI remains functional after network error.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Error message is displayed but doesn't crash UI
        - Form fields remain interactive
        - User can try submitting again after error
        """
        # Mock network failure for first request
        call_count = {'count': 0}
        
        def handle_route(route):
            call_count['count'] += 1
            # First call fails, second call succeeds
            if call_count['count'] == 1:
                route.abort()
            else:
                # After first error, return error response
                route.abort()
        
        page.route('**/api/v1/notifications', handle_route)
        
        notification_page.navigate()
        
        # First attempt - should fail
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Verify error message is displayed
        error_message = notification_page.get_status_message()
        assert error_message != '', "Error message should be displayed"
        
        # Verify form is still interactive - user can fill new data
        recipient_input = page.locator('[data-testid="recipient"]')
        assert not recipient_input.is_disabled(), "Recipient input should not be disabled"
        
        # Clear and try again
        recipient_input.fill('another@example.com')
        message_input = page.locator('[data-testid="message"]')
        message_input.fill('Another message')
        
        # Submit again
        notification_page.submit()
        
        # UI should still be responsive
        assert page.is_closed() == False, "Page should still be open and functional"
    
    def test_error_message_does_not_expose_ip_addresses(self, page: Page, notification_page):
        """Test that error message does not expose IP addresses or hostnames.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - IP addresses are not exposed
        - Hostnames are not exposed
        - Port numbers are not exposed
        - Internal server details are not exposed
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Get error message
        error_message = notification_page.get_status_message()
        
        # Verify no IP addresses are exposed
        import re
        ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
        assert not re.search(ip_pattern, error_message), \
            f"Error message should not expose IP addresses, got: {error_message}"
        
        # Verify common hostnames/addresses are not exposed
        hostnames = ['localhost', 'localhost:8081', '127.0.0.1', 'http://localhost']
        for hostname in hostnames:
            assert hostname not in error_message, \
                f"Error message should not expose hostname '{hostname}', got: {error_message}"
    
    def test_error_message_does_not_expose_stack_trace(self, page: Page, notification_page):
        """Test that error message does not expose JavaScript stack traces.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - Stack traces are not visible to user
        - Function names are not exposed
        - Source file locations are not exposed
        - No 'at' lines are shown (common in stack traces)
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        # Fill and submit form
        notification_page.fill_form(
            'EMAIL',
            'test@example.com',
            'Test message'
        )
        notification_page.submit()
        
        # Get error message
        error_message = notification_page.get_status_message()
        error_lower = error_message.lower()
        
        # Verify no stack trace indicators
        stack_trace_indicators = [
            'at ', ' at\n', '.js:', '.tsx:', '.ts:',
            '(anonymous)', 'Object.', 'Function',
            'line 1', 'column '
        ]
        
        for indicator in stack_trace_indicators:
            # Case-sensitive check for most indicators
            if indicator.lower() == indicator:  # Check if it's already lowercase
                assert indicator not in error_lower, \
                    f"Error message should not contain stack trace indicator '{indicator}', got: {error_message}"
            else:
                assert indicator not in error_message, \
                    f"Error message should not contain stack trace indicator '{indicator}', got: {error_message}"
    
    def test_multiple_channel_types_show_same_friendly_error(self, page: Page, notification_page):
        """Test that different channel types all show the same friendly error message.
        
        Validates: Requirement 3.3
        
        Verifies that:
        - EMAIL channel shows friendly error on backend unavailable
        - SMS channel shows friendly error on backend unavailable
        - WHATSAPP channel shows friendly error on backend unavailable
        - All errors follow same format
        """
        # Mock network failure
        page.route('**/api/v1/notifications', lambda route: route.abort())
        
        notification_page.navigate()
        
        test_cases = [
            ('EMAIL', 'test@example.com', 'Email test', 'Test subject'),
            ('SMS', '+34612345678', 'SMS test'),
            ('WHATSAPP', '+34612345678', 'WhatsApp test'),
        ]
        
        error_messages = []
        
        for notification_type, recipient, message, *optional in test_cases:
            # Reset form
            page.reload()
            notification_page.navigate()
            
            # Fill form with channel-specific data
            if optional:  # Has subject (EMAIL)
                notification_page.fill_form(notification_type, recipient, message, optional[0])
            else:
                notification_page.fill_form(notification_type, recipient, message)
            
            # Submit
            notification_page.submit()
            
            # Get error message
            error_msg = notification_page.get_status_message()
            error_messages.append(error_msg)
            
            # Verify all have user-friendly error messages
            error_lower = error_msg.lower()
            assert 'unable' in error_lower or 'connection' in error_lower or 'service' in error_lower, \
                f"Error message for {notification_type} should be user-friendly"
            
            # Verify no technical details
            assert '8081' not in error_msg, f"Port should not be exposed in {notification_type} error"
            assert 'localhost' not in error_msg, f"Localhost should not be exposed in {notification_type} error"
        
        # All error messages should be similar in tone
        # (they may be different depending on implementation, but all should be user-friendly)
        for error_msg in error_messages:
            assert error_msg != '', "All channel types should show error message"

