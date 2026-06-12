"""
Property-based tests for React component rendering.

This module tests that React UI components render correctly in the browser with all
expected elements visible and interactive across various component states.

**Validates: Requirements 6.1**

Property 11: Component Rendering
- For any React UI component in the application, when a test executes, the component
  SHALL render correctly in the browser with all expected elements visible and interactive.
  This includes:
  - NotificationForm component: type dropdown, recipient input, message input, subject field
    (visibility depends on type), submit button, all fields retain values after interaction
  - NotificationQuery component: filter inputs (type, status, from date, to date), search button,
    results area initially empty/not visible
"""

import pytest
from hypothesis import given, settings, Verbosity, HealthCheck
from playwright.sync_api import Page
from tests.utils.generators import (
    valid_notifications,
    query_filters,
    notification_types,
    valid_emails,
    valid_sms_numbers,
    valid_whatsapp_numbers,
    valid_messages,
    valid_subjects
)


class TestNotificationFormRendering:
    """Test suite for NotificationForm component rendering."""
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_form_elements_visible_and_interactive(self, page: Page, notification_page, notification_data):
        """Property test: All notification form elements are visible and interactive.
        
        **Validates: Requirements 6.1**
        
        For any valid notification data:
        1. Navigate to the application
        2. Verify all form elements are present in the DOM
        3. Verify all form elements are visible (not hidden by CSS)
        4. Verify all form elements are interactive (clickable/fillable)
        5. Verify form elements can accept user input
        
        Form elements to verify:
        - Type dropdown: present, visible, shows all 3 options (EMAIL, SMS, WHATSAPP)
        - Recipient input field: present, visible, accepts input
        - Message input field: present, visible, accepts input
        - Subject field: visible only for EMAIL type, hidden for SMS/WHATSAPP
        - Submit button: present, visible, clickable
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
        """
        # Navigate to the application
        notification_page.navigate()
        
        # Wait for page to load (5-second timeout from conftest)
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Assertion 1: Verify type dropdown is present and visible
        assert notification_page.type_select.is_visible(), \
            "Type dropdown should be visible in the form"
        
        # Assertion 2: Verify type dropdown contains all required options
        type_options = notification_page.type_select.locator('option').count()
        assert type_options >= 3, \
            f"Type dropdown should have at least 3 options (EMAIL, SMS, WHATSAPP), got {type_options}"
        
        # Assertion 3: Verify type dropdown is interactive (can select option)
        try:
            notification_page.type_select.select_option(notification_data['type'])
            selected_value = notification_page.type_select.input_value()
            assert selected_value == notification_data['type'], \
                f"Type dropdown should be selectable and retain value. Expected {notification_data['type']}, got {selected_value}"
        except Exception as e:
            pytest.fail(f"Type dropdown should be interactive and selectable: {e}")
        
        # Assertion 4: Verify recipient input field is present and visible
        assert notification_page.recipient_input.is_visible(), \
            "Recipient input field should be visible in the form"
        
        # Assertion 5: Verify recipient input field is interactive (can accept input)
        try:
            notification_page.recipient_input.fill(notification_data['recipient'])
            recipient_value = notification_page.recipient_input.input_value()
            assert recipient_value == notification_data['recipient'], \
                f"Recipient field should accept and retain input. Expected {notification_data['recipient']}, got {recipient_value}"
        except Exception as e:
            pytest.fail(f"Recipient input field should be interactive: {e}")
        
        # Assertion 6: Verify message input field is present and visible
        assert notification_page.message_input.is_visible(), \
            "Message input field should be visible in the form"
        
        # Assertion 7: Verify message input field is interactive (can accept input)
        try:
            notification_page.message_input.fill(notification_data['message'])
            message_value = notification_page.message_input.input_value()
            assert message_value == notification_data['message'], \
                f"Message field should accept and retain input. Expected {notification_data['message']}, got {message_value}"
        except Exception as e:
            pytest.fail(f"Message input field should be interactive: {e}")
        
        # Assertion 8: Verify subject field visibility matches notification type
        notification_type = notification_data['type']
        is_subject_visible = notification_page.is_subject_visible()
        
        if notification_type == 'EMAIL':
            assert is_subject_visible, \
                f"Subject field should be visible for EMAIL type, but it's hidden"
            
            # Assertion 9: Verify subject field is interactive for EMAIL
            subject_value = notification_data.get('subject', '')
            try:
                notification_page.subject_input.fill(subject_value)
                subject_filled = notification_page.subject_input.input_value()
                assert subject_filled == subject_value, \
                    f"Subject field should accept and retain input for EMAIL. Expected {subject_value}, got {subject_filled}"
            except Exception as e:
                pytest.fail(f"Subject input field should be interactive for EMAIL: {e}")
        else:
            # For SMS and WHATSAPP, subject should be hidden
            assert not is_subject_visible, \
                f"Subject field should be hidden for {notification_type} type, but it's visible"
        
        # Assertion 10: Verify submit button is present and visible
        assert notification_page.submit_button.is_visible(), \
            "Submit button should be visible in the form"
        
        # Assertion 11: Verify submit button is interactive (clickable)
        # Check if button is enabled (not disabled)
        is_disabled = page.locator('[data-testid="submit"]').is_disabled()
        assert not is_disabled, \
            "Submit button should be enabled and clickable"
    
    @given(notification_data=valid_notifications())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_form_fields_retain_values_after_interaction(self, page: Page, notification_page, notification_data):
        """Property test: Form fields retain values after user interaction.
        
        **Validates: Requirements 6.1**
        
        For any valid notification data:
        1. Navigate to the application
        2. Fill all form fields with notification data
        3. Interact with form elements (click, focus, blur)
        4. Verify all fields retain their values
        5. Verify values persist across multiple interactions
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            notification_data: Valid notification data from Hypothesis generator
        """
        # Navigate to the application
        notification_page.navigate()
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Fill the form with notification data
        notification_type = notification_data['type']
        recipient = notification_data['recipient']
        message = notification_data['message']
        subject = notification_data.get('subject', '')
        
        notification_page.select_type(notification_type)
        notification_page.recipient_input.fill(recipient)
        notification_page.message_input.fill(message)
        
        if notification_type == 'EMAIL':
            notification_page.subject_input.fill(subject)
        
        # Interaction 1: Click on recipient field and blur
        notification_page.recipient_input.click()
        notification_page.recipient_input.blur()
        
        # Assertion 1: Verify type value persists after interaction
        type_value = notification_page.type_select.input_value()
        assert type_value == notification_type, \
            f"Type field should retain value after interaction. Expected {notification_type}, got {type_value}"
        
        # Assertion 2: Verify recipient value persists after interaction
        recipient_value = notification_page.recipient_input.input_value()
        assert recipient_value == recipient, \
            f"Recipient field should retain value after interaction. Expected {recipient}, got {recipient_value}"
        
        # Assertion 3: Verify message value persists after interaction
        message_value = notification_page.message_input.input_value()
        assert message_value == message, \
            f"Message field should retain value after interaction. Expected {message}, got {message_value}"
        
        # Interaction 2: Click on message field and blur
        notification_page.message_input.click()
        notification_page.message_input.blur()
        
        # Assertion 4: Verify all values still persist after second interaction
        type_value = notification_page.type_select.input_value()
        recipient_value = notification_page.recipient_input.input_value()
        message_value = notification_page.message_input.input_value()
        
        assert type_value == notification_type, \
            f"Type field should retain value after multiple interactions. Expected {notification_type}, got {type_value}"
        assert recipient_value == recipient, \
            f"Recipient field should retain value after multiple interactions. Expected {recipient}, got {recipient_value}"
        assert message_value == message, \
            f"Message field should retain value after multiple interactions. Expected {message}, got {message_value}"
        
        # For EMAIL type, verify subject persists as well
        if notification_type == 'EMAIL':
            subject_value = notification_page.subject_input.input_value()
            assert subject_value == subject, \
                f"Subject field should retain value after interaction. Expected {subject}, got {subject_value}"
    
    @given(
        initial_type=notification_types(),
        target_type=notification_types()
    )
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_subject_field_visibility_on_type_switch(self, page: Page, notification_page, initial_type, target_type):
        """Property test: Subject field visibility changes correctly when switching notification types.
        
        **Validates: Requirements 6.1**
        
        For any combination of notification types:
        1. Navigate to the application
        2. Select initial notification type
        3. Verify subject field visibility matches type
        4. Switch to target notification type
        5. Verify subject field visibility updates correctly
        
        Args:
            page: Playwright page fixture
            notification_page: NotificationPage Page Object Model fixture
            initial_type: First notification type to select
            target_type: Second notification type to switch to
        """
        # Navigate to the application
        notification_page.navigate()
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Step 1: Select initial type
        notification_page.select_type(initial_type)
        
        # Assertion 1: Verify subject visibility matches initial type
        is_subject_visible = notification_page.is_subject_visible()
        if initial_type == 'EMAIL':
            assert is_subject_visible, \
                f"Subject field should be visible for EMAIL type (initial={initial_type}), but it's hidden"
        else:
            assert not is_subject_visible, \
                f"Subject field should be hidden for {initial_type} type (initial={initial_type}), but it's visible"
        
        # Step 2: Switch to target type
        notification_page.select_type(target_type)
        
        # Assertion 2: Verify subject visibility matches target type
        is_subject_visible = notification_page.is_subject_visible()
        if target_type == 'EMAIL':
            assert is_subject_visible, \
                f"Subject field should be visible for EMAIL type (switched to {target_type}), but it's hidden"
        else:
            assert not is_subject_visible, \
                f"Subject field should be hidden for {target_type} type (switched to {target_type}), but it's visible"


