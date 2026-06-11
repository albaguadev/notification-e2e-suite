"""
Hypothesis strategies for property-based testing.

This module provides test data generators using Hypothesis for creating
randomized test data across property-based tests.

Requirements: 9.4
- Strategy for valid email addresses
- Strategy for valid ES region phone numbers
- Strategy for valid E.164 phone numbers
- Strategy for notification types (EMAIL, SMS, WHATSAPP)
- Strategy for message content (1-500 characters)
- Strategy for error responses with various status codes
"""

from hypothesis import strategies as st
from typing import Dict, Any


# ============================================================================
# NOTIFICATION TYPE STRATEGIES
# ============================================================================

@st.composite
def notification_types(draw) -> str:
    """Generate a valid notification type.
    
    Returns one of: EMAIL, SMS, WHATSAPP
    
    Returns:
        str: One of the valid notification types
        
    Requirement: 9.4 - Implement strategy for notification types (EMAIL, SMS, WHATSAPP)
    """
    return draw(st.sampled_from(['EMAIL', 'SMS', 'WHATSAPP']))


# ============================================================================
# EMAIL ADDRESS STRATEGIES
# ============================================================================

@st.composite
def valid_emails(draw) -> str:
    """Generate a valid RFC 5322 compliant email address.
    
    Format: local-part@domain.tld
    - Local part: alphanumeric + . % + - _
    - Domain: alphanumeric + . -
    - TLD: 2+ letters
    
    Returns:
        str: A valid email address
        
    Requirement: 9.4 - Implement strategy for valid email addresses
    """
    # Local part: 1-20 characters, alphanumeric with some special chars
    local_part = draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._',
            min_size=1,
            max_size=20
        ).filter(lambda x: x[0] not in '._%+-' and x[-1] not in '._%+-')
    )
    
    # Domain name: 2-20 characters per part
    domain_parts = draw(
        st.lists(
            st.text(
                alphabet='abcdefghijklmnopqrstuvwxyz0123456789',
                min_size=1,
                max_size=10
            ),
            min_size=1,
            max_size=3
        )
    )
    
    # TLD: 2-6 letters
    tld = draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz',
            min_size=2,
            max_size=6
        )
    )
    
    domain = '.'.join(domain_parts) + '.' + tld
    
    return f"{local_part}@{domain}"


@st.composite
def invalid_emails(draw) -> str:
    """Generate an invalid email address.
    
    Common invalid formats:
    - Missing @
    - Multiple @
    - No domain
    - No local part
    - Spaces in address
    
    Returns:
        str: An invalid email address
        
    Requirement: 9.4 (implicit - for validation testing)
    """
    invalid_type = draw(st.integers(min_value=0, max_value=4))
    
    if invalid_type == 0:
        # No @ symbol
        return draw(st.emails()).replace('@', '')
    elif invalid_type == 1:
        # Multiple @ symbols
        email = draw(st.emails())
        return email.replace('@', '@@')
    elif invalid_type == 2:
        # No local part
        return '@example.com'
    elif invalid_type == 3:
        # No domain
        return 'user@'
    else:
        # Spaces in address
        return 'user name@example.com'


# ============================================================================
# SMS PHONE NUMBER STRATEGIES (ES REGION)
# ============================================================================

@st.composite
def valid_sms_numbers(draw) -> str:
    """Generate a valid ES region SMS phone number.
    
    Format: +34 followed by 9 digits starting with 6 or 7
    Examples:
    - +34612345678
    - +34712345678
    
    Returns:
        str: A valid Spanish SMS phone number
        
    Requirement: 9.4 - Implement strategy for valid ES region phone numbers
    """
    prefix = draw(st.sampled_from(['6', '7']))
    remaining_digits = draw(
        st.text(
            alphabet='0123456789',
            min_size=8,
            max_size=8
        )
    )
    
    return f"+34{prefix}{remaining_digits}"


@st.composite
def invalid_sms_numbers(draw) -> str:
    """Generate an invalid SMS phone number.
    
    Common invalid formats:
    - Missing +34 prefix
    - Wrong country code
    - Starting with 8 or 9 (not 6 or 7)
    - Wrong length
    - Contains letters or special characters
    
    Returns:
        str: An invalid SMS phone number
        
    Requirement: 9.4 (implicit - for validation testing)
    """
    invalid_type = draw(st.integers(min_value=0, max_value=4))
    
    if invalid_type == 0:
        # Missing + prefix
        return '34612345678'
    elif invalid_type == 1:
        # Wrong country code
        return '+33612345678'  # French
    elif invalid_type == 2:
        # Starting with 8 (invalid for ES mobile)
        return '+34812345678'
    elif invalid_type == 3:
        # Wrong length (too short)
        return '+3461234567'
    else:
        # Contains letters
        return '+34612345ABC'


