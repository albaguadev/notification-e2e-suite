import { useState } from 'react'
import StatusDisplay from './StatusDisplay'
import './NotificationQuery.css'

interface QueryFilters {
  type?: string
  status?: string
  from?: string
  to?: string
}

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
    type: '',
    status: '',
    from: '',
    to: '',
  })

  // Results state
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFilterChange = (field: keyof QueryFilters, value: string) => {
    setFilters(prev => ({ ...prev, [field]: value }))
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setNotifications([])

    try {
      // Build query parameters
      const params = new URLSearchParams()
      if (filters.type) params.append('type', filters.type)
      if (filters.status) params.append('status', filters.status)
      if (filters.from) params.append('from', filters.from)
      if (filters.to) params.append('to', filters.to)

      const queryString = params.toString()
      const url = `http://localhost:8081/api/v1/notifications${queryString ? `?${queryString}` : ''}`

      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })

      if (response.ok) {
        const data = await response.json()
        
        // Check if response contains error information
        if (data.status && data.message && data.description) {
          setError(`${data.message}: ${data.description}`)
        } else if (Array.isArray(data)) {
          setNotifications(data)
        } else {
          setNotifications([])
        }
      } else {
        // Handle error responses
        const data = await response.json()
        if (data.status && data.message && data.description) {
          if (data.status === response.status) {
            setError(`${data.message}: ${data.description}`)
          }
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
      type: '',
      status: '',
      from: '',
      to: '',
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
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
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
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
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
              value={filters.from}
              onChange={(e) => handleFilterChange('from', e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="filter-to">To Date</label>
            <input
              type="date"
              id="filter-to"
              data-testid="filter-to"
              value={filters.to}
              onChange={(e) => handleFilterChange('to', e.target.value)}
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
