"""
Unit tests for test data loading and validation utilities.

Tests verify that the helpers module correctly:
- Loads test data from JSON files
- Validates data structure
- Provides clear error messages for invalid data
- Handles file I/O errors gracefully
"""

import json
import pytest
import tempfile
from pathlib import Path

from tests.utils.helpers import (
    load_json_file,
    load_valid_notifications,
    load_invalid_notifications,
    load_error_responses,
    load_test_data_by_type,
    get_error_response_by_status,
    get_malformed_error_responses,
    validate_notification_data,
    validate_error_response_data,
    get_data_file_path,
    TestDataError,
    TestDataFileError,
    TestDataParsingError,
    TestDataValidationError,
)


class TestDataFileLoading:
    """Tests for file loading functionality."""
    
    def test_load_valid_notifications_succeeds(self):
        """Test that valid_notifications.json loads successfully."""
        data = load_valid_notifications()
        assert isinstance(data, dict)
        assert "email_notifications" in data
        assert "sms_notifications" in data
        assert "whatsapp_notifications" in data
    
    def test_load_invalid_notifications_succeeds(self):
        """Test that invalid_notifications.json loads successfully."""
        data = load_invalid_notifications()
        assert isinstance(data, dict)
        assert "invalid_emails" in data
        assert "invalid_sms_numbers" in data
        assert "invalid_whatsapp_numbers" in data
    
    def test_load_error_responses_succeeds(self):
        """Test that error_responses.json loads successfully."""
        data = load_error_responses()
        assert isinstance(data, dict)
        assert "400_bad_request_errors" in data
        assert "404_not_found_errors" in data
        assert "500_internal_server_error" in data
        assert "503_service_unavailable" in data
        assert "malformed_error_responses" in data
    
    def test_load_nonexistent_file_raises_error(self):
        """Test that loading a nonexistent file raises TestDataFileError."""
        with pytest.raises(TestDataFileError) as exc_info:
            load_json_file("nonexistent_file.json")
        
        assert "not found" in str(exc_info.value).lower()
        assert "tests/data/" in str(exc_info.value)
    
    def test_malformed_json_raises_parsing_error(self):
        """Test that malformed JSON raises TestDataParsingError."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a temporary invalid JSON file
            test_file = Path(tmpdir) / "invalid.json"
            test_file.write_text("{invalid json content")
            
            # Mock get_data_file_path to return our temp file
            import tests.utils.helpers as helpers_module
            original_get_path = helpers_module.get_data_file_path
            
            def mock_get_path(filename):
                if filename == "invalid.json":
                    return test_file
                return original_get_path(filename)
            
            helpers_module.get_data_file_path = mock_get_path
            
            try:
                with pytest.raises(TestDataParsingError) as exc_info:
                    load_json_file("invalid.json")
                
                assert "invalid json" in str(exc_info.value).lower()
            finally:
                helpers_module.get_data_file_path = original_get_path


class TestNotificationDataValidation:
    """Tests for notification data validation."""
    
    def test_valid_email_notification_passes_validation(self):
        """Test that valid email notification passes validation."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": "Test message",
            "subject": "Test subject"
        }
        # Should not raise
        validate_notification_data(data)
    
    def test_valid_sms_notification_passes_validation(self):
        """Test that valid SMS notification passes validation."""
        data = {
            "type": "SMS",
            "recipient": "+34612345678",
            "message": "Test message"
        }
        # Should not raise
        validate_notification_data(data)
    
    def test_valid_whatsapp_notification_passes_validation(self):
        """Test that valid WhatsApp notification passes validation."""
        data = {
            "type": "WHATSAPP",
            "recipient": "+34612345678",
            "message": "Test message"
        }
        # Should not raise
        validate_notification_data(data)
    
    def test_missing_required_field_raises_error(self):
        """Test that missing required field raises validation error."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com"
            # Missing 'message'
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_notification_data(data)
        
        assert "message" in str(exc_info.value).lower()
        assert "missing required" in str(exc_info.value).lower()
    
    def test_empty_recipient_raises_error(self):
        """Test that empty recipient raises validation error."""
        data = {
            "type": "EMAIL",
            "recipient": "",
            "message": "Test message"
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_notification_data(data)
        
        assert "recipient" in str(exc_info.value).lower()
        assert "empty" in str(exc_info.value).lower()
    
    def test_empty_message_raises_error(self):
        """Test that empty message raises validation error."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": ""
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_notification_data(data)
        
        assert "message" in str(exc_info.value).lower()
        assert "empty" in str(exc_info.value).lower()
    
    def test_invalid_notification_type_raises_error(self):
        """Test that invalid notification type raises validation error."""
        data = {
            "type": "TELEGRAM",
            "recipient": "user@telegram",
            "message": "Test message"
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_notification_data(data)
        
        assert "telegram" in str(exc_info.value).lower()
        assert "valid types" in str(exc_info.value).lower()
    
    def test_wrong_field_type_raises_error(self):
        """Test that wrong field type raises validation error."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": 12345  # Should be string
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_notification_data(data)
        
        assert "message" in str(exc_info.value).lower()
        assert "expected string" in str(exc_info.value).lower()
    
    def test_optional_subject_field_allowed(self):
        """Test that subject field is optional."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": "Test message"
            # No subject field
        }
        # Should not raise
        validate_notification_data(data)
    
    def test_additional_fields_allowed(self):
        """Test that additional fields don't cause validation to fail."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": "Test message",
            "extra_field": "extra_value",
            "another_field": 123
        }
        # Should not raise - additional fields are allowed
        validate_notification_data(data)


class TestErrorResponseDataValidation:
    """Tests for error response data validation."""
    
    def test_valid_error_response_passes_validation(self):
        """Test that valid error response passes validation."""
        data = {
            "status": 400,
            "response_status": 400,
            "timestamp": "2024-01-15T10:30:00Z",
            "message": "Bad Request",
            "description": "Invalid data provided"
        }
        # Should not raise
        validate_error_response_data(data)
    
    def test_partial_error_response_allowed(self):
        """Test that partial error response (for malformed cases) is allowed."""
        data = {
            "status": 500,
            "message": "Server Error"
            # Missing other fields
        }
        # Should not raise
        validate_error_response_data(data)
    
    def test_invalid_status_code_raises_error(self):
        """Test that invalid HTTP status code raises validation error."""
        data = {
            "status": 999,  # Invalid status code
            "message": "Error"
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_error_response_data(data)
        
        assert "status code" in str(exc_info.value).lower()
    
    def test_wrong_status_type_raises_error(self):
        """Test that non-integer status raises validation error."""
        data = {
            "status": "400",  # Should be int
            "message": "Error"
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_error_response_data(data)
        
        assert "status" in str(exc_info.value).lower()
        assert "expected int" in str(exc_info.value).lower()
    
    def test_wrong_message_type_raises_error(self):
        """Test that non-string message raises validation error."""
        data = {
            "status": 400,
            "message": 123  # Should be string
        }
        
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_error_response_data(data)
        
        assert "message" in str(exc_info.value).lower()
        assert "expected string" in str(exc_info.value).lower()
    
    def test_non_dict_error_response_raises_error(self):
        """Test that non-dict error response raises validation error."""
        with pytest.raises(TestDataValidationError) as exc_info:
            validate_error_response_data("invalid response")
        
        assert "dictionary" in str(exc_info.value).lower()


class TestLoadTestDataByType:
    """Tests for loading test data by notification type."""
    
    def test_load_email_notifications(self):
        """Test loading EMAIL notification test data."""
        data = load_test_data_by_type("EMAIL")
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(item["type"] == "EMAIL" for item in data)
    
    def test_load_sms_notifications(self):
        """Test loading SMS notification test data."""
        data = load_test_data_by_type("SMS")
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(item["type"] == "SMS" for item in data)
    
    def test_load_whatsapp_notifications(self):
        """Test loading WHATSAPP notification test data."""
        data = load_test_data_by_type("WHATSAPP")
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(item["type"] == "WHATSAPP" for item in data)
    
    def test_invalid_notification_type_raises_error(self):
        """Test that invalid notification type raises validation error."""
        with pytest.raises(TestDataValidationError) as exc_info:
            load_test_data_by_type("INVALID")
        
        assert "invalid" in str(exc_info.value).lower()
        assert "notification type" in str(exc_info.value).lower()


class TestErrorResponsesByStatus:
    """Tests for loading error responses by status code."""
    
    def test_load_400_error_responses(self):
        """Test loading 400 Bad Request error responses."""
        data = get_error_response_by_status(400)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_load_404_error_responses(self):
        """Test loading 404 Not Found error responses."""
        data = get_error_response_by_status(404)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_load_500_error_responses(self):
        """Test loading 500 Internal Server Error responses."""
        data = get_error_response_by_status(500)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_load_503_error_responses(self):
        """Test loading 503 Service Unavailable responses."""
        data = get_error_response_by_status(503)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_unsupported_status_code_raises_error(self):
        """Test that unsupported status code raises validation error."""
        with pytest.raises(TestDataValidationError) as exc_info:
            get_error_response_by_status(201)
        
        assert "unsupported" in str(exc_info.value).lower()
        assert "status code" in str(exc_info.value).lower()


class TestMalformedErrorResponses:
    """Tests for loading malformed error response test data."""
    
    def test_get_malformed_error_responses(self):
        """Test loading malformed error response test data."""
        data = get_malformed_error_responses()
        assert isinstance(data, list)
        assert len(data) > 0
        # Malformed responses can be dicts or strings
        assert any(isinstance(item, (dict, str)) for item in data)


class TestErrorMessages:
    """Tests to verify error messages are clear and informative."""
    
    def test_missing_field_error_message_is_clear(self):
        """Test that missing field error message is clear and helpful."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com"
            # Missing 'message'
        }
        
        try:
            validate_notification_data(data)
            pytest.fail("Expected TestDataValidationError")
        except TestDataValidationError as e:
            error_msg = str(e)
            # Error message should be clear about what's missing and what's required
            assert "message" in error_msg.lower()
            assert "required field" in error_msg.lower()
            assert "recipient" in error_msg  # Show what fields were provided
    
    def test_file_not_found_error_message_is_clear(self):
        """Test that file not found error message shows expected location."""
        try:
            load_json_file("nonexistent.json")
            pytest.fail("Expected TestDataFileError")
        except TestDataFileError as e:
            error_msg = str(e)
            # Error message should indicate the file wasn't found
            assert "not found" in error_msg.lower() or "cannot" in error_msg.lower()
            # Should show where it was expected
            assert "tests/data/" in error_msg or "test" in error_msg.lower()
    
    def test_validation_error_shows_actual_value(self):
        """Test that validation error shows the problematic value."""
        data = {
            "type": "EMAIL",
            "recipient": "test@example.com",
            "message": 12345  # Wrong type
        }
        
        try:
            validate_notification_data(data)
            pytest.fail("Expected TestDataValidationError")
        except TestDataValidationError as e:
            error_msg = str(e)
            # Error should show the problematic value
            assert "12345" in error_msg or "int" in error_msg
    
    def test_error_message_includes_context(self):
        """Test that error messages include enough context for debugging."""
        # Test with multiple missing fields
        data = {
            "type": "EMAIL"
            # Missing 'recipient' and 'message'
        }
        
        try:
            validate_notification_data(data)
            pytest.fail("Expected TestDataValidationError")
        except TestDataValidationError as e:
            error_msg = str(e)
            # Error should indicate which fields are required
            assert "required" in error_msg.lower()
            # Should suggest valid options
            assert "recipient" in error_msg or "message" in error_msg


class TestDataIntegrity:
    """Tests to verify loaded test data maintains integrity."""
    
    def test_valid_notifications_are_all_valid(self):
        """Test that all loaded valid notifications pass validation."""
        data = load_valid_notifications()
        
        for category, notifications in data.items():
            for idx, notification in enumerate(notifications):
                try:
                    validate_notification_data(notification)
                except TestDataValidationError as e:
                    pytest.fail(
                        f"Valid notification in category '{category}' at index {idx} failed validation: {e}"
                    )
    
    def test_error_responses_maintain_structure(self):
        """Test that error responses maintain proper structure."""
        data = load_error_responses()
        
        for status_code in [400, 404, 500, 503]:
            responses = get_error_response_by_status(status_code)
            assert len(responses) > 0, f"No error responses for status {status_code}"
    
    def test_loaded_data_is_not_empty(self):
        """Test that all loaded data files contain actual test data."""
        valid = load_valid_notifications()
        invalid = load_invalid_notifications()
        errors = load_error_responses()
        
        # Check that we have meaningful amounts of test data
        assert sum(len(v) for v in valid.values()) > 0
        assert sum(len(v) for v in invalid.values()) > 0
        assert sum(len(v) for v in errors.values()) > 0
