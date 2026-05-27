"""
Smoke tests to verify Playwright and Page Object Models are working correctly.

These tests validate that:
- Playwright can launch and interact with the browser
- Page Object Models can interact with the React application
- Fixtures are properly initialized
"""

import pytest
from pages.notification_page import NotificationPage
from pages.query_page import QueryPage


@pytest.mark.unit_test
def test_playwright_is_working(page):
    """Verify that Playwright can launch and navigate to a page."""
    page.goto('http://localhost:5173/')
    assert page.title() is not None
    print("✓ Playwright is working correctly")


@pytest.mark.unit_test
def test_notification_page_can_interact_with_app(notification_page):
    """Verify that NotificationPage can interact with the React application."""
    notification_page.navigate()
    
    # Verify page loaded
    assert notification_page.page.url == 'http://localhost:5173/'
    
    # Verify form elements are accessible
    assert notification_page.type_select.is_visible()
    assert notification_page.recipient_input.is_visible()
    assert notification_page.message_input.is_visible()
    assert notification_page.submit_button.is_visible()
    
    print("✓ NotificationPage can interact with React application")


@pytest.mark.unit_test
def test_query_page_can_interact_with_app(query_page):
    """Verify that QueryPage can interact with the React application."""
    query_page.navigate()
    
    # Verify page loaded
    assert query_page.page.url == 'http://localhost:5173/'
    
    # Verify query elements are accessible
    assert query_page.type_filter.is_visible()
    assert query_page.search_button.is_visible()
    
    print("✓ QueryPage can interact with React application")


@pytest.mark.unit_test
def test_fixtures_are_properly_initialized(notification_page, query_page, test_data):
    """Verify that all fixtures are properly initialized."""
    # Verify notification_page fixture
    assert isinstance(notification_page, NotificationPage)
    assert notification_page.page is not None
    
    # Verify query_page fixture
    assert isinstance(query_page, QueryPage)
    assert query_page.page is not None
    
    # Verify test_data fixture
    assert 'valid_email' in test_data
    assert 'valid_sms' in test_data
    assert 'valid_whatsapp' in test_data
    
    print("✓ All fixtures are properly initialized")


@pytest.mark.unit_test
def test_notification_page_methods_work(notification_page):
    """Verify that NotificationPage methods work correctly."""
    notification_page.navigate()
    
    # Test select_type method
    notification_page.select_type('EMAIL')
    
    # Test is_subject_visible method
    is_visible = notification_page.is_subject_visible()
    assert isinstance(is_visible, bool)
    
    # Test fill_form method (without submitting)
    notification_page.fill_form('EMAIL', 'test@example.com', 'Test message', 'Test subject')
    
    print("✓ NotificationPage methods work correctly")


@pytest.mark.unit_test
def test_query_page_methods_work(query_page):
    """Verify that QueryPage methods work correctly."""
    query_page.navigate()
    
    # Test apply_filters method
    query_page.apply_filters(notification_type='EMAIL', status='SENT')
    
    # Test has_no_results_message method
    has_message = query_page.has_no_results_message()
    assert isinstance(has_message, bool)
    
    print("✓ QueryPage methods work correctly")
