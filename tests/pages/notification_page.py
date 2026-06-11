"""
Page Object Model for the Notification Form page.

This module provides the NotificationPage class which encapsulates all interactions
with the notification form UI, following the Page Object Model pattern for maintainable
and reusable test automation.
"""

from playwright.sync_api import Page, Locator


class NotificationPage:
    """Page Object Model for the Notification Form.
    
    This class provides methods to interact with the notification form UI,
    including form filling, submission, and status message retrieval.
    
    Attributes:
        page: Playwright Page instance
        type_select: Locator for notification type dropdown
        recipient_input: Locator for recipient input field
        message_input: Locator for message textarea
        subject_input: Locator for subject input field
        submit_button: Locator for submit button
        status_message: Locator for status message display
    """
    
    def __init__(self, page: Page):
        """Initialize the NotificationPage with locators.
        
        Args:
            page: Playwright Page instance
        """
        self.page = page
        self.type_select = page.locator('[data-testid="notification-type"]')
        self.recipient_input = page.locator('[data-testid="recipient"]')
        self.message_input = page.locator('[data-testid="message"]')
        self.subject_input = page.locator('[data-testid="subject"]')
        self.submit_button = page.locator('[data-testid="submit"]')
        self.status_message = page.locator('[data-testid="status-message"]')
    
    def navigate(self) -> None:
        """Navigate to the notification form page.
        
        Loads the application at http://localhost:5173/ (Vite dev server).
        """
        self.page.goto('http://localhost:5173/')
    
    def select_type(self, notification_type: str) -> None:
        """Select a notification type from the dropdown.
        
        Args:
            notification_type: The notification type to select (EMAIL, SMS, or WHATSAPP)
        """
        self.type_select.select_option(notification_type)
    
    def fill_form(
        self,
        notification_type: str,
        recipient: str,
        message: str,
        subject: str = None
    ) -> None:
        """Fill the notification form with provided data.
        
        This method fills all form fields with the provided data. The subject field
        is only filled if provided and the notification type is EMAIL.
        
        Args:
            notification_type: The notification type (EMAIL, SMS, or WHATSAPP)
            recipient: The recipient address or phone number
            message: The notification message content
            subject: Optional email subject (only used for EMAIL type)
        """
        self.select_type(notification_type)
        self.recipient_input.fill(recipient)
        self.message_input.fill(message)
        
        # Only fill subject if provided and type is EMAIL
        if subject and notification_type == 'EMAIL':
            # Wait for subject field to be visible (it may be hidden for non-EMAIL types)
            self.subject_input.wait_for(state='visible', timeout=1000)
            self.subject_input.fill(subject)
    
    def submit(self) -> None:
        """Submit the notification form.
        
        Clicks the submit button to trigger form submission.
        """
        self.submit_button.click()
    
    def get_status_message(self) -> str:
        """Retrieve the status message displayed after form submission.
        
        Returns:
            The text content of the status message, or empty string if not visible
        """
        try:
            # Wait for status message to appear (with timeout)
            self.status_message.wait_for(state='visible', timeout=5000)
            # Give the DOM a brief moment to fully update with content
            self.page.wait_for_timeout(100)
            return self.status_message.text_content() or ''
        except Exception:
            # Return empty string if status message is not visible
            return ''
    
    def is_subject_visible(self) -> bool:
        """Check if the subject field is currently visible.
        
        Returns:
            True if the subject field is visible, False otherwise
        """
        return self.subject_input.is_visible()
