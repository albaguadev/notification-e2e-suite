import { useState } from 'react'
import StatusDisplay from './StatusDisplay'
import { queryNotifications } from '../api/client'
import type { QueryFilters, ErrorResponse } from '../api/client'
import './NotificationQuery.css'

interface Notification {
  id: string
  type: string
  recipient: string
  message: string
  subject?: string
  status: string
  timestamp: string
}

function NotificationQuery() {
  // Filter state
  const [filters, setFilters] = useState<QueryFilters>({
    type: undefined,
    status: undefined,
    from: undefined,
    to: undefined,
  })

  // Results state
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFilterChange = (field: keyof QueryFilters, value: string | undefined) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setNotifications([])

    try {
      // Call API client with filters (Requirement 4.4, 4.5, 7.6)
      const response = await queryNotifications(filters)

      if (response.success && response.data) {
        // Success response (Requirement 4.4, 4.5)
        if (response.data.length === 0) {
          // Handle empty results (Requirement 4.5)
          setNotifications([])
        } else {
          // Display results in readable format (Requirement 4.4)
          // Map NotificationData to Notification, ensuring id is always present
          const mappedNotifications = response.data.map(notif => ({
            ...notif,
            id: notif.id || `${notif.timestamp}-${notif.recipient}`,
          }))
          setNotifications(mappedNotifications)
        }
      } else {
        // Error response (Requirement 7.6)
        if (response.error) {
          if (typeof response.error === 'string') {
            // Network error message
            setError(response.error)
          } else {
            // Structured error response
            const errorData = response.error as ErrorResponse
            setError(`${errorData.message}: ${errorData.description}`)
          }
        } else {
          // Malformed error response - fail silently
          setError('')
        }
      }
    } catch (err) {
      setError('Unable to connect to notification service. Please try again later.')
    } finally {
      setLoading(false)
    }
  }

  const handleClearFilters = () => {
    setFilters({
      type: undefined,
      status: undefined,
      from: undefined,
      to: undefined,
    })
    setNotifications([])
    setError('')
  }

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return date.toLocaleString()
    } catch {
      return timestamp
    }
  }

  return (
    <div className="notification-query-container">
      <h2>Query Notifications</h2>

      {error && (
        <StatusDisplay
          type="error"
          message={error}
          onDismiss={() => setError('')}
        />
      )}

      <form className="query-form" onSubmit={handleSearch}>
        <div className="filter-row">
          <div className="form-group">
            <label htmlFor="filter-type">Type</label>
            <select
              id="filter-type"
              data-testid="filter-type"
              value={filters.type || ''}
              onChange={(e) => handleFilterChange('type', e.target.value || undefined)}
            >
              <option value="">All</option>
              <option value="EMAIL">EMAIL</option>
              <option value="SMS">SMS</option>
              <option value="WHATSAPP">WHATSAPP</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="filter-status">Status</label>
            <input
              type="text"
              id="filter-status"
              data-testid="filter-status"
              value={filters.status || ''}
              onChange={(e) => handleFilterChange('status', e.target.value || undefined)}
              placeholder="e.g., SENT, FAILED"
            />
          </div>
        </div>

        <div className="filter-row">
          <div className="form-group">
            <label htmlFor="filter-from">From Date</label>
            <input
              type="date"
              id="filter-from"
              data-testid="filter-from"
              value={filters.from || ''}
              onChange={(e) => handleFilterChange('from', e.target.value || undefined)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="filter-to">To Date</label>
            <input
              type="date"
              id="filter-to"
              data-testid="filter-to"
              value={filters.to || ''}
              onChange={(e) => handleFilterChange('to', e.target.value || undefined)}
            />
          </div>
        </div>

        <div className="button-group">
          <button
            type="submit"
            data-testid="search"
            className="search-button"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
          <button
            type="button"
            className="clear-button"
            onClick={handleClearFilters}
            disabled={loading}
          >
            Clear Filters
          </button>
        </div>
      </form>

      <div className="results-section">
        {loading && <div className="loading-message">Loading...</div>}

        {!loading && notifications.length === 0 && !error && (
          <div className="no-results" data-testid="no-results">
            No notifications found. Try adjusting your filters or send a notification first.
          </div>
        )}

        {!loading && notifications.length > 0 && (
          <div className="results-table-container">
            <table className="results-table" data-testid="results">
              <thead>
                <tr>
                  <th>Type</th>
                  <th>Recipient</th>
                  <th>Message</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {notifications.map((notification) => (
                  <tr key={notification.id}>
                    <td>
                      <span className={`type-badge type-badge--${notification.type.toLowerCase()}`}>
                        {notification.type}
                      </span>
                    </td>
                    <td>{notification.recipient}</td>
                    <td className="message-cell">{notification.message}</td>
                    <td>{notification.subject || '-'}</td>
                    <td>
                      <span className="status-badge">{notification.status}</span>
                    </td>
                    <td className="timestamp-cell">{formatTimestamp(notification.timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default NotificationQuery
