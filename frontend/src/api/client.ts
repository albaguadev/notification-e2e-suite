/**
 * API Client Module for MultiChannelNotifier Backend
 * 
 * This module provides centralized API communication functions for the frontend application.
 * All backend API requests should go through this module.
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 4.1, 4.3
 */

const API_BASE_URL = '/api/v1'

/**
 * Date/Time Constants for Query Filters
 * 
 * These constants define the time boundaries for date range queries.
 * They ensure that when a user selects a date range, the query includes
 * the complete day(s) selected, not just a single moment in time.
 */

/**
 * START_OF_DAY_HOURS = 0
 * Represents the beginning of a day (00:00:00)
 * Used for the 'from' parameter to include all notifications from the start of the selected day
 * Example: If user selects 2026-05-27, we query from 2026-05-27T00:00:00Z
 */
const START_OF_DAY_HOURS = 0
const START_OF_DAY_MINUTES = 0
const START_OF_DAY_SECONDS = 0

/**
 * END_OF_DAY_HOURS = 23
 * END_OF_DAY_MINUTES = 59
 * END_OF_DAY_SECONDS = 59
 * Represents the end of a day (23:59:59)
 * Used for the 'to' parameter to include all notifications until the end of the selected day
 * Example: If user selects 2026-05-27, we query until 2026-05-27T23:59:59Z
 * 
 * Rationale: This ensures that a single-day query (from=2026-05-27, to=2026-05-27)
 * returns all notifications for that entire day, not just those at midnight.
 */
const END_OF_DAY_HOURS = 23
const END_OF_DAY_MINUTES = 59
const END_OF_DAY_SECONDS = 59

/**
 * START_OF_DAY_MILLISECONDS = 0
 * Represents the start of milliseconds in a day (000)
 * Used for the 'from' parameter to ensure precision at the beginning of the day
 */
const START_OF_DAY_MILLISECONDS = 0

/**
 * END_OF_DAY_MILLISECONDS = 999
 * Represents the end of milliseconds in a day (999)
 * Used for the 'to' parameter to ensure we capture all milliseconds until the end of the day
 */
const END_OF_DAY_MILLISECONDS = 999

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
    
    console.log('[handleAPIError] Error data received:', { errorData, httpStatus })

    // Validate error response structure - at least message is required
    if (!errorData.status || !errorData.message) {
      // Missing critical fields - fail silently (Requirement 3.6)
      console.log('[handleAPIError] Missing status or message - failing silently')
      return null
    }

    // Verify response_status field matches HTTP status code (Requirement 3.5)
    if (errorData.status !== httpStatus) {
      // Status mismatch - fail silently (Requirement 3.6)
      console.log('[handleAPIError] Status mismatch - failing silently', { expected: httpStatus, got: errorData.status })
      return null
    }

    // Return structured error, even if timestamp/description are missing
    const result = {
      status: errorData.status,
      timestamp: errorData.timestamp || new Date().toISOString(),
      message: errorData.message,
      description: errorData.description || '',
    } as ErrorResponse
    
    console.log('[handleAPIError] Returning error:', result)
    return result
  } catch (error) {
    // Malformed JSON - fail silently (Requirement 3.6)
    console.log('[handleAPIError] Malformed JSON - failing silently', error)
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
  let response: Response
  
  try {
    response = await fetch(`${API_BASE_URL}/notifications`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // No authentication headers (Requirement 3.7)
      },
      body: JSON.stringify(notificationData),
    })
  } catch (error) {
    // Network error - backend unavailable (Requirement 3.3)
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }

  let data: unknown
  try {
    data = await response.json()
  } catch (error) {
    // Malformed JSON - fail silently (Requirement 3.6)
    if (!response.ok) {
      return {
        success: false,
        error: undefined,
      }
    }
    // For successful responses, treat parse error as network error
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }

  if (response.ok) {
    // Check if 200 response contains error information (Requirement 7.4)
    if (data && typeof data === 'object' && 'status' in data && 'message' in data && 'description' in data) {
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
  let response: Response
  
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
        // Convert date to ISO 8601 DATE_TIME format (e.g., 2026-05-27 -> 2026-05-27T00:00:00Z)
        // Set to start of day to include all notifications from the beginning of the selected day
        const fromDate = new Date(filters.from)
        fromDate.setHours(START_OF_DAY_HOURS, START_OF_DAY_MINUTES, START_OF_DAY_SECONDS, START_OF_DAY_MILLISECONDS)
        queryParams.append('from', fromDate.toISOString())
      }
      if (filters.to) {
        // Convert date to ISO 8601 DATE_TIME format and set to end of day
        // This ensures all notifications until the end of the selected day are included
        const toDate = new Date(filters.to)
        toDate.setHours(END_OF_DAY_HOURS, END_OF_DAY_MINUTES, END_OF_DAY_SECONDS, END_OF_DAY_MILLISECONDS)
        queryParams.append('to', toDate.toISOString())
      }
    }

    const queryString = queryParams.toString()
    const url = queryString
      ? `${API_BASE_URL}/notifications?${queryString}`
      : `${API_BASE_URL}/notifications`

    response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // No authentication headers (Requirement 3.7)
      },
    })
  } catch (error) {
    // Network error - backend unavailable
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }

  let data: unknown
  try {
    data = await response.json()
  } catch (error) {
    // Malformed JSON - fail silently (Requirement 3.6)
    if (!response.ok) {
      return {
        success: false,
        error: undefined,
      }
    }
    // For successful responses, treat parse error as network error
    return {
      success: false,
      error: 'Unable to connect to notification service. Please try again later.',
    }
  }

  if (response.ok) {
    // Check if 200 response contains error information
    if (data && typeof data === 'object' && 'status' in data && 'message' in data && 'description' in data) {
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
}
