"""
Property-based tests for malformed error response handling.

This module tests that the React application fails silently when receiving
malformed error responses (invalid JSON, missing fields) and shows no error
message to the user.

**Validates: Requirements 3.6**

Property 7: Malformed Error Handling
- For any malformed error response (invalid JSON or missing expected error fields),
  the React application SHALL fail silently and show no error message to the user.
"""

import pytest
import json
from hypothesis import given, settings, Verbosity, HealthCheck, strategies as st
from playwright.sync_api import Page
from tests.utils.generators import (
    valid_notifications,
    error_status_codes
)


@st.composite
def malformed_error_responses(draw):
    """Generate a malformed error response.
    
    Creates various types of malformed responses:
    - Invalid JSON strings
    - Missing required fields (status, timestamp, message, description)
    - Partial error responses with only some fields
    - Empty JSON objects
    - Null/undefined fields
    
    Returns:
        tuple: (response_body, content_type) where response_body is the actual
               response content and content_type is the header to use
    """
    malformed_type = draw(st.integers(min_value=0, max_value=7))
    
    if malformed_type == 0:
        # Invalid JSON string
        return ('{"invalid": json', 'application/json; charset=utf-8')
    elif malformed_type == 1:
        # Missing message field
        return (json.dumps({
            'status': 400,
            'timestamp': '2024-01-01T00:00:00Z',
            'description': 'Something went wrong'
        }), 'application/json; charset=utf-8')
    elif malformed_type == 2:
        # Missing description field
        return (json.dumps({
            'status': 400,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Error occurred'
        }), 'application/json; charset=utf-8')
    elif malformed_type == 3:
        # Missing status field
        return (json.dumps({
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Error',
            'description': 'Something went wrong'
        }), 'application/json; charset=utf-8')
    elif malformed_type == 4:
        # Empty JSON object
        return ('{}', 'application/json; charset=utf-8')
    elif malformed_type == 5:
        # Only status field
        return (json.dumps({'status': 400}), 'application/json; charset=utf-8')
    elif malformed_type == 6:
        # Null/empty string fields
        return (json.dumps({
            'status': 400,
            'timestamp': None,
            'message': '',
            'description': None
        }), 'application/json; charset=utf-8')
    else:
        # Non-JSON response (plain text)
        return ('This is not JSON', 'text/plain; charset=utf-8')


class TestMalformedErrorHandling:
    """Test suite for verifying malformed error response handling."""
    
    @given(
        notification_data=valid_notifications(),
        error_status=error_status_codes(),
        malformed_response=malformed_error_responses()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_malformed_error_responses_fail_silently(
        self, page: Page, notification_page, notification_data, error_status, malformed_response
    ):
        """Property test: Malformed error responses fail silently with no error message.
        
        **Validates: Requirements 3.6**
        
        For any valid notification data and malformed error response:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return malformed response (invalid JSON or missing fields)
        4. Submit the form
        5. Verify the UI fails silently - NO error message is displayed
        6. Verify the form remains interactive or shows no status message
        
        Malformed responses include:
        - Invalid JSON strings
        - Missing required fields (status, timestamp, message, description)
        - Partial error responses with only some fields
        - Empty JSON objects
        - Null/undefined fields
        - Non-JSON content
        
        When the UI cannot parse an error response, it should fail gracefully
        without displaying an error message to the user.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            error_status: Error status code (400, 404, 500, 503)
            malformed_response: Tuple of (response_body, content_type) from generator
        """
        response_body, content_type = malformed_response
        
        def handle_route(route):
            """Intercept and mock malformed error backend response."""
            if '/api/v1/notifications' in route.request.url:
                # Mock malformed error response
                route.fulfill(
                    status=error_status,
                    content_type=content_type,
                    body=response_body
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation to catch on-mount requests
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate to the application
        notification_page.navigate()
        
        # Fill the form with notification data
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit the form
        notification_page.submit()
        
        # Retrieve the displayed status message
        status_message = notification_page.get_status_message()
        
        # **CRITICAL REQUIREMENT 3.6**: 
        # For malformed responses, the UI SHALL fail silently and show NO error message.
        # The status_message should be empty/falsy when handling malformed responses.
        assert not status_message or status_message.strip() == '', \
            f"Malformed error response should fail silently with no error message displayed, " \
            f"but got: '{status_message}'. " \
            f"Error status: {error_status}, " \
            f"Response body: {response_body[:100]}..."
        
        # Verify no visible error indication on the page
        # The page should either show no status message or a generic fallback
        # (but NOT parse and display the malformed error details)
        
        # This test validates that the UI gracefully handles malformed responses
        # without confusing the user with parse errors or undefined behavior


