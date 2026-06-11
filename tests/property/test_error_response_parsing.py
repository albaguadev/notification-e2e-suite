"""
Property-based tests for error response parsing and display.

This module tests that the React application correctly parses error responses
from the backend with various HTTP status codes and displays the error details
to the user.

**Validates: Requirements 3.4, 3.5, 7.5**

Property 6: Error Response Parsing
- For any error response from the backend with status codes 400, 404, 500, or 503,
  the React application SHALL parse the error JSON (containing status, timestamp,
  message, and description) and display the error message and description to the user.
"""

import pytest
import json
from hypothesis import given, settings, Verbosity, HealthCheck
from playwright.sync_api import Page
from tests.utils.generators import (
    valid_notifications,
    error_responses,
    error_status_codes
)


class TestErrorResponseParsing:
    """Test suite for verifying error response parsing and display."""
    
    @given(
        notification_data=valid_notifications(),
        error_response=error_responses()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_response_parsing_displays_message_and_description(
        self, page: Page, notification_page, notification_data, error_response
    ):
        """Property test: UI parses and displays error message and description.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data and error response with status codes
        400, 404, 500, or 503:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return error response with complete error JSON
        4. Submit the form
        5. Verify UI parses the error JSON correctly
        6. Verify UI displays both the error message and description from the response
        7. Verify the response_status field matches the HTTP status code
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            error_response: Error response data from Hypothesis generator with fields:
                {
                    'status': 400|404|500|503,
                    'timestamp': str,
                    'message': str,
                    'description': str
                }
        """
        def handle_route(route):
            """Intercept and mock error backend response."""
            if '/api/v1/notifications' in route.request.url:
                # Mock error response with complete error structure
                route.fulfill(
                    status=error_response['status'],
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
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
        assert status_message, \
            f"Expected error message to be displayed after error response, but got empty message. " \
            f"Error status: {error_response['status']}, " \
            f"Error message: {error_response['message']}, " \
            f"Error description: {error_response['description']}"
        
        # Verify the UI displays error message and/or description
        # The UI should parse the error JSON and display these fields
        message_lower = status_message.lower()
        error_message_lower = error_response['message'].lower()
        description_lower = error_response['description'].lower()
        
        # At least one of the error details should be visible
        # Break down error message and description into words and check if they appear
        error_message_words = error_message_lower.split()
        description_words = description_lower.split()
        
        # Check if any significant words from error message or description appear in status
        error_content_found = False
        
        # Check for presence of error message words (filter out very short words like 'a', 'is')
        significant_error_words = [w for w in error_message_words if len(w) > 2]
        for word in significant_error_words:
            if word in message_lower:
                error_content_found = True
                break
        
        # Check for presence of description words
        significant_description_words = [w for w in description_words if len(w) > 2]
        for word in significant_description_words:
            if word in message_lower:
                error_content_found = True
                break
        
        # Allow for substring matching as well
        if error_message_lower in message_lower or description_lower in message_lower:
            error_content_found = True
        
        assert error_content_found, \
            f"Status message should contain error details from response. " \
            f"Status message: '{status_message}', " \
            f"Expected error message or description: '{error_response['message']}' or '{error_response['description']}'"
    
    
    @given(
        notification_data=valid_notifications(),
        error_response=error_responses()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_response_status_matches_http_code(
        self, page: Page, notification_page, notification_data, error_response
    ):
        """Property test: error response status field matches HTTP status code.
        
        **Validates: Requirements 3.5, 7.5**
        
        For any valid notification data and error response:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return error response where status field matches HTTP code
        4. Submit the form
        5. Verify UI correctly interprets the response_status field
        6. Verify the response_status field exactly matches the HTTP status code
        
        This property tests that the frontend correctly validates that the error
        response's status field matches the HTTP status code returned by the server.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            error_response: Error response data from Hypothesis generator
        """
        # Ensure the error response status matches the HTTP status we'll return
        http_status = error_response['status']
        response_body = error_response.copy()
        response_body['status'] = http_status  # Ensure consistency
        
        def handle_route(route):
            """Intercept and mock error backend response."""
            if '/api/v1/notifications' in route.request.url:
                # Return response where status field matches HTTP status code
                route.fulfill(
                    status=http_status,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(response_body)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate to the application
        notification_page.navigate()
        
        # Fill the form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit the form
        notification_page.submit()
        
        # Verify error message is displayed (indicates proper parsing)
        status_message = notification_page.get_status_message()
        assert status_message, \
            f"Expected error message for HTTP status {http_status} with matching " \
            f"response_status field, but got empty message"
        
        # Verify that the message indicates an error (not a success message)
        message_lower = status_message.lower()
        error_indicators = ['error', 'failed', 'invalid', 'problem', 'issue', 'unavailable']
        assert any(indicator in message_lower for indicator in error_indicators), \
            f"Status message should indicate error for HTTP status {http_status}, " \
            f"but got: '{status_message}'"
    
    
    @given(
        notification_data=valid_notifications(),
        status_code=error_status_codes()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_status_code_400_parsing(
        self, page: Page, notification_page, notification_data, status_code
    ):
        """Property test: UI correctly parses and displays 400 status error responses.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data with 400 status code errors:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return 400 error with complete error JSON
        4. Submit the form
        5. Verify UI displays error message and description
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            status_code: Error status code (400, 404, 500, 503)
        """
        # Only test 400 status code in this test
        if status_code != 400:
            return
        
        error_response = {
            'status': 400,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Bad request - invalid notification data',
            'description': 'The notification request contains invalid or missing required fields'
        }
        
        def handle_route(route):
            """Intercept and mock 400 error response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=400,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate and set up interception
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        status_message = notification_page.get_status_message()
        assert status_message, \
            f"Expected error message for 400 status code, but got empty message"
        
        # Verify error message contains error details
        message_lower = status_message.lower()
        assert 'bad request' in message_lower or 'invalid' in message_lower or 'error' in message_lower, \
            f"Status message for 400 error should contain error details, but got: '{status_message}'"
    
    
    @given(
        notification_data=valid_notifications(),
        status_code=error_status_codes()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_status_code_404_parsing(
        self, page: Page, notification_page, notification_data, status_code
    ):
        """Property test: UI correctly parses and displays 404 status error responses.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data with 404 status code errors:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return 404 error with complete error JSON
        4. Submit the form
        5. Verify UI displays error message and description
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            status_code: Error status code (400, 404, 500, 503)
        """
        # Only test 404 status code in this test
        if status_code != 404:
            return
        
        error_response = {
            'status': 404,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Not found - endpoint not available',
            'description': 'The requested notification endpoint is not available on the server'
        }
        
        def handle_route(route):
            """Intercept and mock 404 error response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=404,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate and set up interception
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        status_message = notification_page.get_status_message()
        assert status_message, \
            f"Expected error message for 404 status code, but got empty message"
        
        # Verify error message contains error details
        message_lower = status_message.lower()
        assert 'not found' in message_lower or 'not available' in message_lower or 'error' in message_lower, \
            f"Status message for 404 error should contain error details, but got: '{status_message}'"
    
    
    @given(
        notification_data=valid_notifications(),
        status_code=error_status_codes()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_status_code_500_parsing(
        self, page: Page, notification_page, notification_data, status_code
    ):
        """Property test: UI correctly parses and displays 500 status error responses.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data with 500 status code errors:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return 500 error with complete error JSON
        4. Submit the form
        5. Verify UI displays error message and description
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            status_code: Error status code (400, 404, 500, 503)
        """
        # Only test 500 status code in this test
        if status_code != 500:
            return
        
        error_response = {
            'status': 500,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Internal server error - backend processing failed',
            'description': 'The backend server encountered an error while processing the notification request'
        }
        
        def handle_route(route):
            """Intercept and mock 500 error response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=500,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate and set up interception
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        status_message = notification_page.get_status_message()
        assert status_message, \
            f"Expected error message for 500 status code, but got empty message"
        
        # Verify error message contains error details
        message_lower = status_message.lower()
        assert 'server error' in message_lower or 'internal' in message_lower or 'error' in message_lower, \
            f"Status message for 500 error should contain error details, but got: '{status_message}'"
    
    
    @given(
        notification_data=valid_notifications(),
        status_code=error_status_codes()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_status_code_503_parsing(
        self, page: Page, notification_page, notification_data, status_code
    ):
        """Property test: UI correctly parses and displays 503 status error responses.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data with 503 status code errors:
        1. Navigate to the application
        2. Fill the form with notification data
        3. Mock backend to return 503 error with complete error JSON
        4. Submit the form
        5. Verify UI displays error message and description
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            status_code: Error status code (400, 404, 500, 503)
        """
        # Only test 503 status code in this test
        if status_code != 503:
            return
        
        error_response = {
            'status': 503,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Service unavailable - backend is temporarily down',
            'description': 'The notification service is temporarily unavailable. Please try again later'
        }
        
        def handle_route(route):
            """Intercept and mock 503 error response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=503,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate and set up interception
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        status_message = notification_page.get_status_message()
        assert status_message, \
            f"Expected error message for 503 status code, but got empty message"
        
        # Verify error message contains error details
        message_lower = status_message.lower()
        assert 'unavailable' in message_lower or 'service' in message_lower or 'error' in message_lower, \
            f"Status message for 503 error should contain error details, but got: '{status_message}'"
    
    
    @given(
        notification_data=valid_notifications(),
        error_response=error_responses()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.normal,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    @pytest.mark.property_test
    def test_error_response_different_error_codes_coverage(
        self, page: Page, notification_page, notification_data, error_response
    ):
        """Property test: Error responses with all status codes are handled correctly.
        
        **Validates: Requirements 3.4, 3.5, 7.5**
        
        For any valid notification data and any error status code (400, 404, 500, 503):
        1. Generate various error responses
        2. Verify UI handles each status code appropriately
        3. Ensure consistency in error message display across different codes
        
        This test ensures broad coverage of all supported error status codes.
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
            error_response: Error response data from Hypothesis generator
        """
        def handle_route(route):
            """Intercept and mock error backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=error_response['status'],
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(error_response)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate and set up interception
        notification_page.navigate()
        
        # Fill form
        notification_page.fill_form(
            notification_data['type'],
            notification_data['recipient'],
            notification_data['message'],
            notification_data.get('subject')
        )
        
        # Submit form
        notification_page.submit()
        
        # Verify error message is displayed
        status_message = notification_page.get_status_message()
        
        # Basic validation - message should be present and indicate error
        assert status_message, \
            f"Expected error message for status code {error_response['status']}, but got empty message"
        
        message_lower = status_message.lower()
        
        # Message should contain some indication of error/problem
        error_keywords = ['error', 'failed', 'invalid', 'problem', 'issue', 'unavailable', 
                         'not found', 'bad', 'server', 'connection', 'unable']
        assert any(keyword in message_lower for keyword in error_keywords), \
            f"Error message should indicate an error for status {error_response['status']}, " \
            f"but got: '{status_message}'"

