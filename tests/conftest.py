"""
Pytest configuration and fixtures for the Notification E2E Test Suite.

This module provides shared fixtures for test isolation, page object models,
and test data management.
"""

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function")
def test_data():
    """Fixture providing test data for notification tests."""
    return {
        'valid_email': {
            'type': 'EMAIL',
            'recipient': 'test@example.com',
            'message': 'Test message',
            'subject': 'Test subject'
        },
        'valid_sms': {
            'type': 'SMS',
            'recipient': '+34612345678',
            'message': 'Test SMS'
        },
        'valid_whatsapp': {
            'type': 'WHATSAPP',
            'recipient': '+34612345678',
            'message': 'Test WhatsApp'
        }
    }


@pytest.fixture(scope="function", autouse=True)
def cleanup(page: Page):
    """Cleanup fixture that runs after each test.
    
    Fails silently if cleanup operations fail to prevent test suite interruption.
    """
    yield
    # Cleanup logic here (if needed)
    # Fails silently if cleanup operations fail
    try:
        # Future cleanup operations can be added here
        pass
    except Exception:
        # Silent failure as per requirement 11.5
        pass
