/**
 * API Module Entry Point
 * 
 * Exports all API client functions and types for use in the application.
 */

export {
  sendNotification,
  queryNotifications,
  type NotificationRequest,
  type ErrorResponse,
  type APIResponse,
  type QueryFilters,
  type NotificationData,
} from './client'
