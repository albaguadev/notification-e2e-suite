/**
 * API Client Module for MultiChannelNotifier Backend
 * 
 * This module provides centralized API communication functions for the frontend application.
 * All backend API requests should go through this module.
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.3
 */

const API_BASE_URL = 'http://localhost:8081/api/v1'

/**
 * Notification request data structure
 */
export interface NotificationRequest {
  type: 'EMAIL' | 'SMS' | 'WHATSAPP'
  recipient: string
  message: string
  subject?: string // Only for EMAIL type
}

/**
 * Error response structure from backend
 */
export interface ErrorResponse {
  status: number
  timestamp: string
  message: string
  description: string
}

/**
 * API response wrapper
 */
export interface APIResponse<T> {
  success: boolean
  data?: T
  error?: ErrorResponse | string
}

/**
 * Query filters for notification history
 */
export interface QueryFilters {
  type?: 'EMAIL' | 'SMS' | 'WHATSAPP'
  status?: string
  from?: string // ISO date string
  to?: string // ISO date string
}

/**
 * Notification response data
 */
export interface NotificationData {
  id?: string
  type: string
  recipient: string
  message: string
  subject?: string
  status: string
  timestamp: string
}

/**
 * Parse and validate error response from backend
 * 
 * Requirements: 3.4, 3.5, 3.6
 * - Validates error response structure (status, timestamp, message, description)
 * - Verifies response_status field matches HTTP status code
 * - Implements silent failure for malformed JSON or missing fields
 * 
 * @param response - The fetch Response object
 * @param httpStatus - The HTTP status code
 * @returns ErrorResponse object or null if validation fails
 */
async function handleAPIError(
  response: Response,
  httpStatus: number
): Promise<ErrorResponse | null> {
  try {
    const errorData = await response.json()

    // Validate error response structure - all fields must be present
    if (
      !errorData.status ||
      !errorData.timestamp ||
      !errorData.message ||
      !errorData.description
    ) {
      // Missing fields - fail silently (Requirement 3.6)
      return null
    }

    // Verify response_status field matches HTTP status code (Requirement 3.5)
    if (errorData.status !== httpStatus) {
      // Status mismatch - fail silently (Requirement 3.6)
      return null
    }

    return errorData as ErrorResponse
  } catch (error) {
    // Malformed JSON - fail silently (Requirement 3.6)
    return null
  }
}

/**
 * Send a notification through the backend API
 * 
 * Requirements: 3.1, 3.2, 3.7
 * - Implements POST request to http://localhost:8081/api/v1/notifications
 * - Adds proper headers (Content-Type: application/json)
 * - Ensures no authentication headers are included
 * - Handles request body formatting with type, recipient, message, and optional subject
 * - Returns structured response object with success, data, and error fields
 * 
 * @param notificationData - The notification data to send
 * @returns APIResponse with success status and data or error
 */
export async function sendNotification(
  notificationData: NotificationRequest
): Promise<APIResponse<NotificationData>> {
  try {
    const response = await fetch(`${API_BASE_URL}/notifications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // No authentication headers (Requirement 3.7)
      },
      body: JSON.stringify(notificationData),
    })

    const data = await response.json()

    if (response.ok) {
      // Check if 200 response contains error information (Requirement 7.4)
      if (data.status && data.message && data.description) {
        return {
          success: false,
          error: data as ErrorResponse,
        }
      }

      return {
        success: true,
        data: data as NotificationData,
      }
    } else {
      // Handle error responses (400, 404, 500, 503)
      const errorResponse = await handleAPIError(response, response.status)

      if (errorResponse) {
        return {
          success: false,
          error: errorResponse,
        }
      } else {
        // Malformed error response - fail silently (Requirement 3.6)
        return {
          success: false,
          error: undefined,
        }
      }
    }
  } catch (error) {
    // Network error - backend unavailable (Requirement 3.3)
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }
}

/**
 * Query notification history with optional filters
 * 
 * Requirements: 4.1, 4.3
 * - Implements GET request to http://localhost:8081/api/v1/notifications
 * - Adds query parameter formatting for filters (type, status, from, to)
 * - Handles response parsing and error handling
 * - Returns structured response with notifications array
 * 
 * @param filters - Optional query filters
 * @returns APIResponse with success status and notifications array or error
 */
export async function queryNotifications(
  filters?: QueryFilters
): Promise<APIResponse<NotificationData[]>> {
  try {
    // Build query parameters
    const queryParams = new URLSearchParams()

    if (filters) {
      if (filters.type) {
        queryParams.append('type', filters.type)
      }
      if (filters.status) {
        queryParams.append('status', filters.status)
      }
      if (filters.from) {
        queryParams.append('from', filters.from)
      }
      if (filters.to) {
        queryParams.append('to', filters.to)
      }
    }

    const queryString = queryParams.toString()
    const url = queryString
      ? `${API_BASE_URL}/notifications?${queryString}`
      : `${API_BASE_URL}/notifications`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // No authentication headers (Requirement 3.7)
      },
    })

    const data = await response.json()

    if (response.ok) {
      // Check if 200 response contains error information
      if (data.status && data.message && data.description) {
        return {
          success: false,
          error: data as ErrorResponse,
        }
      }

      // Assume data is an array of notifications
      return {
        success: true,
        data: Array.isArray(data) ? data : [],
      }
    } else {
      // Handle error responses
      const errorResponse = await handleAPIError(response, response.status)

      if (errorResponse) {
        return {
          success: false,
          error: errorResponse,
        }
      } else {
        // Malformed error response - fail silently
        return {
          success: false,
          error: undefined,
        }
      }
    }
  } catch (error) {
    // Network error - backend unavailable
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }
}
