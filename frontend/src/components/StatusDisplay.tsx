import './StatusDisplay.css'

interface StatusDisplayProps {
  type: 'success' | 'error' | 'info'
  message: string
  onDismiss?: () => void
}

function StatusDisplay({ type, message, onDismiss }: StatusDisplayProps) {
  return (
    <div className={`status-display status-display--${type}`} data-testid="status-message">
      <div className="status-display__content">
        <span className="status-display__icon">
          {type === 'success' && '✓'}
          {type === 'error' && '✕'}
          {type === 'info' && 'ℹ'}
        </span>
        <span className="status-display__message">{message}</span>
      </div>
      {onDismiss && (
        <button
          className="status-display__dismiss"
          onClick={onDismiss}
          aria-label="Dismiss message"
        >
          ×
        </button>
      )}
    </div>
  )
}

export default StatusDisplay