# ============================================================================
# WHATSAPP PHONE NUMBER STRATEGIES (E.164 FORMAT)
# ============================================================================

@st.composite
def valid_whatsapp_numbers(draw) -> str:
    """Generate a valid E.164 format WhatsApp phone number.
    
    Format: + followed by 7-15 digits
    Examples:
    - +34612345678 (Spain)
    - +12025551234 (USA)
    - +442071838750 (UK)
    
    Returns:
        str: A valid E.164 format phone number
        
    Requirement: 9.4 - Implement strategy for valid E.164 phone numbers
    """
    # Generate 7-15 total digits
    total_digits = draw(st.integers(min_value=7, max_value=15))
    
    # Split between country code (1-3 digits) and number part
    country_code_len = draw(st.integers(min_value=1, max_value=min(3, total_digits - 4)))
    number_part_len = total_digits - country_code_len
    
    # Country code: 1-3 digits
    country_code = draw(
        st.text(
            alphabet='0123456789',
            min_size=country_code_len,
            max_size=country_code_len
        )
    )
    
    # Number part: remaining digits
    number_part = draw(
        st.text(
            alphabet='0123456789',
            min_size=number_part_len,
            max_size=number_part_len
        )
    )
    
    return f"+{country_code}{number_part}"


@st.composite
def invalid_whatsapp_numbers(draw) -> str:
    """Generate an invalid E.164 format WhatsApp phone number.
    
    Common invalid formats:
    - Missing + prefix
    - Too short (< 7 digits)
    - Too long (> 15 digits)
    - Contains letters or special characters
    - Spaces in number
    
    Returns:
        str: An invalid E.164 format phone number
        
    Requirement: 9.4 (implicit - for validation testing)
    """
    invalid_type = draw(st.integers(min_value=0, max_value=4))
    
    if invalid_type == 0:
        # Missing + prefix
        return '34612345678'
    elif invalid_type == 1:
        # Too short
        return '+346'
    elif invalid_type == 2:
        # Too long
        return '+346123456789012345'
    elif invalid_type == 3:
        # Contains letters
        return '+34612345ABC'
    else:
        # Spaces in number
        return '+34 612 345 678'


# ============================================================================
# MESSAGE CONTENT STRATEGIES
# ============================================================================

@st.composite
def valid_messages(draw) -> str:
    """Generate valid message content.
    
    Constraint: 1-500 characters
    Content: Printable ASCII + common punctuation
    
    Returns:
        str: Valid message content
        
    Requirement: 9.4 - Implement strategy for message content (1-500 characters)
    """
    return draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:\'"()-',
            min_size=1,
            max_size=500
        )
    )


@st.composite
def short_messages(draw) -> str:
    """Generate short message content (1-50 characters).
    
    Returns:
        str: Short message content
    """
    return draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?',
            min_size=1,
            max_size=50
        )
    )


@st.composite
def long_messages(draw) -> str:
    """Generate long message content (100-500 characters).
    
    Returns:
        str: Long message content
    """
    return draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:\'"()-\n',
            min_size=100,
            max_size=500
        )
    )


@st.composite
def empty_or_whitespace_messages(draw) -> str:
    """Generate empty or whitespace-only message content.
    
    Returns:
        str: Empty or whitespace message
    """
    whitespace_type = draw(st.integers(min_value=0, max_value=2))
    
    if whitespace_type == 0:
        return ''
    elif whitespace_type == 1:
        return '   '
    else:
        return '\t\n  '


# ============================================================================
# SUBJECT LINE STRATEGIES
# ============================================================================

@st.composite
def valid_subjects(draw) -> str:
    """Generate valid email subject line.
    
    Constraint: 1-200 characters
    Content: Printable ASCII
    
    Returns:
        str: Valid subject line
    """
    return draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,!?;:\'"-',
            min_size=1,
            max_size=200
        )
    )


