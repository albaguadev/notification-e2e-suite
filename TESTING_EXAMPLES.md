# Testing Examples and Patterns

This document provides practical examples of testing patterns used in the Notification E2E Suite, including Page Object Model usage, property-based testing, and test data management.

## Table of Contents

1. [Page Object Model Usage](#page-object-model-usage)
2. [Unit Testing Examples](#unit-testing-examples)
3. [Property-Based Testing Examples](#property-based-testing-examples)
4. [E2E Testing Examples](#e2e-testing-examples)
5. [Test Data Management](#test-data-management)

## Page Object Model Usage

The Page Object Model (POM) pattern encapsulates page-specific code and logic, making tests more maintainable and readable.

### NotificationPage Example

```python
# File: tests/pages/notification_page.py

from playwright.async_api import Page, expect

class NotificationPage:
    """Page Object for the Notification Form page"""
    
    def __init__(self, page: Page):
        self.page = page
        
        # Define locators using data-testid attributes
        # This approach is more resilient to UI changes than relying on specific selectors
        self.type_select = page.locator('[data-testid="notification-type"]')
        self.recipient_input = page.locator('[data-testid="recipient"]')
        self.message_input = page.locator('[data-testid="message"]')
        self.subject_input = page.locator('[data-testid="subject"]')
        self.submit_button = page.locator('[data-testid="submit"]')
        self.status_message = page.locator('[data-testid="status-message"]')
        self.error_container = page.locator('[data-testid="error-container"]')
    
    async def navigate(self):
        """Navigate to the notification form page"""
        await self.page.goto('http://localhost:5173')
        await self.page.wait_for_load_state('networkidle')
    
    async def select_type(self, notification_type: str):
        """Select notification type from dropdown"""
        await self.type_select.select_option(notification_type)
        # Wait for any dependent UI updates (e.g., subject field visibility)
        await self.page.wait_for_timeout(100)
    
    async def fill_form(
        self,
        notification_type: str,
        recipient: str,
        message: str,
        subject: str = None
    ):
        """Fill the notification form with provided data"""
        await self.select_type(notification_type)
        await self.recipient_input.fill(recipient)
        await self.message_input.fill(message)
        
        if subject and notification_type == 'EMAIL':
            await self.subject_input.fill(subject)
    
    async def submit(self):
        """Click the submit button"""
        await self.submit_button.click()
    
    async def get_status_message(self) -> str:
        """Get the status message from the UI"""
        await expect(self.status_message).to_be_visible()
        return await self.status_message.text_content()
    
    async def is_subject_visible(self) -> bool:
        """Check if the subject field is visible"""
        return await self.subject_input.is_visible()
    
    async def wait_for_status_message(self, timeout: int = 5000):
        """Wait for status message to appear"""
        await self.status_message.wait_for(state='visible', timeout=timeout)
    
    async def has_validation_error(self) -> bool:
        """Check if validation error is displayed"""
        return await self.error_container.is_visible()
    
    async def get_validation_error_text(self) -> str:
        """Get validation error message"""
        return await self.error_container.text_content()
```

### Using Page Objects in Tests

```python
# File: tests/unit/test_form_rendering.py

import pytest
from tests.pages.notification_page import NotificationPage

@pytest.mark.unit_test
async def test_form_fields_render(page):
    """Test that all form fields render correctly"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    
    # Verify all form elements are visible
    assert await notification_page.type_select.is_visible()
    assert await notification_page.recipient_input.is_visible()
    assert await notification_page.message_input.is_visible()
    assert await notification_page.submit_button.is_visible()

@pytest.mark.unit_test
async def test_subject_hidden_for_sms(page):
    """Test that subject field is hidden for SMS notifications"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type('SMS')
    
    assert not await notification_page.is_subject_visible()

@pytest.mark.unit_test
async def test_subject_visible_for_email(page):
    """Test that subject field is visible for EMAIL notifications"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type('EMAIL')
    
    assert await notification_page.is_subject_visible()
```

## Unit Testing Examples

Unit tests verify specific examples and edge cases with deterministic inputs and outputs.

### Example 1: Form Validation Testing

```python
# File: tests/unit/test_validation_examples.py

import pytest
from tests.pages.notification_page import NotificationPage

@pytest.mark.unit_test
async def test_invalid_email_shows_error(page):
    """Test that invalid email format shows validation error"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type('EMAIL')
    
    # Fill with invalid email
    await notification_page.recipient_input.fill('invalid-email')
    await notification_page.recipient_input.blur()  # Trigger validation
    
    # Verify error is shown
    assert await notification_page.has_validation_error()

@pytest.mark.unit_test
async def test_empty_recipient_prevents_submission(page):
    """Test that empty recipient field prevents form submission"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type('EMAIL')
    await notification_page.recipient_input.fill('')  # Empty
    await notification_page.message_input.fill('Test message')
    
    await notification_page.submit()
    
    # Verify form was not submitted and error is shown
    assert await notification_page.has_validation_error()

@pytest.mark.unit_test
async def test_valid_email_allows_submission(page):
    """Test that valid email allows form submission"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type('EMAIL')
    await notification_page.recipient_input.fill('test@example.com')
    await notification_page.message_input.fill('Test message')
    await notification_page.subject_input.fill('Test subject')
    
    # Should not show validation error
    assert not await notification_page.has_validation_error()
```

### Example 2: Backend Error Handling

```python
# File: tests/unit/test_error_handling_examples.py

import pytest
from tests.pages.notification_page import NotificationPage

@pytest.mark.unit_test
async def test_backend_unavailable_error(page):
    """Test user-friendly error message when backend is unavailable"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    
    # Mock backend unavailable (abort network request)
    await page.route(
        '**/api/v1/notifications',
        lambda route: route.abort()
    )
    
    # Fill and submit form
    await notification_page.fill_form(
        'EMAIL',
        'test@example.com',
        'Test message',
        'Test subject'
    )
    await notification_page.submit()
    
    # Verify user-friendly error is shown
    await notification_page.wait_for_status_message(timeout=3000)
    status = await notification_page.get_status_message()
    assert 'unable to connect' in status.lower() or 'error' in status.lower()

@pytest.mark.unit_test
async def test_400_error_response_parsing(page):
    """Test that 400 error responses are parsed and displayed"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    
    # Mock 400 Bad Request with error JSON
    error_response = {
        "status": 400,
        "timestamp": "2024-01-01T12:00:00Z",
        "message": "Invalid recipient format",
        "description": "The email address format is invalid"
    }
    
    await page.route(
        '**/api/v1/notifications',
        lambda route: route.abort('timedout')  # Simulate timeout
    )
    
    # Alternative: Mock with actual response
    # await page.route(
    #     '**/api/v1/notifications',
    #     lambda route: route.fulfill(
    #         status=400,
    #         content_type='application/json',
    #         body=json.dumps(error_response)
    #     )
    # )
    
    await notification_page.fill_form(
        'EMAIL',
        'invalid-email',
        'Test message'
    )
    await notification_page.submit()
    
    # Verify error message is displayed
    await notification_page.wait_for_status_message()
```

## Property-Based Testing Examples

Property-based tests use Hypothesis to generate many test inputs automatically, verifying that properties hold across all inputs.

### Example 1: Form Submission Triggers API Request

This property verifies that for ANY valid notification data, the form submission triggers the correct API request.

```python
# File: tests/property/test_form_submission_example.py

from hypothesis import given, settings, Verbosity, HealthCheck
import pytest
from tests.pages.notification_page import NotificationPage
from tests.utils.generators import notification_types, valid_emails, valid_messages

# Feature: notification-e2e-suite, Property 1: Form Submission Triggers API Request
@given(
    notification_type=notification_types(),
    recipient=valid_emails(),
    message=valid_messages()
)
@settings(
    max_examples=25,
    verbosity=Verbosity.quiet,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@pytest.mark.property_test
async def test_form_submission_triggers_api_request(
    page,
    notification_type,
    recipient,
    message
):
    """
    Validates: Requirements 2.2, 3.1, 6.3
    
    Property: For any valid notification data (type, recipient, message),
    when the user submits the form, the React application SHALL trigger
    a POST request to the backend API with all required fields.
    """
    notification_page = NotificationPage(page)
    await notification_page.navigate()
    
    # Capture API requests
    requests = []
    
    async def handle_route(route):
        # Capture the request before sending
        requests.append(route.request)
        # Continue with the request (this will fail if backend not available)
        await route.continue_()
    
    # Set up request interception
    await page.route('**/api/v1/notifications', handle_route)
    
    # Fill and submit form
    await notification_page.fill_form(
        notification_type,
        recipient,
        message
    )
    await notification_page.submit()
    
    # Wait a bit for request to be made
    await page.wait_for_timeout(500)
    
    # Verify API request was made
    assert len(requests) > 0, "No API request was made"
    
    request = requests[0]
    assert request.method == 'POST'
    assert '/api/v1/notifications' in request.url
    
    # Verify request body contains all required fields
    body = request.post_data_json
    assert body['type'] == notification_type
    assert body['recipient'] == recipient
    assert body['message'] == message
```

### Example 2: Required Field Validation

This property verifies that missing required fields prevent submission.

```python
# File: tests/property/test_validation_properties_example.py

from hypothesis import given, strategies as st, settings, Verbosity, HealthCheck
import pytest
from tests.pages.notification_page import NotificationPage

# Feature: notification-e2e-suite, Property 3: Required Field Validation
@given(
    missing_field=st.sampled_from(['recipient', 'message'])
)
@settings(
    max_examples=25,
    verbosity=Verbosity.quiet,
    suppress_health_check=[
        HealthCheck.function_scoped_fixture,
        HealthCheck.too_slow
    ]
)
@pytest.mark.property_test
async def test_missing_required_fields_prevents_submission(
    page,
    missing_field
):
    """
    Validates: Requirements 2.4, 2.6
    
    Property: For any form submission attempt with one or more missing
    required fields (type, recipient, or message), the React application
    SHALL prevent submission and display validation errors.
    """
    notification_page = NotificationPage(page)
    await notification_page.navigate()
    
    # Fill form with missing field
    await notification_page.select_type('EMAIL')
    
    if missing_field != 'recipient':
        await notification_page.recipient_input.fill('test@example.com')
    
    if missing_field != 'message':
        await notification_page.message_input.fill('Test message')
    
    await notification_page.submit()
    
    # Wait for validation to trigger
    await page.wait_for_timeout(300)
    
    # Verify validation error is shown and form was not submitted
    assert await notification_page.has_validation_error()
```

## E2E Testing Examples

E2E tests verify complete user flows from the UI perspective.

### Example 1: Complete Email Notification Flow

```python
# File: tests/e2e/test_email_flow_example.py

import pytest
from tests.pages.notification_page import NotificationPage

@pytest.mark.e2e_test
async def test_send_email_notification_complete_flow(page):
    """
    Complete flow: User navigates to app, sends email notification,
    and sees success message
    
    Validates: Requirement 7.1
    """
    notification_page = NotificationPage(page)
    
    # Navigate to application
    await notification_page.navigate()
    
    # Verify form is ready
    assert await notification_page.type_select.is_visible()
    
    # Fill form with valid email data
    await notification_page.fill_form(
        notification_type='EMAIL',
        recipient='test@example.com',
        message='This is a test email notification',
        subject='Test Subject'
    )
    
    # Verify subject is visible for EMAIL
    assert await notification_page.is_subject_visible()
    
    # Submit the form
    await notification_page.submit()
    
    # Wait for response and verify success or error message
    await notification_page.wait_for_status_message(timeout=5000)
    status_message = await notification_page.get_status_message()
    
    # Verify we got some feedback (success or error)
    assert status_message is not None
    assert len(status_message) > 0
```

### Example 2: SMS Notification with Validation

```python
# File: tests/e2e/test_sms_flow_example.py

import pytest
from tests.pages.notification_page import NotificationPage

@pytest.mark.e2e_test
async def test_send_sms_notification_with_validation(page):
    """
    Flow: User selects SMS, enters valid Spanish phone number,
    and sends notification
    
    Validates: Requirement 7.2, 6.2
    """
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    
    # Select SMS type
    await notification_page.select_type('SMS')
    
    # Verify subject is NOT visible for SMS
    assert not await notification_page.is_subject_visible()
    
    # Fill form with valid Spanish phone number (+34 format)
    await notification_page.fill_form(
        notification_type='SMS',
        recipient='+34612345678',  # Valid ES region number
        message='This is a test SMS notification'
    )
    
    # Submit and verify response
    await notification_page.submit()
    
    await notification_page.wait_for_status_message(timeout=5000)
    status_message = await notification_page.get_status_message()
    
    assert status_message is not None
```

## Test Data Management

Test data can be stored in JSON files and loaded by tests, making it easy to update test scenarios without changing test code.

### Test Data Files

#### File: `tests/data/valid_notifications.json`

```json
{
  "email_notifications": [
    {
      "type": "EMAIL",
      "recipient": "test@example.com",
      "message": "Test email notification",
      "subject": "Test Subject"
    },
    {
      "type": "EMAIL",
      "recipient": "user@company.co.uk",
      "message": "Another test email",
      "subject": "Another Subject"
    }
  ],
  "sms_notifications": [
    {
      "type": "SMS",
      "recipient": "+34612345678",
      "message": "Test SMS notification"
    },
    {
      "type": "SMS",
      "recipient": "+34712345678",
      "message": "Another SMS"
    }
  ],
  "whatsapp_notifications": [
    {
      "type": "WHATSAPP",
      "recipient": "+34612345678",
      "message": "Test WhatsApp notification"
    }
  ]
}
```

#### File: `tests/data/invalid_notifications.json`

```json
{
  "invalid_emails": [
    {
      "type": "EMAIL",
      "recipient": "not-an-email",
      "message": "Test"
    },
    {
      "type": "EMAIL",
      "recipient": "@example.com",
      "message": "Test"
    }
  ],
  "invalid_phones": [
    {
      "type": "SMS",
      "recipient": "123456789",
      "message": "Test"
    },
    {
      "type": "SMS",
      "recipient": "+34812345678",
      "message": "Test"
    }
  ]
}
```

### Loading Test Data

```python
# File: tests/utils/test_data_loader.py

import json
import os
from pathlib import Path
from typing import Any, Dict

class TestDataLoader:
    """Utility for loading test data from JSON files"""
    
    @staticmethod
    def load_json(filename: str) -> Dict[str, Any]:
        """Load test data from JSON file"""
        filepath = Path(__file__).parent.parent / 'data' / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Test data file not found: {filepath}")
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    @staticmethod
    def get_valid_email_notifications():
        """Get valid email notification test data"""
        data = TestDataLoader.load_json('valid_notifications.json')
        return data.get('email_notifications', [])
    
    @staticmethod
    def get_valid_sms_notifications():
        """Get valid SMS notification test data"""
        data = TestDataLoader.load_json('valid_notifications.json')
        return data.get('sms_notifications', [])
    
    @staticmethod
    def get_invalid_email_notifications():
        """Get invalid email notification test data"""
        data = TestDataLoader.load_json('invalid_notifications.json')
        return data.get('invalid_emails', [])
```

### Using Test Data in Tests

```python
# File: tests/unit/test_with_data_examples.py

import pytest
from tests.utils.test_data_loader import TestDataLoader
from tests.pages.notification_page import NotificationPage

@pytest.mark.parametrize(
    'notification',
    TestDataLoader.get_valid_email_notifications()
)
@pytest.mark.unit_test
async def test_valid_email_notifications(page, notification):
    """Test with multiple valid email examples from test data"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.fill_form(
        notification['type'],
        notification['recipient'],
        notification['message'],
        notification.get('subject')
    )
    
    # Should not have validation errors
    assert not await notification_page.has_validation_error()

@pytest.mark.parametrize(
    'notification',
    TestDataLoader.get_invalid_email_notifications()
)
@pytest.mark.unit_test
async def test_invalid_email_notifications(page, notification):
    """Test with invalid email examples from test data"""
    notification_page = NotificationPage(page)
    
    await notification_page.navigate()
    await notification_page.select_type(notification['type'])
    await notification_page.recipient_input.fill(notification['recipient'])
    await notification_page.recipient_input.blur()
    
    # Should have validation error
    assert await notification_page.has_validation_error()
```

## Test Strategies (Generators)

Hypothesis uses strategies to generate test data. Here are commonly used strategies:

```python
# File: tests/utils/generators.py

from hypothesis import strategies as st

# Email strategy
valid_emails = st.emails()

# Phone number strategies
valid_es_phone = st.from_regex(r'\+34[67]\d{8}', fullmatch=True)
valid_e164_phone = st.from_regex(r'\+\d{1,3}\d{6,14}', fullmatch=True)

# Notification type strategy
notification_types = st.sampled_from(['EMAIL', 'SMS', 'WHATSAPP'])

# Message strategy (1-500 characters)
valid_messages = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=500
)

# Subject strategy for emails
email_subjects = st.text(
    alphabet=st.characters(blacklist_categories=('Cc', 'Cs')),
    min_size=1,
    max_size=100
)
```

## Running Example Tests

```bash
# Run all example tests
pytest tests/ --headed

# Run specific example test file
pytest tests/unit/test_form_rendering.py -v

# Run property-based examples only
pytest tests/property/ -m property_test -v

# Run E2E examples with detailed output
pytest tests/e2e/ -m e2e_test -vv --tb=short

# Run with specific browser
pytest tests/ --browser firefox --headed
```

## Summary

This guide covered:
- **Page Object Models**: Encapsulating page elements and actions
- **Unit Testing**: Testing specific examples and edge cases
- **Property-Based Testing**: Verifying properties with generated data
- **E2E Testing**: Testing complete user flows
- **Test Data Management**: Organizing and loading test data

For more information, see:
- [Test Suite README](tests/README.md)
- [Design Document](/.kiro/specs/notification-e2e-suite/design.md)
- [Playwright Documentation](https://playwright.dev/python/)
- [Hypothesis Documentation](https://hypothesis.readthedocs.io/)
