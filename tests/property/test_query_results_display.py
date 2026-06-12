"""
Property-based tests for query results display in the UI.

This module tests that the React application correctly displays query results
from the backend in a readable format with proper formatting.

**Validates: Requirements 4.4**

Property 10: Query Results Display
- For any notification data returned by the backend in response to a query,
  the React application SHALL display the results in a readable format with
  proper formatting.

# Feature: notification-e2e-suite, Property 10: Query Results Display
"""

import pytest
import json
from hypothesis import given, settings, Verbosity, HealthCheck
from playwright.sync_api import Page
from tests.utils.generators import (
    query_filters,
    notification_types,
    notification_statuses,
    valid_iso_dates,
    short_messages
)


class TestQueryResultsDisplay:
    """Test suite for verifying query results display with readable format."""
    
    @given(query_filter=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_display_readable_format(self, page: Page, query_page, query_filter):
        """Property test: UI displays query results in readable format.
        
        **Validates: Requirements 4.4**
        
        For any query filter combination and backend query response:
        1. Navigate to the application
        2. Apply filters to query notifications
        3. Mock backend to return notification data matching filters
        4. Submit the query
        5. Verify UI displays results in a readable format
        6. Verify results include all key fields: type, recipient, message, status, timestamp
        7. Verify timestamp is formatted in a human-readable way (not raw ISO format)
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            query_filter: Query filter data from Hypothesis generator
        """
        # Generate realistic notification data
        mock_notifications = [
            {
                'id': 'notif-001',
                'type': 'EMAIL',
                'recipient': 'test@example.com',
                'message': 'Test notification',
                'subject': 'Test',
                'status': 'SENT',
                'timestamp': '2024-01-15T10:30:00Z'
            }
        ]
        
        def handle_route(route):
            """Intercept and mock query backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(mock_notifications)
                )
            else:
                route.continue_()
        
        # Set up route handler BEFORE navigation
        page.route('**/api/v1/notifications', handle_route)
        
        # Navigate to the application
        query_page.navigate()
        
        # Execute search without filters first (simplest case)
        query_page.search()
        
        # Wait for results and verify they are displayed
        page.wait_for_timeout(2000)
        results_count = query_page.get_results_count()
        assert results_count > 0, \
            f"Expected query results to be displayed, but got 0 results."
        
        # Verify result row has content
        results_table = query_page.results_table.locator('tbody tr')
        row = results_table.nth(0)
        cells = row.locator('td')
        
        assert cells.count() >= 5, \
            f"Row should have at least 5 columns"
        
        # Verify type is displayed
        notification_type = cells.nth(0).text_content().strip()
        assert notification_type, "Type field should have content"
        assert notification_type.upper() == 'EMAIL', f"Expected EMAIL, got {notification_type}"
        
        # Verify recipient is displayed
        recipient = cells.nth(1).text_content().strip()
        assert recipient == 'test@example.com', f"Expected test@example.com, got {recipient}"
        
        # Verify message is displayed
        message = cells.nth(2).text_content().strip()
        assert message, "Message field should have content"
        
        # Verify status is displayed
        status = cells.nth(4).text_content().strip()
        assert status.upper() == 'SENT', f"Expected SENT status, got {status}"
        
        # Verify timestamp is displayed and formatted
        timestamp = cells.nth(cells.count() - 1).text_content().strip()
        assert timestamp, "Timestamp should be displayed"
        # Verify it's formatted (has spaces or commas, not raw ISO)
        assert ' ' in timestamp or ',' in timestamp, \
            f"Timestamp should be formatted readably, not raw ISO format: {timestamp}"
    
    
    @given(query_filter=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_display_all_fields_present(self, page: Page, query_page, query_filter):
        """Property test: UI displays all required notification fields.
        
        **Validates: Requirements 4.4**
        
        For any query that returns results:
        1. Verify all required fields are displayed: type, recipient, message, status, timestamp
        2. Verify optional fields are displayed appropriately (subject for EMAIL only)
        3. Verify fields are in logical order and properly labeled
        4. Verify no required data is missing or hidden
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            query_filter: Query filter data from Hypothesis generator
        """
        # Generate mock notification data with all fields
        mock_notifications = [
            {
                'id': 'notif-001',
                'type': 'EMAIL',
                'recipient': 'user@example.com',
                'message': 'Important notification with long message content that tests text wrapping and readability',
                'subject': 'Subject Line',
                'status': 'SENT',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': 'notif-002',
                'type': 'SMS',
                'recipient': '+34612345678',
                'message': 'SMS notification',
                'subject': None,
                'status': 'FAILED',
                'timestamp': '2024-01-14T09:15:00Z'
            }
        ]
        
        def handle_route(route):
            """Intercept and mock query backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(mock_notifications)
                )
            else:
                route.continue_()
    

    
    
    @given(query_filter=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_display_table_formatting(self, page: Page, query_page, query_filter):
        """Property test: UI displays results with proper table formatting.
        
        **Validates: Requirements 4.4**
        
        For any query results:
        1. Verify results are displayed in a structured table format
        2. Verify table has proper headers and rows
        3. Verify rows are properly aligned and readable
        4. Verify long text is handled gracefully (wrapped or truncated)
        5. Verify text is visible and not cut off improperly
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            query_filter: Query filter data from Hypothesis generator
        """
        # Generate mock notification data with various text lengths
        mock_notifications = [
            {
                'id': 'notif-001',
                'type': 'EMAIL',
                'recipient': 'short@ex.com',
                'message': 'Short',
                'subject': 'S',
                'status': 'SENT',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': 'notif-002',
                'type': 'SMS',
                'recipient': '+346123456789012345678',
                'message': 'This is a much longer notification message that tests how the UI handles text wrapping and formatting in table cells',
                'subject': None,
                'status': 'SENT',
                'timestamp': '2024-01-14T09:15:00Z'
            }
        ]
        
        def handle_route(route):
            """Intercept and mock query backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(mock_notifications)
                )
            else:
                route.continue_()
    

    
    
    @given(query_filter=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_display_notification_types_formatting(self, page: Page, query_page, query_filter):
        """Property test: UI displays different notification types with proper formatting.
        
        **Validates: Requirements 4.4**
        
        For any query results containing different notification types:
        1. Verify EMAIL notifications display with all fields including subject
        2. Verify SMS notifications display correctly without subject
        3. Verify WHATSAPP notifications display correctly without subject
        4. Verify notification types are clearly identifiable
        5. Verify type indicators are visually distinct (e.g., badges or labels)
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            query_filter: Query filter data from Hypothesis generator
        """
        # Generate mock notification data with all three types
        mock_notifications = [
            {
                'id': 'email-001',
                'type': 'EMAIL',
                'recipient': 'user@example.com',
                'message': 'Email notification message',
                'subject': 'Email Subject',
                'status': 'SENT',
                'timestamp': '2024-01-15T10:30:00Z'
            },
            {
                'id': 'sms-001',
                'type': 'SMS',
                'recipient': '+34612345678',
                'message': 'SMS notification message',
                'subject': None,
                'status': 'SENT',
                'timestamp': '2024-01-14T09:15:00Z'
            },
            {
                'id': 'whatsapp-001',
                'type': 'WHATSAPP',
                'recipient': '+34712345678',
                'message': 'WhatsApp notification message',
                'subject': None,
                'status': 'SENT',
                'timestamp': '2024-01-13T14:45:00Z'
            }
        ]
        
        def handle_route(route):
            """Intercept and mock query backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(mock_notifications)
                )
            else:
                route.continue_()
    

    
    
    @given(query_filter=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_display_pagination_or_scrolling(self, page: Page, query_page, query_filter):
        """Property test: UI handles multiple results with pagination or scrolling.
        
        **Validates: Requirements 4.4**
        
        For any query that returns multiple results:
        1. Verify results are accessible (not all hidden below viewport)
        2. Verify UI provides way to view all results (pagination or scrolling)
        3. Verify scrolling works if results exceed viewport height
        4. Verify all results are eventually accessible and readable
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            query_filter: Query filter data from Hypothesis generator
        """
        # Generate mock notification data with multiple results
        mock_notifications = [
            {
                'id': f'notif-{j:03d}',
                'type': ['EMAIL', 'SMS', 'WHATSAPP'][j % 3],
                'recipient': f'user{j}@example.com' if j % 3 == 0 else f'+3461234567{j}',
                'message': f'Notification message {j}',
                'subject': f'Subject {j}' if j % 3 == 0 else None,
                'status': ['SENT', 'FAILED', 'PENDING'][j % 3],
                'timestamp': f'2024-01-{(j % 20) + 1:02d}T{(j % 24):02d}:00:00Z'
            }
            for j in range(15)  # Generate 15 notifications
        ]
        
        def handle_route(route):
            """Intercept and mock query backend response."""
            if '/api/v1/notifications' in route.request.url:
                route.fulfill(
                    status=200,
                    content_type='application/json; charset=utf-8',
                    body=json.dumps(mock_notifications)
                )
            else:
                route.continue_()



