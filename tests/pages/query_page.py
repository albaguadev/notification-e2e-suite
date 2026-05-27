"""
Page Object Model for the Notification Query page.

This module provides the QueryPage class which encapsulates all interactions
with the notification query UI, following the Page Object Model pattern for maintainable
and reusable test automation.
"""

from playwright.sync_api import Page, Locator


class QueryPage:
    """Page Object Model for the Notification Query interface.
    
    This class provides methods to interact with the notification query UI,
    including filter application, search execution, and results retrieval.
    
    Attributes:
        page: Playwright Page instance
        type_filter: Locator for notification type filter dropdown
        status_filter: Locator for status filter input
        from_date: Locator for from date filter input
        to_date: Locator for to date filter input
        search_button: Locator for search button
        results_table: Locator for results table
        no_results_message: Locator for no results message
    """
    
    def __init__(self, page: Page):
        """Initialize the QueryPage with locators.
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.type_filter = page.locator('[data-testid="filter-type"]')
        self.status_filter = page.locator('[data-testid="filter-status"]')
        self.from_date = page.locator('[data-testid="filter-from"]')
        self.to_date = page.locator('[data-testid="filter-to"]')
        self.search_button = page.locator('[data-testid="search"]')
        self.results_table = page.locator('[data-testid="results"]')
        self.no_results_message = page.locator('[data-testid="no-results"]')
    
    def navigate(self) -> None:
        """Navigate to the notification query page.
        
        Loads the application at http://localhost:5173/ (Vite dev server).
        """
        self.page.goto('http://localhost:5173/')
    
    def apply_filters(
        self,
        notification_type: str = None,
        status: str = None,
        from_date: str = None,
        to_date: str = None
    ) -> None:
        """Apply filters to the notification query.
        
        This method fills the filter form with the provided values. All parameters
        are optional, allowing for flexible filter combinations.
        
        Args:
            notification_type: Optional notification type filter (EMAIL, SMS, or WHATSAPP)
            status: Optional status filter (e.g., SENT, FAILED)
            from_date: Optional from date filter in YYYY-MM-DD format
            to_date: Optional to date filter in YYYY-MM-DD format
        """
        if notification_type is not None:
            self.type_filter.select_option(notification_type)
        
        if status is not None:
            self.status_filter.fill(status)
        
        if from_date is not None:
            self.from_date.fill(from_date)
        
        if to_date is not None:
            self.to_date.fill(to_date)
    
    def search(self) -> None:
        """Trigger the search operation.
        
        Clicks the search button to execute the query with applied filters.
        """
        self.search_button.click()
    
    def get_results_count(self) -> int:
        """Count the number of displayed notification results.
        
        Returns:
            The number of notification rows in the results table, or 0 if table is not visible
        """
        try:
            # Wait for results table to be visible (with timeout)
            self.results_table.wait_for(state='visible', timeout=5000)
            # Count tbody rows (excluding header)
            return self.results_table.locator('tbody tr').count()
        except Exception:
            # Return 0 if results table is not visible
            return 0
    
    def has_no_results_message(self) -> bool:
        """Check if the no results message is displayed.
        
        Returns:
            True if the no results message is visible, False otherwise
        """
        return self.no_results_message.is_visible()
