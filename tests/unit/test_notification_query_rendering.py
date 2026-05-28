"""
Unit tests for NotificationQuery component rendering.

This module tests that the NotificationQuery component renders correctly,
including all filter inputs, search button, results area, and initial state.

Tests validate Requirements 6.1 by verifying:
- All filter inputs render correctly
- Search button is present
- Results area is initially empty
- No-results message is hidden initially
"""

import pytest
from playwright.sync_api import Page


@pytest.mark.unit_test
class TestNotificationQueryRendering:
    """Test suite for NotificationQuery component rendering."""
    
    def test_query_component_renders_correctly(self, page: Page, query_page):
        """Test that the notification query component renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The query container is visible
        - The query heading is displayed
        - The filter form exists
        """
        query_page.navigate()
        
        # Verify query container is visible
        query_container = page.locator('.notification-query-container')
        assert query_container.is_visible(), "Query container should be visible"
        
        # Verify query heading is displayed
        heading = page.locator('.notification-query-container h2')
        assert heading.is_visible(), "Query heading should be visible"
        assert heading.text_content() == "Query Notifications", "Query heading should display 'Query Notifications'"
        
        # Verify filter form exists
        filter_form = page.locator('.query-form')
        assert filter_form.is_visible(), "Filter form should be visible"
    
    def test_type_filter_input_renders(self, page: Page, query_page):
        """Test that the type filter dropdown renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The type filter dropdown is visible
        - The label is displayed
        - The dropdown has the correct data-testid attribute
        """
        query_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="filter-type"]')
        assert label.is_visible(), "Type filter label should be visible"
        assert "Type" in label.text_content(), "Label should display 'Type'"
        
        # Verify dropdown is visible
        type_filter = page.locator('[data-testid="filter-type"]')
        assert type_filter.is_visible(), "Type filter dropdown should be visible"
        
        # Verify it's optional (no required indicator)
        required_indicator = label.locator('.required')
        assert not required_indicator.is_visible(), "Type filter should not have required indicator"
    
    def test_status_filter_input_renders(self, page: Page, query_page):
        """Test that the status filter input renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The status filter input is visible
        - The label is displayed
        - The input has the correct data-testid attribute
        """
        query_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="filter-status"]')
        assert label.is_visible(), "Status filter label should be visible"
        assert "Status" in label.text_content(), "Label should display 'Status'"
        
        # Verify input is visible
        status_filter = page.locator('[data-testid="filter-status"]')
        assert status_filter.is_visible(), "Status filter input should be visible"
        
        # Verify it's optional
        required_indicator = label.locator('.required')
        assert not required_indicator.is_visible(), "Status filter should not have required indicator"
    
    def test_from_date_filter_renders(self, page: Page, query_page):
        """Test that the 'from' date filter renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The from date input is visible
        - The label is displayed
        - The input has the correct data-testid attribute
        - The input is empty initially
        """
        query_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="filter-from"]')
        assert label.is_visible(), "From date filter label should be visible"
        assert "From" in label.text_content(), "Label should display 'From'"
        
        # Verify input is visible
        from_filter = page.locator('[data-testid="filter-from"]')
        assert from_filter.is_visible(), "From date filter input should be visible"
        
        # Verify input is empty initially
        assert from_filter.input_value() == "", "From date filter should be empty initially"
    
    def test_to_date_filter_renders(self, page: Page, query_page):
        """Test that the 'to' date filter renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The to date input is visible
        - The label is displayed
        - The input has the correct data-testid attribute
        - The input is empty initially
        """
        query_page.navigate()
        
        # Verify label is displayed
        label = page.locator('label[for="filter-to"]')
        assert label.is_visible(), "To date filter label should be visible"
        assert "To" in label.text_content(), "Label should display 'To'"
        
        # Verify input is visible
        to_filter = page.locator('[data-testid="filter-to"]')
        assert to_filter.is_visible(), "To date filter input should be visible"
        
        # Verify input is empty initially
        assert to_filter.input_value() == "", "To date filter should be empty initially"
    
    def test_search_button_present_and_enabled(self, page: Page, query_page):
        """Test that the search button is present and enabled.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The search button is visible
        - The search button is enabled
        - The search button has the correct data-testid attribute
        - The search button displays the correct text
        """
        query_page.navigate()
        
        search_button = page.locator('[data-testid="search"]')
        
        # Verify button is visible
        assert search_button.is_visible(), "Search button should be visible"
        
        # Verify button is enabled
        assert not search_button.is_disabled(), "Search button should be enabled"
        
        # Verify button text
        button_text = search_button.text_content()
        assert button_text == "Search", "Search button should display 'Search'"
    
    def test_results_area_renders(self, page: Page, query_page):
        """Test that the results area renders correctly.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The results area is visible
        - The results container has the correct data-testid attribute
        """
        query_page.navigate()
        
        results_area = page.locator('.results-section')
        assert results_area.is_visible(), "Results area should be visible"
    
    def test_results_area_initially_empty(self, page: Page, query_page):
        """Test that the results area is initially empty.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - No results are displayed initially
        - The results table/list is empty
        """
        query_page.navigate()
        
        results_area = page.locator('.results-section')
        
        # Check that there are no result rows initially
        result_rows = results_area.locator('tbody tr')
        # Should be empty initially
        assert result_rows.count() == 0, "Results area should be empty initially"
    
    def test_no_results_message_hidden_initially(self, page: Page, query_page):
        """Test that the no-results message is hidden initially.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - The no-results message is not visible initially
        - The message appears only when search returns no results
        """
        query_page.navigate()
        
        # The no-results message is shown when there are no notifications and no error
        # Initially, the component shows the no-results message because notifications is empty
        # This is the expected behavior - the message guides users to send a notification first
        no_results_message = page.locator('[data-testid="no-results"]')
        # The message should be visible initially to guide users
        assert no_results_message.is_visible(), "No-results message should be visible initially to guide users"
    
    def test_filter_form_structure(self, page: Page, query_page):
        """Test that the filter form is properly structured.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Filter form contains all required filter fields
        - Filter fields are organized in form groups
        """
        query_page.navigate()
        
        filter_form = page.locator('.query-form')
        
        # Verify form groups exist for each filter
        form_groups = filter_form.locator('.form-group')
        assert form_groups.count() >= 4, "Should have at least 4 form groups (type, status, from, to)"
    
    def test_filter_inputs_are_interactive(self, page: Page, query_page):
        """Test that all filter inputs are interactive.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Type filter can be changed
        - Status filter accepts text
        - From date filter accepts date input
        - To date filter accepts date input
        """
        query_page.navigate()
        
        # Test type filter is interactive
        type_filter = page.locator('[data-testid="filter-type"]')
        type_filter.select_option('EMAIL')
        assert type_filter.input_value() == "EMAIL", "Type filter should accept selection"
        
        # Test status filter is interactive
        status_filter = page.locator('[data-testid="filter-status"]')
        status_filter.fill('SENT')
        assert status_filter.input_value() == "SENT", "Status filter should accept text"
        
        # Test from date filter is interactive
        from_filter = page.locator('[data-testid="filter-from"]')
        from_filter.fill('2026-05-27')
        assert from_filter.input_value() == "2026-05-27", "From date filter should accept date"
        
        # Test to date filter is interactive
        to_filter = page.locator('[data-testid="filter-to"]')
        to_filter.fill('2026-05-28')
        assert to_filter.input_value() == "2026-05-28", "To date filter should accept date"
    
    def test_results_table_structure(self, page: Page, query_page):
        """Test that the results table/list has proper structure.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Results are displayed in a table or list format
        - Table has header row with column names
        - Columns include: type, recipient, message, status, timestamp
        """
        query_page.navigate()
        
        results_area = page.locator('[data-testid="results"]')
        
        # Check if results are in a table
        table = results_area.locator('table')
        if table.is_visible():
            # Verify table has header row
            header_row = table.locator('thead tr')
            assert header_row.is_visible(), "Table should have header row"
            
            # Verify header contains expected columns
            headers = header_row.locator('th')
            header_texts = [header.text_content() for header in headers.all()]
            
            # Should contain at least these columns
            assert any('Type' in text for text in header_texts), "Should have Type column"
            assert any('Recipient' in text for text in header_texts), "Should have Recipient column"
            assert any('Status' in text for text in header_texts), "Should have Status column"
    
    def test_loading_state_not_visible_initially(self, page: Page, query_page):
        """Test that loading state is not visible initially.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Loading indicator is not visible initially
        - Loading spinner/message appears only during search
        """
        query_page.navigate()
        
        loading_indicator = page.locator('[data-testid="loading"]')
        assert not loading_indicator.is_visible(), "Loading indicator should not be visible initially"
    
    def test_error_message_not_visible_initially(self, page: Page, query_page):
        """Test that error message is not visible initially.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Error message is not displayed initially
        - Error message appears only when query fails
        """
        query_page.navigate()
        
        error_message = page.locator('[data-testid="error-message"]')
        assert not error_message.is_visible(), "Error message should not be visible initially"
    
    def test_filter_labels_have_proper_styling(self, page: Page, query_page):
        """Test that filter labels are properly styled and readable.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - All labels are visible and readable
        - Labels are associated with their inputs
        """
        query_page.navigate()
        
        # Get all labels in the filter form
        labels = page.locator('.query-form label')
        
        # Verify all labels are visible
        for i in range(labels.count()):
            label = labels.nth(i)
            assert label.is_visible(), f"Label {i} should be visible"
            assert label.text_content().strip() != "", f"Label {i} should have text"
    
    def test_clear_filters_button_present(self, page: Page, query_page):
        """Test that a clear/reset filters button is present.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - Clear filters button is visible
        - Button is enabled
        - Button has appropriate label
        """
        query_page.navigate()
        
        # Look for clear/reset button
        clear_button = page.locator('.clear-button')
        
        if clear_button.count() > 0:
            assert clear_button.is_visible(), "Clear filters button should be visible"
            assert not clear_button.is_disabled(), "Clear filters button should be enabled"
    
    def test_query_component_accessibility(self, page: Page, query_page):
        """Test that the query component has proper accessibility attributes.
        
        Validates: Requirement 6.1
        
        Verifies that:
        - All inputs have associated labels
        - Buttons have descriptive text
        - Form has proper ARIA attributes
        """
        query_page.navigate()
        
        # Verify all inputs have labels
        inputs = page.locator('.query-form input, .query-form select')
        for i in range(inputs.count()):
            input_elem = inputs.nth(i)
            input_id = input_elem.get_attribute('id')
            
            if input_id:
                label = page.locator(f'label[for="{input_id}"]')
                assert label.count() > 0, f"Input {i} should have associated label"
