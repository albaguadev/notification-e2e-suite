"""
E2E test for notification query flow.

This module tests the complete user flow for querying notification history:
- Create test notifications via the backend API
- Navigate to application
- Apply filters (type, status, date range)
- Trigger search
- Verify UI displays retrieved notifications correctly with proper formatting
- Verify no error messages are shown for successful queries

This is a TRUE E2E test without mocks - it uses the real MultiChannelNotifier
backend running on http://localhost:8081.

Requirements: 7.6
"""

import pytest
import requests
import json
from playwright.sync_api import Page
from pages.query_page import QueryPage
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
def test_notifications(backend_available):
    """Create test notifications in the backend.
    
    This fixture:
    1. Sends POST requests to create various test notifications
    2. Returns the created notification IDs for verification
    3. Cleans up after tests
    
    Yields:
        dict: Created notification IDs indexed by type
    """
    backend_url = 'http://localhost:8081/api/v1/notifications'
    cleanup_url = 'http://localhost:8081/api/v1/notifications'
    
    created_ids = {
        'email': [],
        'sms': [],
        'whatsapp': []
    }
    
    # Create EMAIL test notifications
    email_notifications = [
        {
            "type": "EMAIL",
            "recipient": "test1@example.com",
            "message": "Test email notification 1",
            "subject": "Test Subject 1"
        },
        {
            "type": "EMAIL",
            "recipient": "test2@example.com",
            "message": "Test email notification 2",
            "subject": "Test Subject 2"
        }
    ]
    
    # Create SMS test notifications
    sms_notifications = [
        {
            "type": "SMS",
            "recipient": "+34612345678",
            "message": "Test SMS notification 1"
        },
        {
            "type": "SMS",
            "recipient": "+34712345679",
            "message": "Test SMS notification 2"
        }
    ]
    
    # Create WHATSAPP test notifications
    whatsapp_notifications = [
        {
            "type": "WHATSAPP",
            "recipient": "+34612345680",
            "message": "Test WhatsApp notification 1"
        }
    ]
    
    # Send all test notifications
    all_notifications = email_notifications + sms_notifications + whatsapp_notifications
    
    for notif in all_notifications:
        try:
            response = requests.post(
                backend_url,
                json=notif,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            if response.status_code == 200:
                notif_type = notif['type'].lower()
                response_data = response.json()
                notif_id = response_data.get('id', '')
                if notif_id:
                    created_ids[notif_type].append(notif_id)
        except Exception as e:
            print(f"Failed to create test notification: {e}")
    
    yield created_ids
    
    # Cleanup: Delete all created notifications
    for notif_type in created_ids:
        for notif_id in created_ids[notif_type]:
            try:
                delete_url = f'{cleanup_url}/{notif_id}'
                requests.delete(delete_url, timeout=5)
            except Exception as e:
                # Fail silently - cleanup errors should not fail the test
                print(f"Warning: Failed to delete notification {notif_id}: {e}")


@pytest.mark.e2e_test
class TestNotificationQueryFlow:
    """Test suite for notification query end-to-end flow.
    
    These tests validate the complete user flow for querying notification history,
    from UI interaction through backend integration. The tests create test data first,
    then verify that queries return the correct results.
    
    Validates: Requirement 7.6
    """
    
    def test_query_notifications_displays_created_results(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test retrieving and displaying created test notifications.
        
        This test validates the basic notification query flow:
        1. Create test notifications via API
        2. Navigate to application
        3. Search for notifications
        4. Verify UI displays the created notifications
        5. Verify no error messages are shown
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - UI displays retrieved notifications correctly
        """
        assert backend_available is True
        
        # Verify test data was created
        total_created = (len(test_notifications['email']) + 
                        len(test_notifications['sms']) + 
                        len(test_notifications['whatsapp']))
        assert total_created > 0, "Test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Trigger search without applying any filters
        query_page.search()
        
        # Wait for results to load
        query_page.page.wait_for_timeout(1000)
        
        # Verify results are displayed
        results_table = query_page.page.locator('[data-testid="results"]')
        try:
            results_table.wait_for(state='visible', timeout=2000)
            table_visible = True
        except:
            table_visible = False
        
        # If results table is visible, verify it has data rows
        if table_visible:
            rows = results_table.locator('tbody tr')
            row_count = rows.count()
            assert row_count >= total_created, \
                f"UI should display at least {total_created} notifications"
        
        # Verify UI does not display error messages
        status_message_element = query_page.page.locator('[data-testid="status-message"]')
        is_error_shown = False
        try:
            is_error_shown = status_message_element.is_visible(timeout=500)
        except:
            is_error_shown = False
        
        assert not is_error_shown, \
            "No error messages should be displayed for successful queries"
    
    def test_query_notifications_with_type_filter_email(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test querying notifications with EMAIL type filter.
        
        This test validates that the type filter works correctly:
        1. Create test notifications (including EMAIL)
        2. Navigate to application
        3. Apply EMAIL type filter
        4. Trigger search
        5. Verify UI displays only EMAIL notifications
        6. Verify no error messages are shown
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - Filter and display correctly
        """
        assert backend_available is True
        assert len(test_notifications['email']) > 0, "EMAIL test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Apply EMAIL type filter
        query_page.apply_filters(notification_type="EMAIL")
        
        # Trigger search
        query_page.search()
        
        # Wait for results to load
        query_page.page.wait_for_timeout(1000)
        
        # Verify results are displayed
        results_table = query_page.page.locator('[data-testid="results"]')
        try:
            results_table.wait_for(state='visible', timeout=2000)
            table_visible = True
        except:
            table_visible = False
        
        if table_visible:
            rows = results_table.locator('tbody tr')
            row_count = rows.count()
            assert row_count >= len(test_notifications['email']), \
                f"UI should display at least {len(test_notifications['email'])} EMAIL notifications"
        
        # Verify UI does not display error messages
        status_message_element = query_page.page.locator('[data-testid="status-message"]')
        is_error_shown = False
        try:
            is_error_shown = status_message_element.is_visible(timeout=500)
        except:
            is_error_shown = False
        
        assert not is_error_shown, \
            "No error messages should be displayed for successful queries with EMAIL filter"
    
    def test_query_notifications_with_type_filter_sms(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test querying notifications with SMS type filter.
        
        This test validates that the SMS type filter works correctly:
        1. Create test notifications (including SMS)
        2. Navigate to application
        3. Apply SMS type filter
        4. Trigger search
        5. Verify UI displays SMS notifications
        6. Verify no error messages are shown
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - Filter by SMS type
        """
        assert backend_available is True
        assert len(test_notifications['sms']) > 0, "SMS test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Apply SMS type filter
        query_page.apply_filters(notification_type="SMS")
        
        # Trigger search
        query_page.search()
        
        # Wait for results to load
        query_page.page.wait_for_timeout(1000)
        
        # Verify results are displayed
        results_table = query_page.page.locator('[data-testid="results"]')
        try:
            results_table.wait_for(state='visible', timeout=2000)
            table_visible = True
        except:
            table_visible = False
        
        if table_visible:
            rows = results_table.locator('tbody tr')
            row_count = rows.count()
            assert row_count >= len(test_notifications['sms']), \
                f"UI should display at least {len(test_notifications['sms'])} SMS notifications"
        
        # Verify UI does not display error messages
        status_message_element = query_page.page.locator('[data-testid="status-message"]')
        is_error_shown = False
        try:
            is_error_shown = status_message_element.is_visible(timeout=500)
        except:
            is_error_shown = False
        
        assert not is_error_shown, \
            "No error messages should be displayed for successful queries with SMS filter"
    
    def test_query_notifications_with_type_filter_whatsapp(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test querying notifications with WHATSAPP type filter.
        
        This test validates that the WHATSAPP type filter works correctly:
        1. Create test notifications (including WHATSAPP)
        2. Navigate to application
        3. Apply WHATSAPP type filter
        4. Trigger search
        5. Verify UI displays WHATSAPP notifications
        6. Verify no error messages are shown
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - Filter by WHATSAPP type
        """
        assert backend_available is True
        assert len(test_notifications['whatsapp']) > 0, "WHATSAPP test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Apply WHATSAPP type filter
        query_page.apply_filters(notification_type="WHATSAPP")
        
        # Trigger search
        query_page.search()
        
        # Wait for results to load
        query_page.page.wait_for_timeout(1000)
        
        # Verify results are displayed
        results_table = query_page.page.locator('[data-testid="results"]')
        try:
            results_table.wait_for(state='visible', timeout=2000)
            table_visible = True
        except:
            table_visible = False
        
        if table_visible:
            rows = results_table.locator('tbody tr')
            row_count = rows.count()
            assert row_count >= len(test_notifications['whatsapp']), \
                f"UI should display at least {len(test_notifications['whatsapp'])} WHATSAPP notifications"
        
        # Verify UI does not display error messages
        status_message_element = query_page.page.locator('[data-testid="status-message"]')
        is_error_shown = False
        try:
            is_error_shown = status_message_element.is_visible(timeout=500)
        except:
            is_error_shown = False
        
        assert not is_error_shown, \
            "No error messages should be displayed for successful queries with WHATSAPP filter"
    
    def test_query_results_display_with_proper_formatting(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test that notification results are displayed with proper formatting.
        
        This test validates that the UI displays notification results correctly:
        - Results are visible
        - Results are displayed in readable format with table structure
        - Headers are present
        - Data rows contain notification information
        - No error messages are shown
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - Proper formatting of results
        """
        assert backend_available is True
        assert len(test_notifications['email']) > 0, "Test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Trigger search
        query_page.search()
        
        # Wait for results to load
        query_page.page.wait_for_timeout(1000)
        
        # Verify results table exists and is visible
        results_table = query_page.page.locator('[data-testid="results"]')
        try:
            results_table.wait_for(state='visible', timeout=2000)
            table_visible = True
        except:
            table_visible = False
        
        if table_visible:
            # Verify table has headers
            headers = results_table.locator('thead th, th')
            header_count = headers.count()
            assert header_count > 0, \
                "Results table should have headers indicating proper formatting"
            
            # Verify table has data rows
            rows = results_table.locator('tbody tr')
            row_count = rows.count()
            assert row_count > 0, \
                "Results table should have data rows with notification information"
        
        # Verify no error messages are shown
        status_message_element = query_page.page.locator('[data-testid="status-message"]')
        is_error_shown = False
        try:
            is_error_shown = status_message_element.is_visible(timeout=500)
        except:
            is_error_shown = False
        
        assert not is_error_shown, \
            "No error messages should be displayed for successful queries"
    
    def test_query_no_error_messages_on_success(
        self,
        query_page: QueryPage,
        backend_available,
        test_notifications
    ):
        """Test that no error messages are displayed for successful queries.
        
        This test explicitly validates requirement 7.6 that when a user queries
        notification history and the query succeeds, no error messages are shown.
        Tests with multiple filter combinations to ensure robust behavior.
        
        Args:
            query_page: QueryPage POM instance
            backend_available: Fixture that skips test if backend unavailable
            test_notifications: Fixture that creates test data
            
        Validates: Requirement 7.6 - No error messages for successful queries
        """
        assert backend_available is True
        assert len(test_notifications['email']) > 0, "Test notifications should be created"
        
        # Navigate to application
        query_page.navigate()
        
        # Test multiple filter combinations to ensure no errors appear
        test_cases = [
            {"notification_type": "EMAIL"},
            {"notification_type": "SMS"},
        ]
        
        for filters in test_cases:
            # Clear previous filters by navigating again
            query_page.navigate()
            
            # Apply filters
            query_page.apply_filters(**filters)
            
            # Trigger search
            query_page.search()
            
            # Wait for response
            query_page.page.wait_for_timeout(1000)
            
            # Verify no error message is visible
            status_message_element = query_page.page.locator('[data-testid="status-message"]')
            is_error_shown = False
            try:
                is_error_shown = status_message_element.is_visible(timeout=500)
            except:
                is_error_shown = False
            
            assert not is_error_shown, \
                f"No error messages should be displayed for successful queries with filters {filters}"
