"""
Test data loading and validation utilities.

This module provides helper functions to load test data from JSON files,
validate the data structure, and handle errors with clear, informative messages.

Features:
- Load test data from JSON files in the tests/data/ directory
- Validate notification data structure (type, recipient, message, subject)
- Validate error response data structure
- Organize test data by type (EMAIL, SMS, WHATSAPP)
- Organize error responses by HTTP status code
- Clear, informative error messages for debugging

Usage Examples:

    # Load all valid notifications
    from tests.utils.helpers import load_valid_notifications
    data = load_valid_notifications()
    # Returns: {'email_notifications': [...], 'sms_notifications': [...], ...}
    
    # Load notifications for a specific type
    from tests.utils.helpers import load_test_data_by_type
    email_data = load_test_data_by_type("EMAIL")
    # Returns: [{'type': 'EMAIL', 'recipient': '...', ...}, ...]
    
    # Load error responses for a specific status code
    from tests.utils.helpers import get_error_response_by_status
    bad_request_errors = get_error_response_by_status(400)
    # Returns: [{'status': 400, 'message': '...', ...}, ...]
    
    # Load invalid notifications for testing validation
    from tests.utils.helpers import load_invalid_notifications
    invalid_data = load_invalid_notifications()
    # Returns: {'invalid_emails': [...], 'invalid_sms_numbers': [...], ...}
    
    # Validate notification data
    from tests.utils.helpers import validate_notification_data, DataValidationError
    try:
        validate_notification_data({'type': 'EMAIL', 'recipient': 'test@example.com', ...})
    except DataValidationError as e:
        print(f"Validation failed: {e}")

Exception Types:
- DataError: Base exception for all test data errors
- DataFileError: File I/O errors (file not found, permission denied, etc.)
- DataParsingError: JSON parsing errors (malformed JSON)
- DataValidationError: Data structure validation errors

Note: For backwards compatibility, aliases are provided:
- TestDataError -> DataError
- TestDataFileError -> DataFileError
- TestDataParsingError -> DataParsingError
- TestDataValidationError -> DataValidationError
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class DataError(Exception):
    """Base exception for test data loading and validation errors."""
    __test__ = False  # Tell pytest this is not a test class


class DataFileError(DataError):
    """Exception raised when file I/O operations fail."""
    __test__ = False


class DataParsingError(DataError):
    """Exception raised when JSON parsing fails."""
    __test__ = False


class DataValidationError(DataError):
    """Exception raised when test data validation fails."""
    __test__ = False


# Backwards compatibility aliases
TestDataError = DataError
TestDataFileError = DataFileError
TestDataParsingError = DataParsingError
TestDataValidationError = DataValidationError


def get_data_file_path(filename: str) -> Path:
    """
    Get the absolute path to a test data file.
    
    Args:
        filename: Name of the test data file (e.g., 'valid_notifications.json')
        
    Returns:
        Path object pointing to the data file
        
    Raises:
        DataFileError: If the file cannot be located
    """
    # Determine the base directory for test data (tests/data/)
    current_dir = Path(__file__).parent.parent
    data_dir = current_dir / "data"
    file_path = data_dir / filename
    
    if not file_path.exists():
        raise DataFileError(
            f"Test data file not found: {filename}\n"
            f"Expected location: {file_path}\n"
            f"Please ensure the file exists in the tests/data/ directory."
        )
    
    return file_path


def load_json_file(filename: str) -> Dict[str, Any]:
    """
    Load a JSON file from the test data directory.
    
    Args:
        filename: Name of the JSON file to load (e.g., 'valid_notifications.json')
        
    Returns:
        Dictionary containing the parsed JSON data
        
    Raises:
        TestDataFileError: If file cannot be read or doesn't exist
        TestDataParsingError: If JSON parsing fails
    """
    try:
        file_path = get_data_file_path(filename)
    except DataFileError:
        raise
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError as e:
        raise DataFileError(
            f"Failed to read test data file: {filename}\n"
            f"File exists but cannot be accessed: {e}\n"
            f"Check file permissions and ensure the file is readable."
        )
    except PermissionError as e:
        raise DataFileError(
            f"Permission denied reading test data file: {filename}\n"
            f"Error: {e}\n"
            f"Please check file permissions."
        )
    except json.JSONDecodeError as e:
        raise DataParsingError(
            f"Invalid JSON format in {filename}\n"
            f"Error at line {e.lineno}, column {e.colno}: {e.msg}\n"
            f"Please ensure the file contains valid JSON."
        )
    except Exception as e:
        raise DataFileError(
            f"Unexpected error reading {filename}: {type(e).__name__}\n"
            f"Error: {e}"
        )


def validate_notification_data(data: Dict[str, Any]) -> None:
    """
    Validate that a notification data object has the correct structure.
    
    Args:
        data: Dictionary containing notification data
        
    Raises:
        TestDataValidationError: If data structure is invalid
    """
    required_fields = {"type", "recipient", "message"}
    optional_fields = {"subject"}
    
    # Check for missing required fields
    missing_fields = required_fields - set(data.keys())
    if missing_fields:
        raise DataValidationError(
            f"Missing required field(s) in notification data: {', '.join(sorted(missing_fields))}\n"
            f"Required fields: {', '.join(sorted(required_fields))}\n"
            f"Data provided: {list(data.keys())}"
        )
    
    # Check for unknown fields
    allowed_fields = required_fields | optional_fields | {"error", "expected_status"}
    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        # Log warning but don't fail - allow additional fields for flexibility
        pass
    
    # Validate field types and values
    if not isinstance(data["type"], str):
        raise DataValidationError(
            f"Invalid 'type' field: expected string, got {type(data['type']).__name__}\n"
            f"Value: {data['type']}"
        )
    
    if not isinstance(data["recipient"], str):
        raise DataValidationError(
            f"Invalid 'recipient' field: expected string, got {type(data['recipient']).__name__}\n"
            f"Value: {data['recipient']}"
        )
    
    if not isinstance(data["message"], str):
        raise DataValidationError(
            f"Invalid 'message' field: expected string, got {type(data['message']).__name__}\n"
            f"Value: {data['message']}"
        )
    
    # Validate notification type
    valid_types = {"EMAIL", "SMS", "WHATSAPP"}
    if data["type"] not in valid_types:
        raise DataValidationError(
            f"Invalid notification type: '{data['type']}'\n"
            f"Valid types are: {', '.join(sorted(valid_types))}"
        )
    
    # Validate empty strings
    if not data["recipient"]:
        raise DataValidationError(
            f"'recipient' field cannot be empty"
        )
    
    if not data["message"]:
        raise DataValidationError(
            f"'message' field cannot be empty"
        )
    
    # Validate optional subject field
    if "subject" in data:
        if not isinstance(data["subject"], str):
            raise DataValidationError(
                f"Invalid 'subject' field: expected string, got {type(data['subject']).__name__}\n"
                f"Value: {data['subject']}"
            )
        # Note: empty subjects are allowed (optional field can be empty string)


def validate_error_response_data(data: Dict[str, Any]) -> None:
    """
    Validate that an error response data object has the correct structure.
    
    Args:
        data: Dictionary containing error response data
        
    Raises:
        TestDataValidationError: If data structure is invalid
    """
    # For malformed error responses, allow partial structures
    if not isinstance(data, dict):
        raise DataValidationError(
            f"Error response must be a dictionary, got {type(data).__name__}\n"
            f"Value: {data}"
        )
    
    # If it has any of the required fields, validate them
    if "status" in data:
        if not isinstance(data["status"], int):
            raise DataValidationError(
                f"Invalid 'status' field: expected int, got {type(data['status']).__name__}\n"
                f"Value: {data['status']}"
            )
        
        if data["status"] < 100 or data["status"] >= 600:
            raise DataValidationError(
                f"Invalid HTTP status code: {data['status']}\n"
                f"Status codes must be between 100 and 599"
            )
    
    if "response_status" in data:
        if not isinstance(data["response_status"], int):
            raise DataValidationError(
                f"Invalid 'response_status' field: expected int, got {type(data['response_status']).__name__}\n"
                f"Value: {data['response_status']}"
            )
    
    if "message" in data:
        if not isinstance(data["message"], str):
            raise DataValidationError(
                f"Invalid 'message' field: expected string, got {type(data['message']).__name__}\n"
                f"Value: {data['message']}"
            )
    
    if "description" in data:
        if not isinstance(data["description"], str):
            raise DataValidationError(
                f"Invalid 'description' field: expected string, got {type(data['description']).__name__}\n"
                f"Value: {data['description']}"
            )
    
    if "timestamp" in data:
        if not isinstance(data["timestamp"], str):
            raise DataValidationError(
                f"Invalid 'timestamp' field: expected string, got {type(data['timestamp']).__name__}\n"
                f"Value: {data['timestamp']}"
            )


def load_valid_notifications() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load valid notification test data from valid_notifications.json.
    
    Returns:
        Dictionary containing lists of valid notifications organized by type
        (email_notifications, sms_notifications, whatsapp_notifications)
        
    Raises:
        TestDataFileError: If file cannot be read
        TestDataParsingError: If JSON is invalid
        TestDataValidationError: If data structure is invalid
    """
    data = load_json_file("valid_notifications.json")
    
    # Validate top-level structure
    expected_keys = {"email_notifications", "sms_notifications", "whatsapp_notifications"}
    provided_keys = set(data.keys())
    
    if not provided_keys >= expected_keys:
        raise DataValidationError(
            f"Missing expected top-level keys in valid_notifications.json\n"
            f"Expected keys: {', '.join(sorted(expected_keys))}\n"
            f"Provided keys: {', '.join(sorted(provided_keys))}"
        )
    
    # Validate each notification type group
    for key in expected_keys:
        if not isinstance(data[key], list):
            raise DataValidationError(
                f"Invalid structure for '{key}': expected list, got {type(data[key]).__name__}"
            )
        
        for idx, notification in enumerate(data[key]):
            if not isinstance(notification, dict):
                raise DataValidationError(
                    f"Invalid notification in '{key}' at index {idx}: expected dict, got {type(notification).__name__}\n"
                    f"Value: {notification}"
                )
            
            try:
                validate_notification_data(notification)
            except DataValidationError as e:
                raise DataValidationError(
                    f"Validation failed for notification in '{key}' at index {idx}:\n{e}"
                )
    
    return data