@st.composite
def optional_subjects(draw) -> str:
    """Generate optional subject line (may be empty).
    
    Returns:
        str: Optional subject line (may be empty)
    """
    is_empty = draw(st.booleans())
    
    if is_empty:
        return ''
    else:
        return draw(valid_subjects())


# ============================================================================
# ERROR RESPONSE STRATEGIES
# ============================================================================

@st.composite
def error_status_codes(draw) -> int:
    """Generate a valid HTTP error status code.
    
    Valid error codes for this API: 400, 404, 500, 503
    
    Returns:
        int: An HTTP error status code
        
    Requirement: 9.4 - Implement strategy for error responses with various status codes
    """
    return draw(st.sampled_from([400, 404, 500, 503]))


@st.composite
def error_responses(draw) -> Dict[str, Any]:
    """Generate a valid error response object.
    
    Structure:
    {
        "status": <int>,
        "timestamp": <ISO 8601 datetime>,
        "message": <str>,
        "description": <str>
    }
    
    Returns:
        Dict: A valid error response object
        
    Requirement: 9.4 - Implement strategy for error responses with various status codes
    """
    status = draw(error_status_codes())
    message = draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz ',
            min_size=5,
            max_size=50
        )
    )
    description = draw(
        st.text(
            alphabet='abcdefghijklmnopqrstuvwxyz0123456789 .,',
            min_size=10,
            max_size=100
        )
    )
    
    return {
        'status': status,
        'timestamp': '2024-01-01T00:00:00Z',
        'message': message,
        'description': description
    }


@st.composite
def malformed_error_responses(draw) -> Dict[str, Any]:
    """Generate a malformed error response.
    
    Missing required fields or incomplete structure
    
    Returns:
        Dict: A malformed error response object
    """
    response_type = draw(st.integers(min_value=0, max_value=3))
    
    if response_type == 0:
        # Missing description
        return {
            'status': 400,
            'timestamp': '2024-01-01T00:00:00Z',
            'message': 'Error'
        }
    elif response_type == 1:
        # Missing message
        return {
            'status': 400,
            'timestamp': '2024-01-01T00:00:00Z',
            'description': 'Something went wrong'
        }
    elif response_type == 2:
        # Only status
        return {'status': 400}
    else:
        # Empty object
        return {}


# ============================================================================
# COMPOSITE NOTIFICATION DATA STRATEGIES
# ============================================================================

@st.composite
def valid_notifications(draw, notification_type=None) -> Dict[str, str]:
    """Generate a valid notification request.
    
    Args:
        notification_type: If specified, use this type; otherwise generate one
        
    Returns:
        Dict: A valid notification request object
        
    Requirement: 9.4 (composite of other strategies)
    """
    notif_type = notification_type or draw(notification_types())
    
    if notif_type == 'EMAIL':
        return {
            'type': notif_type,
            'recipient': draw(valid_emails()),
            'message': draw(valid_messages()),
            'subject': draw(valid_subjects())
        }
    elif notif_type == 'SMS':
        return {
            'type': notif_type,
            'recipient': draw(valid_sms_numbers()),
            'message': draw(valid_messages())
        }
    else:  # WHATSAPP
        return {
            'type': notif_type,
            'recipient': draw(valid_whatsapp_numbers()),
            'message': draw(valid_messages())
        }


@st.composite
def invalid_notifications(draw) -> Dict[str, str]:
    """Generate an invalid notification request.
    
    At least one field is invalid
    
    Returns:
        Dict: An invalid notification request object
    """
    notif_type = draw(notification_types())
    invalid_field = draw(st.integers(min_value=0, max_value=2))
    
    if notif_type == 'EMAIL':
        if invalid_field == 0:
            # Invalid email
            recipient = draw(invalid_emails())
        else:
            recipient = draw(valid_emails())
            
        return {
            'type': notif_type,
            'recipient': recipient,
            'message': draw(valid_messages() if invalid_field != 1 else empty_or_whitespace_messages())
        }
    else:
        # SMS or WHATSAPP
        if notif_type == 'SMS':
            valid_recipient = draw(valid_sms_numbers() if invalid_field != 0 else invalid_sms_numbers())
        else:
            valid_recipient = draw(valid_whatsapp_numbers() if invalid_field != 0 else invalid_whatsapp_numbers())
            
        return {
            'type': notif_type,
            'recipient': valid_recipient,
            'message': draw(valid_messages() if invalid_field != 1 else empty_or_whitespace_messages())
        }
