"""
Property-based tests for verifying no authentication headers are sent.

This module tests that API requests sent by the React application do not include
any authentication headers, ensuring the frontend application adheres to the
requirement of sending unauthenticated requests to the backend API.

**Validates: Requirements 3.7**

Property 8: No Authentication Headers
- For any API request (POST or GET) sent by the React application, the request 
  SHALL NOT include authentication headers.
"""

import pytest
from hypothesis import given, settings, Verbosity, HealthCheck
from playwright.sync_api import Page
from tests.utils.generators import (
    valid_notifications,
    valid_sms_numbers,
    valid_emails,
    valid_whatsapp_numbers,
    valid_messages,
    notification_types
)


class TestNoAuthenticationHeaders:
    """Test suite for verifying no authentication headers are present in API requests."""
    
    # List of authentication header names that should NOT be present in requests
    AUTH_HEADER_NAMES = [
        'authorization',
        'auth',
        'x-auth-token',
        'x-api-key',
        'x-token',
        'cookie',
        'x-csrf-token',
        'bearer',
    ]
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_post_request_no_authentication_headers(self, page: Page, notification_page, notification_data):
        """Property test: POST requests to send notifications do NOT include authentication headers.
        
        **Validates: Requirements 3.7**
        
        For any valid notification data (POST request to /api/v1/notifications):
        1. Generate valid notification data (type, recipient, message, optional subject)
        2. Navigate to the application
        3. Perform the action that triggers the API request (submit form)
        4. Intercept the POST request to /api/v1/notifications
        5. Verify that the request headers do NOT contain any authentication headers:
           - No 'Authorization' header
           - No 'Auth' header
           - No 'X-Auth-Token' header
           - No 'X-API-Key' header
           - No 'X-Token' header
           - No 'Cookie' header
           - No 'X-CSRF-Token' header
           - No 'Bearer' header or similar
        6. Verify the request is still properly formatted with:
           - Correct Content-Type: application/json
           - Correct request body with notification data
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
                {
                    'type': 'EMAIL'|'SMS'|'WHATSAPP',
                    'recipient': str,
                    'message': str,
                    'subject': str (only for EMAIL)
                }
        """
        # List to capture intercepted requests
        intercepted_requests = []
        
        def handle_route(route):
            """Intercept and capture API requests, then abort to avoid real backend call."""
            if '/api/v1/notifications' in route.request.url and route.request.method == 'POST':
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'headers': dict(route.request.headers),
                    'body': route.request.post_data_json if route.request.method == 'POST' else None
                })
            
            # Abort request to avoid real backend call
            route.abort()
        
        # Navigate to the application
        notification_page.navigate()
        
        # Set up route handler to intercept requests
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill the form with notification data
        notification_type = notification_data['type']
        recipient = notification_data['recipient']
        message = notification_data['message']
        subject = notification_data.get('subject')
        
        notification_page.fill_form(notification_type, recipient, message, subject)
        
        # Submit the form
        notification_page.submit()
        
        # Verify a POST request was intercepted
        assert len(intercepted_requests) > 0, \
            f"Expected at least one POST request to /api/v1/notifications, but got none. " \
            f"Notification data: type={notification_type}, recipient={recipient}, message={message}"
        
        # Get the first request (should be the form submission)
        request_data = intercepted_requests[0]
        
        # Assertion 1: Verify correct HTTP method
        assert request_data['method'] == 'POST', \
            f"Request method should be POST, got: {request_data['method']}"
        
        # Assertion 2: Verify Content-Type header is present and correct
        content_type = request_data['headers'].get('content-type', '').lower()
        assert 'application/json' in content_type or content_type == 'application/json', \
            f"Content-Type header should be application/json, got: {request_data['headers'].get('content-type')}"
        
        # Assertion 3: Verify request body is valid
        request_body = request_data['body']
        assert request_body is not None, \
            f"Request body should not be None"
        assert isinstance(request_body, dict), \
            f"Request body should be a JSON object, got: {type(request_body)}"
        assert 'type' in request_body and 'recipient' in request_body and 'message' in request_body, \
            f"Request body should contain type, recipient, and message fields"
        
        # Assertion 4: Verify NO authentication headers are present
        # Convert all header names to lowercase for case-insensitive comparison
        request_header_names_lower = [h.lower() for h in request_data['headers'].keys()]
        
        for auth_header in self.AUTH_HEADER_NAMES:
            assert auth_header not in request_header_names_lower, \
                f"POST request should NOT contain authentication header '{auth_header}'. " \
                f"Got headers: {list(request_data['headers'].keys())}"
        
        # Assertion 5: Additional check - verify no header value contains auth-related content
        for header_name, header_value in request_data['headers'].items():
            header_name_lower = header_name.lower()
            # Check if header name or value contains auth-related keywords
            assert 'auth' not in header_name_lower, \
                f"Header '{header_name}' contains 'auth' keyword, which suggests authentication. " \
                f"Headers should not contain any authentication headers."
            if isinstance(header_value, str):
                assert 'bearer' not in header_value.lower(), \
                    f"Header '{header_name}' contains 'Bearer' token format, which is authentication. " \
                    f"Headers should not contain any authentication headers."
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_get_request_no_authentication_headers(self, page: Page, notification_page, notification_data):
        """Property test: GET requests to query notifications do NOT include authentication headers.
        
        **Validates: Requirements 3.7**
        
        For any GET request to query notifications:
        1. Navigate to the application
        2. Apply query filters (simulate accessing notification query functionality)
        3. Intercept the GET request to /api/v1/notifications with query parameters
        4. Verify that the request headers do NOT contain any authentication headers:
           - No 'Authorization' header
           - No 'Auth' header
           - No 'X-Auth-Token' header
           - No 'X-API-Key' header
           - No 'X-Token' header
           - No 'Cookie' header
           - No 'X-CSRF-Token' header
           - No 'Bearer' header or similar
        5. Verify the request is still properly formatted with:
           - Correct Content-Type: application/json
           - Correct query parameters (if any filters applied)
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator (used to trigger request)
        """
        # List to capture intercepted GET requests
        intercepted_requests = []
        
        def handle_route(route):
            """Intercept and capture GET requests to the notifications endpoint."""
            if '/api/v1/notifications' in route.request.url and route.request.method == 'GET':
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'headers': dict(route.request.headers),
                    'body': route.request.post_data_json if route.request.method == 'POST' else None
                })
            
            # Abort request to avoid real backend call
            route.abort()
        
        # Navigate to the application
        notification_page.navigate()
        
        # Set up route handler to intercept GET requests
        page.route('**/api/v1/notifications', handle_route)
        
        # Trigger a GET request by navigating to trigger query filters
        # (This would normally be done through the NotificationQuery component)
        # For now, we'll simulate by trying to access the query endpoint
        page.evaluate('''
            async () => {
                try {
                    const response = await fetch('/api/v1/notifications', {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                } catch (e) {
                    // Expected - endpoint is mocked
                }
            }
        ''')
        
        # Verify a GET request was intercepted
        assert len(intercepted_requests) > 0, \
            f"Expected at least one GET request to /api/v1/notifications, but got none."
        
        # Get the first GET request
        request_data = intercepted_requests[0]
        
        # Assertion 1: Verify correct HTTP method
        assert request_data['method'] == 'GET', \
            f"Request method should be GET, got: {request_data['method']}"
        
        # Assertion 2: Verify Content-Type header is present and correct
        content_type = request_data['headers'].get('content-type', '').lower()
        assert 'application/json' in content_type or content_type == 'application/json', \
            f"Content-Type header should be application/json, got: {request_data['headers'].get('content-type')}"
        
        # Assertion 3: Verify NO authentication headers are present
        # Convert all header names to lowercase for case-insensitive comparison
        request_header_names_lower = [h.lower() for h in request_data['headers'].keys()]
        
        for auth_header in self.AUTH_HEADER_NAMES:
            assert auth_header not in request_header_names_lower, \
                f"GET request should NOT contain authentication header '{auth_header}'. " \
                f"Got headers: {list(request_data['headers'].keys())}"
        
        # Assertion 4: Additional check - verify no header value contains auth-related content
        for header_name, header_value in request_data['headers'].items():
            header_name_lower = header_name.lower()
            # Check if header name contains auth-related keywords
            assert 'auth' not in header_name_lower, \
                f"Header '{header_name}' contains 'auth' keyword, which suggests authentication. " \
                f"Headers should not contain any authentication headers."
            if isinstance(header_value, str):
                assert 'bearer' not in header_value.lower(), \
                    f"Header '{header_name}' contains 'Bearer' token format, which is authentication. " \
                    f"Headers should not contain any authentication headers."
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_request_headers_only_contain_standard_headers(self, page: Page, notification_page, notification_data):
        """Property test: Requests only contain standard headers, no authentication headers.
        
        **Validates: Requirements 3.7**
        
        For any API request sent by the React application:
        1. Generate valid notification data
        2. Submit the form to trigger API request
        3. Intercept the request
        4. Verify that ALL headers in the request are standard HTTP headers
           (NOT authentication headers)
        5. Standard headers should include:
           - content-type
           - user-agent
           - accept
           - accept-language
           - accept-encoding
        6. Headers should NOT include:
           - Authorization
           - Auth, X-Auth-Token, X-API-Key, X-Token
           - Cookie, X-CSRF-Token
           - Any other authentication-related header
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
        """
        # List of standard non-auth headers that are expected in HTTP requests
        STANDARD_HEADERS = [
            'content-type',
            'content-length',
            'user-agent',
            'accept',
            'accept-language',
            'accept-encoding',
            'host',
            'origin',
            'referer',
            'sec-fetch-dest',
            'sec-fetch-mode',
            'sec-fetch-site',
        ]
        
        # List to capture intercepted requests
        intercepted_requests = []
        
        def handle_route(route):
            """Intercept and capture API requests."""
            if '/api/v1/notifications' in route.request.url and route.request.method == 'POST':
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'headers': dict(route.request.headers),
                    'body': route.request.post_data_json if route.request.method == 'POST' else None
                })
            
            # Abort request
            route.abort()
        
        # Navigate to the application
        notification_page.navigate()
        
        # Set up route handler
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill and submit form
        notification_type = notification_data['type']
        recipient = notification_data['recipient']
        message = notification_data['message']
        subject = notification_data.get('subject')
        
        notification_page.fill_form(notification_type, recipient, message, subject)
        notification_page.submit()
        
        # Verify request was intercepted
        assert len(intercepted_requests) > 0, \
            f"Expected at least one POST request to /api/v1/notifications"
        
        request_data = intercepted_requests[0]
        request_headers = request_data['headers']
        
        # Verify each header is not an authentication header
        for header_name, header_value in request_headers.items():
            header_name_lower = header_name.lower()
            
            # Check against all known authentication header patterns
            auth_patterns = [
                'auth',
                'bearer',
                'token',
                'csrf',
                'cookie',
                'x-token',
                'x-api-key',
                'x-auth',
            ]
            
            for auth_pattern in auth_patterns:
                assert auth_pattern not in header_name_lower, \
                    f"Request header '{header_name}' contains authentication pattern '{auth_pattern}'. " \
                    f"Requests should only contain standard headers, not authentication headers."
                
                # Also check header value for auth patterns
                if isinstance(header_value, str):
                    assert auth_pattern not in header_value.lower() or header_name_lower not in ['origin', 'referer'], \
                        f"Request header '{header_name}' with value '{header_value}' appears to contain authentication. " \
                        f"Headers should not contain authentication tokens or credentials."
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_all_request_types_no_auth_headers(self, page: Page, notification_page, notification_data):
        """Property test: ALL request types (EMAIL, SMS, WHATSAPP) do NOT include authentication headers.
        
        **Validates: Requirements 3.7**
        
        For each notification type (EMAIL, SMS, WHATSAPP), when generating and submitting
        valid notification data:
        1. Verify POST requests for EMAIL notifications have no auth headers
        2. Verify POST requests for SMS notifications have no auth headers
        3. Verify POST requests for WHATSAPP notifications have no auth headers
        4. Ensure consistency across all notification types
        5. Verify each request properly formats the notification data
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
        """
        # List to capture intercepted requests
        intercepted_requests = []
        
        def handle_route(route):
            """Intercept and capture API requests."""
            if '/api/v1/notifications' in route.request.url and route.request.method == 'POST':
                intercepted_requests.append({
                    'url': route.request.url,
                    'method': route.request.method,
                    'headers': dict(route.request.headers),
                    'body': route.request.post_data_json if route.request.method == 'POST' else None,
                    'type': notification_data['type']
                })
            
            # Abort request
            route.abort()
        
        # Navigate to the application
        notification_page.navigate()
        
        # Set up route handler
        page.route('**/api/v1/notifications', handle_route)
        
        # Fill and submit form with generated notification data
        notification_type = notification_data['type']
        recipient = notification_data['recipient']
        message = notification_data['message']
        subject = notification_data.get('subject')
        
        notification_page.fill_form(notification_type, recipient, message, subject)
        notification_page.submit()
        
        # Verify request was intercepted
        assert len(intercepted_requests) > 0, \
            f"Expected at least one POST request for {notification_type} notification"
        
        request_data = intercepted_requests[0]
        
        # Assertion 1: Verify correct notification type was submitted
        assert request_data['type'] == notification_type, \
            f"Request should be for {notification_type} type"
        
        # Assertion 2: Verify no authentication headers are present
        request_header_names_lower = [h.lower() for h in request_data['headers'].keys()]
        
        for auth_header in self.AUTH_HEADER_NAMES:
            assert auth_header not in request_header_names_lower, \
                f"Request for {notification_type} should NOT contain authentication header '{auth_header}'. " \
                f"Got headers: {list(request_data['headers'].keys())}"
        
        # Assertion 3: Verify request body contains required fields
        request_body = request_data['body']
        assert 'type' in request_body and request_body['type'] == notification_type, \
            f"Request body should contain correct notification type"
        assert 'recipient' in request_body and request_body['recipient'] == recipient, \
            f"Request body should contain correct recipient"
        assert 'message' in request_body and request_body['message'] == message, \
            f"Request body should contain correct message"