def load_invalid_notifications() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load invalid notification test data from invalid_notifications.json.
    
    Returns:
        Dictionary containing lists of invalid notifications organized by error type
        (invalid_emails, invalid_sms_numbers, invalid_whatsapp_numbers, etc.)
        
    Raises:
        TestDataFileError: If file cannot be read
        TestDataParsingError: If JSON is invalid
        TestDataValidationError: If data structure is invalid
    """
    data = load_json_file("invalid_notifications.json")
    
    # Validate top-level structure
    expected_keys = {
        "invalid_emails", "invalid_sms_numbers", "invalid_whatsapp_numbers",
        "missing_required_fields", "invalid_message_content", "invalid_notification_types"
    }
    provided_keys = set(data.keys())
    
    if not provided_keys >= expected_keys:
        raise DataValidationError(
            f"Missing expected top-level keys in invalid_notifications.json\n"
            f"Expected keys: {', '.join(sorted(expected_keys))}\n"
            f"Provided keys: {', '.join(sorted(provided_keys))}"
        )
    
    # Validate each category
    for key in expected_keys:
        if not isinstance(data[key], list):
            raise DataValidationError(
                f"Invalid structure for '{key}': expected list, got {type(data[key]).__name__}"
            )
        
        for idx, item in enumerate(data[key]):
            if not isinstance(item, dict):
                raise DataValidationError(
                    f"Invalid item in '{key}' at index {idx}: expected dict, got {type(item).__name__}\n"
                    f"Value: {item}"
                )
            
            # Note: invalid notifications may have partial structure, so we don't validate strictly
            # Just ensure they are dicts
    
    return data


def load_error_responses() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load error response test data from error_responses.json.
    
    Returns:
        Dictionary containing lists of error responses organized by status code
        (400_bad_request_errors, 404_not_found_errors, 500_internal_server_error,
        503_service_unavailable, malformed_error_responses)
        
    Raises:
        TestDataFileError: If file cannot be read
        TestDataParsingError: If JSON is invalid
        TestDataValidationError: If data structure is invalid
    """
    data = load_json_file("error_responses.json")
    
    # Validate top-level structure
    expected_keys = {
        "400_bad_request_errors", "404_not_found_errors", "500_internal_server_error",
        "503_service_unavailable", "malformed_error_responses"
    }
    provided_keys = set(data.keys())
    
    if not provided_keys >= expected_keys:
        raise DataValidationError(
            f"Missing expected top-level keys in error_responses.json\n"
            f"Expected keys: {', '.join(sorted(expected_keys))}\n"
            f"Provided keys: {', '.join(sorted(provided_keys))}"
        )
    
    # Validate each category
    for key in expected_keys:
        if not isinstance(data[key], list):
            raise DataValidationError(
                f"Invalid structure for '{key}': expected list, got {type(data[key]).__name__}"
            )
        
        for idx, item in enumerate(data[key]):
            if not isinstance(item, (dict, str)):
                raise DataValidationError(
                    f"Invalid item in '{key}' at index {idx}: expected dict or string, got {type(item).__name__}\n"
                    f"Value: {item}"
                )
            
            # Validate error response structure if it's a dict
            if isinstance(item, dict):
                try:
                    validate_error_response_data(item)
                except DataValidationError as e:
                    raise DataValidationError(
                        f"Validation failed for error response in '{key}' at index {idx}:\n{e}"
                    )
    
    return data