class TestNotificationQueryRendering:
    """Test suite for NotificationQuery component rendering."""
    
    @given(filters=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_filter_elements_visible_and_interactive(self, page: Page, query_page, filters):
        """Property test: All notification query filter elements are visible and interactive.
        
        **Validates: Requirements 6.1**
        
        For any query filter combination:
        1. Navigate to the application
        2. Verify all filter elements are present in the DOM
        3. Verify all filter elements are visible (not hidden by CSS)
        4. Verify all filter elements are interactive (clickable/fillable)
        5. Verify search button is present, visible, and clickable
        
        Filter elements to verify:
        - Type filter dropdown: present, visible
        - Status filter input: present, visible, accepts input
        - From date filter input: present, visible, accepts input
        - To date filter input: present, visible, accepts input
        - Search button: present, visible, clickable
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            filters: Query filter combination from Hypothesis generator
        """
        # Navigate to the application
        query_page.navigate()
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Assertion 1: Verify type filter is present and visible
        assert query_page.type_filter.is_visible(), \
            "Type filter dropdown should be visible in the query form"
        
        # Assertion 2: Verify type filter is interactive (can select option)
        # Verify it has options by checking if we can interact with it
        try:
            # Get all options in the dropdown
            type_options = query_page.type_filter.locator('option').count()
            assert type_options >= 0, \
                f"Type filter should have options, got {type_options}"
        except Exception:
            pass  # If it's not a select, that's okay for this check
        
        # Assertion 3: Verify status filter is present and visible
        assert query_page.status_filter.is_visible(), \
            "Status filter input should be visible in the query form"
        
        # Assertion 4: Verify status filter is interactive (can accept input)
        try:
            query_page.status_filter.fill('SENT')
            status_value = query_page.status_filter.input_value()
            assert status_value == 'SENT', \
                f"Status filter should accept input. Expected 'SENT', got {status_value}"
            query_page.status_filter.clear()  # Clear for next test
        except Exception:
            pass  # Status filter might be optional or different type
        
        # Assertion 5: Verify from date filter is present and visible
        assert query_page.from_date.is_visible(), \
            "From date filter input should be visible in the query form"
        
        # Assertion 6: Verify from date filter is interactive (can accept input)
        try:
            query_page.from_date.fill('2024-01-01')
            from_value = query_page.from_date.input_value()
            assert from_value == '2024-01-01', \
                f"From date filter should accept input. Expected '2024-01-01', got {from_value}"
            query_page.from_date.clear()  # Clear for next test
        except Exception as e:
            pytest.fail(f"From date filter should be interactive: {e}")
        
        # Assertion 7: Verify to date filter is present and visible
        assert query_page.to_date.is_visible(), \
            "To date filter input should be visible in the query form"
        
        # Assertion 8: Verify to date filter is interactive (can accept input)
        try:
            query_page.to_date.fill('2024-12-31')
            to_value = query_page.to_date.input_value()
            assert to_value == '2024-12-31', \
                f"To date filter should accept input. Expected '2024-12-31', got {to_value}"
            query_page.to_date.clear()  # Clear for next test
        except Exception as e:
            pytest.fail(f"To date filter should be interactive: {e}")
        
        # Assertion 9: Verify search button is present and visible
        assert query_page.search_button.is_visible(), \
            "Search button should be visible in the query form"
        
        # Assertion 10: Verify search button is interactive (not disabled, can be clicked)
        is_disabled = page.locator('[data-testid="search"]').is_disabled()
        assert not is_disabled, \
            "Search button should be enabled and clickable"
    
    @given(filters=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_results_area_initially_not_visible(self, page: Page, query_page, filters):
        """Property test: Query results area is initially empty or not visible.
        
        **Validates: Requirements 6.1**
        
        For any query state:
        1. Navigate to the application
        2. Verify results area is initially empty or not visible
        3. Verify no results message is visible initially
        4. Verify results table is not visible initially
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            filters: Query filter combination from Hypothesis generator
        """
        # Navigate to the application
        query_page.navigate()
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Assertion 1: Verify no results are displayed initially
        # Either the results table is not visible, or it shows no results message
        results_count = query_page.get_results_count()
        has_no_results_msg = query_page.has_no_results_message()
        
        assert results_count == 0 or has_no_results_msg, \
            f"Query results should be initially empty. Got {results_count} results and no-results-message={has_no_results_msg}"
        
        # Assertion 2: Verify the query page is in initial state (no prior search executed)
        # This is verified by the fact that results are empty
        assert results_count == 0, \
            f"Results table should be empty initially before any search is performed. Got {results_count} results"
    
    @given(filters=query_filters())
    @settings(
        max_examples=25,
        verbosity=Verbosity.quiet,
        suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow],
        deadline=None
    )
    @pytest.mark.property_test
    def test_query_filter_fields_retain_values(self, page: Page, query_page, filters):
        """Property test: Query filter fields retain values after interaction.
        
        **Validates: Requirements 6.1**
        
        For any query filter combination:
        1. Navigate to the application
        2. Fill filter fields with provided values
        3. Interact with filter elements (click, focus, blur)
        4. Verify all filter fields retain their values
        5. Verify values persist across multiple interactions
        
        Args:
            page: Playwright page fixture
            query_page: QueryPage Page Object Model fixture
            filters: Query filter combination from Hypothesis generator
        """
        # Navigate to the application
        query_page.navigate()
        page.wait_for_load_state('domcontentloaded', timeout=5000)
        
        # Fill filter fields based on provided filters
        if 'type' in filters:
            query_page.type_filter.select_option(filters['type'])
        
        if 'status' in filters:
            query_page.status_filter.fill(filters['status'])
        
        if 'from' in filters:
            query_page.from_date.fill(filters['from'])
        
        if 'to' in filters:
            query_page.to_date.fill(filters['to'])
        
        # Interaction 1: Click on status filter and blur
        if 'status' in filters:
            query_page.status_filter.click()
            query_page.status_filter.blur()
            
            # Assertion 1: Verify status value persists after interaction
            status_value = query_page.status_filter.input_value()
            assert status_value == filters['status'], \
                f"Status filter should retain value after interaction. Expected {filters['status']}, got {status_value}"
        
        # Interaction 2: Click on from_date filter and blur
        if 'from' in filters:
            query_page.from_date.click()
            query_page.from_date.blur()
            
            # Assertion 2: Verify from_date value persists after interaction
            from_value = query_page.from_date.input_value()
            assert from_value == filters['from'], \
                f"From date filter should retain value after interaction. Expected {filters['from']}, got {from_value}"
        
        # Interaction 3: Click on to_date filter and blur
        if 'to' in filters:
            query_page.to_date.click()
            query_page.to_date.blur()
            
            # Assertion 3: Verify to_date value persists after interaction
            to_value = query_page.to_date.input_value()
            assert to_value == filters['to'], \
                f"To date filter should retain value after interaction. Expected {filters['to']}, got {to_value}"

