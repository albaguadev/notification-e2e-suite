import { useState, useEffect } from 'react'
import StatusDisplay from './StatusDisplay'
import { sendNotification } from '../api/client'
import type { NotificationRequest, ErrorResponse } from '../api/client'
import './NotificationForm.css'

type NotificationType = 'EMAIL' | 'SMS' | 'WHATSAPP'

interface FormErrors {
  type?: string
  recipient?: string
  message?: string
  subject?: string
}

function NotificationForm() {
  // Form state
  const [type, setType] = useState<NotificationType>('EMAIL')
  const [recipient, setRecipient] = useState('')
  const [message, setMessage] = useState('')
  const [subject, setSubject] = useState('')

  // UI state
  const [errors, setErrors] = useState<FormErrors>({})
  const [status, setStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [responseMessage, setResponseMessage] = useState('')
  const [showSubject, setShowSubject] = useState(true)

  // Subject field visibility logic (Requirement 2.5, 6.6)
  useEffect(() => {
    if (type === 'EMAIL') {
      setShowSubject(true)
    } else {
      // Hide subject field only if it's empty
      if (subject === '') {
        setShowSubject(false)
      }
      // If subject has text, keep it visible until form submission or manual clear
    }
  }, [type, subject])

  // Validation functions (Requirement 2.4, 2.6, 6.2, 6.4)
  const validateEmail = (email: string): boolean => {
    // RFC 5322 compliant regex
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    return emailRegex.test(email)
  }

  const validateSMS = (phone: string): boolean => {
    // ES region: +34 followed by 9 digits starting with 6 or 7
    const smsRegex = /^\+34[67]\d{8}$/
    return smsRegex.test(phone)
  }

  const validateWhatsApp = (phone: string): boolean => {
    // E.164 format with + prefix: minimum 7 digits, maximum 15 digits
    const whatsappRegex = /^\+\d{7,15}$/
    return whatsappRegex.test(phone)
  }

  const validateRecipient = (value: string): string | undefined => {
    if (!value.trim()) {
      return 'Recipient is required'
    }

    switch (type) {
      case 'EMAIL':
        if (!validateEmail(value)) {
          return 'Invalid email format'
        }
        break
      case 'SMS':
        if (!validateSMS(value)) {
          return 'Invalid SMS phone number. Use format: +34 followed by 9 digits starting with 6 or 7'
        }
        break
      case 'WHATSAPP':
        if (!validateWhatsApp(value)) {
          return 'Invalid WhatsApp phone number. Use E.164 format with + prefix'
        }
        break
    }
    return undefined
  }

  const validateForm = (): boolean => {
    const newErrors: FormErrors = {}

    if (!type) {
      newErrors.type = 'Notification type is required'
    }

    const recipientError = validateRecipient(recipient)
    if (recipientError) {
      newErrors.recipient = recipientError
    }

    if (!message.trim()) {
      newErrors.message = 'Message is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Real-time validation on input change
  const handleRecipientChange = (value: string) => {
    setRecipient(value)
    // Always validate, even if empty (to show required error)
    const error = validateRecipient(value)
    setErrors(prev => ({ ...prev, recipient: error }))
  }

  const handleMessageChange = (value: string) => {
    setMessage(value)
    // Always validate, even if empty (to show required error)
    if (!value.trim()) {
      setErrors(prev => ({ ...prev, message: 'Message is required' }))
    } else {
      setErrors(prev => ({ ...prev, message: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    // Validate form
    if (!validateForm()) {
      return
    }

    setStatus('loading')
    setResponseMessage('')

    try {
      // Build notification request (Requirement 2.2, 3.1, 6.3)
      const notificationData: NotificationRequest = {
        type,
        recipient,
        message,
      }

      // Only include subject for EMAIL type
      if (type === 'EMAIL' && subject.trim()) {
        notificationData.subject = subject
      }

      // Call API client (Requirement 2.2, 3.1, 6.3)
      const response = await sendNotification(notificationData)

      if (response.success) {
        // Success response (Requirement 2.3, 6.5)
        setStatus('success')
        setResponseMessage('Notification sent successfully!')
        // Clear form after successful submission (Requirement 5.1)
        setRecipient('')
        setMessage('')
        setSubject('')
        setErrors({})
      } else {
        // Error response (Requirement 2.3, 6.5, 7.4)
        if (response.error) {
          // Check if error is an object (structured error) or string (network error)
          if (typeof response.error === 'string') {
            // Network error message
            setStatus('error')
            setResponseMessage(response.error)
          } else if (typeof response.error === 'object' && 'message' in response.error && 'description' in response.error) {
            // Structured error response with message and description (Requirement 3.4, 3.5)
            const errorData = response.error as ErrorResponse
            setStatus('error')
            // Display both message and description from error response
            const errorMessage = `${errorData.message}. ${errorData.description}`.trim()
            setResponseMessage(errorMessage || 'An error occurred. Please try again.')
          } else {
            // Malformed error response - show generic error (Requirement 3.6)
            setStatus('error')
            setResponseMessage('An error occurred. Please try again.')
          }
        } else {
          // No error provided - malformed response
          setStatus('error')
          setResponseMessage('An error occurred. Please try again.')
        }
      }
    } catch (error) {
      // Unexpected error
      setStatus('error')
      setResponseMessage('An unexpected error occurred. Please try again.')
    }
  }

  const handleDismissStatus = () => {
    setStatus('idle')
    setResponseMessage('')
  }

  return (
    <div className="notification-form-container">
      <h2>Send Notification</h2>
      
      {status !== 'idle' && responseMessage && (
        <StatusDisplay
          type={status === 'success' ? 'success' : 'error'}
          message={responseMessage}
          onDismiss={handleDismissStatus}
        />
      )}

      <form className="notification-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="notification-type">
            Notification Type <span className="required">*</span>
          </label>
          <select
            id="notification-type"
            data-testid="notification-type"
            value={type}
            onChange={(e) => setType(e.target.value as NotificationType)}
            className={errors.type ? 'error' : ''}
          >
            <option value="EMAIL">EMAIL</option>
            <option value="SMS">SMS</option>
            <option value="WHATSAPP">WHATSAPP</option>
          </select>
          {errors.type && <span className="error-message" data-testid="type-error">{errors.type}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="recipient">
            Recipient <span className="required">*</span>
          </label>
          <input
            type="text"
            id="recipient"
            data-testid="recipient"
            value={recipient}
            onChange={(e) => handleRecipientChange(e.target.value)}
            placeholder={
              type === 'EMAIL'
                ? 'user@example.com'
                : type === 'SMS'
                ? '+34612345678'
                : '+34612345678'
            }
            className={errors.recipient ? 'error' : ''}
          />
          {errors.recipient && <span className="error-message" data-testid="recipient-error">{errors.recipient}</span>}
        </div>

        {showSubject && (
          <div className="form-group">
            <label htmlFor="subject">
              Subject {type === 'EMAIL' && <span className="optional">(optional)</span>}
            </label>
            <input
              type="text"
              id="subject"
              data-testid="subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Email subject"
              className={errors.subject ? 'error' : ''}
            />
            {errors.subject && <span className="error-message" data-testid="subject-error">{errors.subject}</span>}
          </div>
        )}

        <div className="form-group">
          <label htmlFor="message">
            Message <span className="required">*</span>
          </label>
          <textarea
            id="message"
            data-testid="message"
            value={message}
            onChange={(e) => handleMessageChange(e.target.value)}
            placeholder="Enter your message"
            rows={4}
            className={errors.message ? 'error' : ''}
          />
          {errors.message && <span className="error-message" data-testid="message-error">{errors.message}</span>}
        </div>

        <button
          type="submit"
          data-testid="submit"
          className="submit-button"
          disabled={status === 'loading'}
        >
          {status === 'loading' ? 'Sending...' : 'Send Notification'}
        </button>
      </form>
    </div>
  )
}

export default NotificationForm