def load_test_data_by_type(notification_type: str) -> List[Dict[str, Any]]:
    """
    Load valid notification test data for a specific notification type.
    
    Args:
        notification_type: One of 'EMAIL', 'SMS', or 'WHATSAPP'
        
    Returns:
        List of valid notifications for the specified type
        
    Raises:
        TestDataValidationError: If notification type is invalid or data cannot be loaded
    """
    valid_types = {"EMAIL", "SMS", "WHATSAPP"}
    if notification_type not in valid_types:
        raise DataValidationError(
            f"Invalid notification type: '{notification_type}'\n"
            f"Valid types are: {', '.join(sorted(valid_types))}"
        )
    
    try:
        data = load_valid_notifications()
    except (TestDataFileError, TestDataParsingError) as e:
        raise DataValidationError(
            f"Failed to load valid notifications for type '{notification_type}':\n{e}"
        )
    
    type_key_map = {
        "EMAIL": "email_notifications",
        "SMS": "sms_notifications",
        "WHATSAPP": "whatsapp_notifications"
    }
    
    key = type_key_map[notification_type]
    if key not in data:
        raise DataValidationError(
            f"No test data found for notification type: {notification_type}"
        )
    
    return data[key]


def get_error_response_by_status(status_code: int) -> List[Dict[str, Any]]:
    """
    Get error response test data for a specific HTTP status code.
    
    Args:
        status_code: HTTP status code (400, 404, 500, or 503)
        
    Returns:
        List of error responses for the specified status code
        
    Raises:
        TestDataValidationError: If status code is not supported or data cannot be loaded
    """
    status_key_map = {
        400: "400_bad_request_errors",
        404: "404_not_found_errors",
        500: "500_internal_server_error",
        503: "503_service_unavailable"
    }
    
    if status_code not in status_key_map:
        raise DataValidationError(
            f"Unsupported HTTP status code: {status_code}\n"
            f"Supported codes: {', '.join(str(code) for code in sorted(status_key_map.keys()))}"
        )
    
    try:
        data = load_error_responses()
    except (TestDataFileError, TestDataParsingError) as e:
        raise DataValidationError(
            f"Failed to load error responses for status code {status_code}:\n{e}"
        )
    
    key = status_key_map[status_code]
    if key not in data:
        raise DataValidationError(
            f"No test data found for HTTP status code: {status_code}"
        )
    
    return data[key]


def get_malformed_error_responses() -> List[Union[Dict[str, Any], str]]:
    """
    Get malformed error response test data.
    
    Returns:
        List of malformed error responses (may be dicts or strings)
        
    Raises:
        TestDataValidationError: If data cannot be loaded
    """
    try:
        data = load_error_responses()
    except (TestDataFileError, TestDataParsingError) as e:
        raise DataValidationError(
            f"Failed to load malformed error responses:\n{e}"
        )
    
    if "malformed_error_responses" not in data:
        raise DataValidationError(
            "No 'malformed_error_responses' key found in error_responses.json"
        )
    
    return data["malformed_error_responses"]
