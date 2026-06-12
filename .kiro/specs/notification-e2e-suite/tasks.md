# Implementation Plan: Notification E2E Suite

## Overview

This implementation plan covers the development of a React frontend application with comprehensive Playwright E2E testing in Python. The implementation follows a layered approach: first establishing the React application structure and core UI components, then building the API integration layer, and finally creating the comprehensive test suite with property-based testing using Hypothesis.

The implementation is organized to enable early validation through incremental development, with checkpoints to ensure quality at each stage.

## Tasks

- [x] 1. Set up React frontend project structure
  - Initialize React application with Vite
  - Configure project dependencies (React 18+, TypeScript)
  - Set up CSS for styling
  - Create directory structure: src/components, src/api, src/utils
  - Add data-testid attributes to all interactive elements for testing
  - _Requirements: 1.1, 1.2, 12.3_

- [x] 2. Implement core React UI components
  - [x] 2.1 Create App component with layout structure
    - Implement root component with header and main content area
    - Set up component composition for NotificationForm and NotificationQuery
    - Add global styling and theme
    - _Requirements: 1.2, 2.1_
  
  - [x] 2.2 Implement NotificationForm component with state management
    - Create functional component with useState hooks for form state (type, recipient, message, subject)
    - Implement useState hooks for UI state (errors, status, responseMessage)
    - Add form field rendering with proper labels and data-testid attributes
    - Implement controlled inputs with onChange handlers
    - Add dropdown for notification type selection (EMAIL, SMS, WHATSAPP)
    - _Requirements: 1.2, 1.3, 2.1, 2.4_
  
  - [x] 2.3 Implement subject field visibility logic
    - Add conditional rendering to show subject field only for EMAIL type
    - Implement logic to manage subject field visibility based on type selection
    - Ensure subject field remains visible when user has entered text until form submission or manual clear
    - _Requirements: 2.5, 6.6_
  
  - [x] 2.4 Implement client-side validation logic
    - Add validation functions for email format (RFC 5322 compliant regex)
    - Add validation for SMS phone numbers (ES region: +34 followed by 9 digits starting with 6 or 7)
    - Add validation for WhatsApp phone numbers (E.164 format with + prefix)
    - Implement real-time validation on input change
    - Display inline error messages for invalid inputs
    - Prevent form submission when validation fails
    - _Requirements: 2.4, 2.6, 6.2, 6.4_
  
  - [x] 2.5 Create StatusDisplay component
    - Implement presentational component with props for type, message, and onDismiss
    - Add styling for success, error, and info message types
    - Implement dismiss functionality with optional callback
    - _Requirements: 2.3_
  
  - [x] 2.6 Implement NotificationQuery component
    - Create functional component with useState hooks for filters and results
    - Add filter form with inputs for type, status, from date, and to date
    - Implement controlled inputs for all filter fields
    - Add results display area with table or list format
    - Add loading and error state management
    - Display "no results" message when appropriate
    - _Requirements: 4.2, 4.4, 4.5_

- [x] 3. Checkpoint - Verify React components render correctly
  - Ensure all components render without errors
  - Verify form fields are interactive
  - Check that validation messages display correctly
  - Ask the user if questions arise

- [x] 4. Implement API client module
  - [x] 4.1 Create API client with sendNotification function
    - Implement POST request to http://localhost:8081/api/v1/notifications
    - Add proper headers (Content-Type: application/json)
    - Ensure no authentication headers are included
    - Handle request body formatting with type, recipient, message, and optional subject
    - Return structured response object with success, data, and error fields
    - _Requirements: 3.1, 3.2, 3.7_
  
  - [x] 4.2 Implement error handling logic
    - Create handleAPIError function to parse error JSON responses
    - Validate error response structure (status, timestamp, message, description)
    - Verify response_status field matches HTTP status code
    - Implement silent failure for malformed JSON or missing fields
    - Handle network errors with user-friendly messages
    - _Requirements: 3.3, 3.4, 3.5, 3.6_
  
  - [x] 4.3 Create queryNotifications function
    - Implement GET request to http://localhost:8081/api/v1/notifications
    - Add query parameter formatting for filters (type, status, from, to)
    - Handle response parsing and error handling
    - Return structured response with notifications array
    - _Requirements: 4.1, 4.3_

- [x] 5. Integrate API client with React components
  - [x] 5.1 Wire NotificationForm to API client
    - Add form submission handler that calls sendNotification
    - Implement loading state during API request
    - Display success message on successful submission
    - Display error message on failure using StatusDisplay component
    - Clear form after successful submission
    - Handle 200 responses with error content by checking response body
    - _Requirements: 2.2, 2.3, 6.3, 6.5, 7.4_
  
  - [x] 5.2 Wire NotificationQuery to API client
    - Add search handler that calls queryNotifications with filters
    - Implement loading state during query
    - Display results in readable format
    - Handle empty results with appropriate message
    - Display error messages for failed queries
    - _Requirements: 4.4, 4.5, 7.6_


- [x] 6. Checkpoint - Test frontend with backend integration
  - Start backend server on http://localhost:8081
  - Test sending notifications through UI for all channel types
  - Verify error handling with backend unavailable
  - Test query functionality with various filters
  - Ask the user if questions arise

- [x] 7. Set up Playwright E2E test framework
  - [x] 7.1 Initialize Python project for testing
    - Create tests directory structure (conftest.py, pages/, unit/, property/, e2e/, data/, utils/)
    - Set up pyproject.toml or requirements.txt with dependencies (playwright, pytest, pytest-playwright, pytest-html, hypothesis)
    - Install Playwright browsers with `playwright install`
    - Configure pytest.ini with test discovery patterns and markers
    - _Requirements: 5.1, 5.2, 12.3_
  
  - [x] 7.2 Configure Playwright and pytest settings
    - Create pytest configuration for headless/headed modes
    - Configure browser engines (Chromium, Firefox, WebKit)
    - Set up HTML report generation with pytest-html
    - Configure screenshot capture for all tests
    - Add test markers for unit_test, property_test, e2e_test
    - _Requirements: 5.3, 5.4, 8.2, 8.5_
  
  - [x] 7.3 Create test fixtures in conftest.py
    - Implement browser context fixture
    - Create page fixtures for test isolation
    - Add test data fixture with valid notification examples
    - Implement cleanup fixture with silent failure handling
    - Add fixtures for NotificationPage and QueryPage instances
    - _Requirements: 5.5, 11.2, 11.4, 11.5_

- [x] 8. Implement Page Object Models
  - [x] 8.1 Create NotificationPage class
    - Define locators for all form elements using data-testid attributes
    - Implement navigate() method to load application
    - Add select_type() method for notification type selection
    - Implement fill_form() method with parameters for all fields
    - Add submit() method to trigger form submission
    - Implement get_status_message() to retrieve UI feedback
    - Add is_subject_visible() to check subject field visibility
    - _Requirements: 6.1_
  
  - [x] 8.2 Create QueryPage class
    - Define locators for filter inputs and results area
    - Implement navigate() method
    - Add apply_filters() method with optional parameters
    - Implement search() method to trigger query
    - Add get_results_count() to count displayed notifications
    - Implement has_no_results_message() to check for empty state
    - _Requirements: 6.1_

- [x] 9. Checkpoint - Verify test framework setup
  - Run a simple smoke test to verify Playwright is working
  - Ensure page objects can interact with React application
  - Verify fixtures are properly initialized
  - Ask the user if questions arise


- [x] 10. Implement unit tests for component rendering
  - [x] 10.1 Write tests for NotificationForm rendering
    - Test that all form fields render correctly
    - Verify type dropdown contains EMAIL, SMS, WHATSAPP options
    - Check that submit button is present and enabled
    - Test initial component state is correct
    - _Requirements: 6.1, 11.1_
  
  - [x] 10.2 Write tests for NotificationQuery rendering
    - Test that filter inputs render correctly
    - Verify search button is present
    - Check that results area is initially empty
    - Test that no-results message is hidden initially
    - _Requirements: 6.1_

- [x] 11. Implement unit tests for validation
  - [x] 11.1 Write tests for email validation
    - Test valid email formats are accepted
    - Test invalid email formats show error messages
    - Verify error messages display in real-time
    - _Requirements: 6.2, 6.4_
  
  - [x]* 11.2 Write tests for SMS validation
    - Test valid ES region phone numbers are accepted (+34612345678)
    - Test invalid phone numbers show error messages
    - Verify format requirements are enforced
    - _Requirements: 6.2, 6.4_
  
  - [x]* 11.3 Write tests for WhatsApp validation
    - Test valid E.164 format numbers are accepted
    - Test numbers without + prefix show error messages
    - Verify international format is enforced
    - _Requirements: 6.2, 6.4_
  
  - [x]* 11.4 Write test for required field validation
    - Test that empty required fields prevent submission
    - Verify error messages display for missing fields
    - Test that form submission is blocked when validation fails
    - _Requirements: 2.4, 2.6_

- [x] 12. Implement unit tests for error handling
  - [x] 12.1 Write test for backend unavailable scenario
    - Mock network failure
    - Verify UI displays user-friendly error message
    - Test that technical details are not exposed to user
    - _Requirements: 3.3_
  
  - [x]* 12.2 Write test for malformed error response
    - Mock backend response with invalid JSON
    - Verify UI fails silently with no error message
    - Test that application doesn't crash
    - _Requirements: 3.6_
  
  - [x]* 12.3 Write test for 200 response with error content
    - Mock backend returning 200 with error information in body
    - Verify UI checks response body and displays error feedback
    - _Requirements: 7.4_
  
  - [x]* 12.4 Write test for subject field persistence
    - Fill subject field with text
    - Switch notification type from EMAIL to SMS
    - Verify subject field remains visible until form submission or manual clear
    - _Requirements: 6.6_


- [x] 13. Create Hypothesis strategies for property-based testing
  - [x] 13.1 Create test data generators in utils/generators.py
    - Implement strategy for valid email addresses
    - Implement strategy for valid ES region phone numbers
    - Implement strategy for valid E.164 phone numbers
    - Implement strategy for notification types (EMAIL, SMS, WHATSAPP)
    - Implement strategy for message content (1-500 characters)
    - Implement strategy for error responses with various status codes
    - _Requirements: 9.4_

- [x] 14. Implement property-based tests
  - [x]* 14.1 Write property test for form submission triggers API request
    - **Property 1: Form Submission Triggers API Request**
    - **Validates: Requirements 2.2, 3.1, 6.3**
    - Use Hypothesis to generate valid notification data
    - Intercept network requests during form submission
    - Verify POST request is sent to correct endpoint with all required fields
    - Run minimum 25 iterations
    - _Requirements: 2.2, 3.1, 6.3_
  
  - [x] 14.2 Write property test for backend response display
    - **Property 2: Backend Response Display**
    - **Validates: Requirements 2.3, 6.5, 7.1, 7.2, 7.3, 7.6**
    - Generate various backend responses (success and error)
    - Mock backend responses
    - Verify UI displays appropriate feedback for each response type
    - Run minimum 25 iterations
    - _Requirements: 2.3, 6.5, 7.1, 7.2, 7.3, 7.6_
  
  - [x] 14.3 Write property test for required field validation
    - **Property 3: Required Field Validation**
    - **Validates: Requirements 2.4, 2.6**
    - Generate form data with missing required fields
    - Attempt form submission
    - Verify submission is prevented and validation errors display
    - Run minimum 25 iterations
    - _Requirements: 2.4, 2.6_
  
  - [x] 14.4 Write property test for subject field visibility
    - **Property 4: Subject Field Visibility**
    - **Validates: Requirements 2.5**
    - Generate non-EMAIL notification types (SMS, WHATSAPP)
    - Select each type in the form
    - Verify subject field is hidden for all non-EMAIL types
    - Run minimum 25 iterations
    - _Requirements: 2.5_
  
  - [x] 14.5 Write property test for channel type support
    - **Property 5: Channel Type Support**
    - **Validates: Requirements 3.2**
    - Generate valid notification data for all channel types
    - Submit notifications through UI
    - Verify backend receives correct channel-specific format
    - Run minimum 25 iterations
    - _Requirements: 3.2_
  
  - [x] 14.6 Write property test for error response parsing
    - **Property 6: Error Response Parsing**
    - **Validates: Requirements 3.4, 3.5, 7.5**
    - Generate error responses with status codes 400, 404, 500, 503
    - Mock backend error responses
    - Verify UI parses error JSON and displays message and description
    - Run minimum 25 iterations
    - _Requirements: 3.4, 3.5, 7.5_
  
  - [x] 14.7 Write property test for malformed error handling
    - **Property 7: Malformed Error Handling**
    - **Validates: Requirements 3.6**
    - Generate malformed error responses (invalid JSON, missing fields)
    - Mock backend responses
    - Verify UI fails silently with no error message
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 3.6_
  
  - [x] 14.8 Write property test for no authentication headers
    - **Property 8: No Authentication Headers**
    - **Validates: Requirements 3.7**
    - Generate various API requests (POST and GET)
    - Intercept network requests
    - Verify no authentication headers are present
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 3.7_
  
  - [x] 14.9 Write property test for query filter parameters
    - **Property 9: Query Filter Parameters**
    - **Validates: Requirements 4.3**
    - Generate various combinations of query filters
    - Apply filters and trigger search
    - Verify GET request includes filters as query parameters
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 4.3_
  
  - [x] 14.10 Write property test for query results display
    - **Property 10: Query Results Display**
    - **Validates: Requirements 4.4**
    - Generate various notification data sets
    - Mock backend query responses
    - Verify UI displays results in readable format with proper formatting
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 4.4_
  
  - [x] 14.11 Write property test for component rendering
    - **Property 11: Component Rendering**
    - **Validates: Requirements 6.1**
    - Generate various component states
    - Render components in browser
    - Verify all expected elements are visible and interactive
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 6.1_
  
  - [x] 14.12 Write property test for client-side validation
    - **Property 12: Client-Side Validation**
    - **Validates: Requirements 6.2, 6.4**
    - Generate invalid inputs for each channel type
    - Interact with form elements
    - Verify appropriate validation error messages display in real-time
    - Run minimum 25 iterations with optimizations:
      - Hypothesis: `verbosity=Verbosity.quiet` and `suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]`
      - Playwright context: 5-second action timeout for faster failure detection
      - Headless mode enabled by default for faster execution
    - _Requirements: 6.2, 6.4_


- [x] 15. Checkpoint - Verify property-based tests
  - Run all property tests with minimum 25 iterations
  - Review test coverage for all correctness properties
  - Ensure all tests pass consistently
  - Ask the user if questions arise

- [x] 16. Implement E2E flow tests
  - [x] 16.1 Write E2E test for EMAIL notification flow
    - Navigate to application
    - Fill form with valid EMAIL data including subject
    - Submit form
    - Verify UI displays success message or error message based on backend response
    - _Requirements: 7.1_
  
  - [x] 16.2 Write E2E test for SMS notification flow
    - Navigate to application
    - Fill form with valid SMS data (ES region phone number)
    - Submit form
    - Verify UI displays success message or error message based on backend response
    - _Requirements: 7.2_
  
  - [x] 16.3 Write E2E test for WHATSAPP notification flow
    - Navigate to application
    - Fill form with valid WHATSAPP data (E.164 format)
    - Submit form
    - Verify UI displays success message or error message based on backend response
    - _Requirements: 7.3_
  
  - [x] 16.4 Write E2E test for notification query flow
    - Navigate to application
    - Apply filters (type, status, date range)
    - Trigger search
    - Verify UI displays retrieved notifications correctly with proper formatting
    - Verify no error messages are shown for successful queries
    - _Requirements: 7.6_

- [x] 17. Implement test data management
  - [x] 17.1 Create test data files
    - Create data/valid_notifications.json with example valid notifications
    - Create data/invalid_notifications.json with example invalid inputs
    - Create data/error_responses.json with example error responses
    - _Requirements: 9.1, 9.5_
  
  - [x] 17.2 Implement test data loading utilities
    - Create helper functions to load test data from JSON files
    - Add validation for test data structure
    - Implement error handling for invalid test data with clear error messages
    - _Requirements: 9.2, 9.3_

- [ ] 18. Configure test reporting
  - [ ] 18.1 Set up HTML report generation
    - Configure pytest-html to generate detailed reports
    - Add execution time tracking for each test
    - Include pass/fail status for all tests
    - Add detailed error messages and stack traces for failures
    - _Requirements: 8.1, 8.3, 8.4_
  
  - [ ]* 18.2 Configure screenshot capture
    - Set up automatic screenshot capture for all tests
    - Configure screenshot storage location
    - Add screenshots to HTML reports
    - _Requirements: 8.2_


- [ ] 19. Configure CI/CD support
  - [ ] 19.1 Add CI/CD configuration
    - Create configuration for headless browser mode
    - Set up proper exit codes for test success/failure
    - Configure test artifact generation
    - Add support for parallel test execution
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 20. Create documentation
  - [ ] 20.1 Write README with setup instructions
    - Document prerequisites (Node.js, Python, Playwright)
    - Provide step-by-step setup instructions
    - Include commands to run frontend and tests
    - Add troubleshooting section
    - _Requirements: 12.1, 12.4_
  
  - [ ] 20.2 Create example tests and documentation
    - Add example tests demonstrating common patterns
    - Document Page Object Model usage
    - Provide examples of property-based tests
    - Document test data management approach
    - _Requirements: 12.2_
  
  - [ ] 20.3 Add linting and formatting configuration
    - Set up ESLint for React code
    - Configure Prettier for code formatting
    - Add Black and Flake8 for Python code
    - Create pre-commit hooks for code quality
    - _Requirements: 12.5_

- [ ] 21. Final checkpoint - Complete system verification
  - Run full test suite (unit, property, E2E) in all browser engines
  - Verify HTML reports are generated correctly
  - Test frontend with backend integration for all notification types
  - Ensure all documentation is complete and accurate
  - Ask the user if questions arise

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- The React frontend uses TypeScript with functional components and hooks (Requirements 1.1, 1.2, 1.3)
- The test suite uses Python with Playwright and Hypothesis for property-based testing (Requirements 5.1)
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and quality gates
- Property tests validate universal correctness properties with minimum 25-100 iterations
- Unit tests validate specific examples, edge cases, and integration points
- E2E tests validate complete user flows from UI perspective
- The backend MultiChannelNotifier must be running on http://localhost:8081 for integration testing
- All React components must include data-testid attributes for reliable test automation
- Test cleanup operations fail silently to prevent test suite interruption (Requirement 11.5)

### Test Performance Optimizations

All property-based tests have been optimized for faster execution:

**Hypothesis Settings**:
- All property tests use `verbosity=Verbosity.quiet` to reduce output overhead
- Health checks suppressed: `HealthCheck.function_scoped_fixture` (fixtures) and `HealthCheck.too_slow` (slow test warnings)
- Minimum 25 iterations per property test (configurable via `max_examples`)

**Playwright Configuration** (conftest.py):
- Browser context action timeout: 5 seconds (fail fast on timeouts)
- Headless mode enabled by default for all tests
- Screenshot capture for all tests for debugging

**pytest.ini Configuration**:
- Headless Chromium browser as default
- HTML reports generated automatically
- Support for parallel execution: `pytest -n auto` (requires pytest-xdist)

**Execution Tips**:
- Run property tests in quiet mode: `pytest tests/property/ -v` (default)
- Run with parallel execution (faster): `pytest tests/property/ -n auto`
- Run specific property test: `pytest tests/property/test_malformed_error_handling.py -v`
- Run with higher iteration count: `pytest tests/property/ --hypothesis-seed=0`


## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["7.1"] },
    { "id": 1, "tasks": ["7.2"] },
    { "id": 2, "tasks": ["7.3"] },
    { "id": 3, "tasks": ["8.1", "8.2"] },
    { "id": 4, "tasks": ["4.1", "10.1", "10.2"] },
    { "id": 5, "tasks": ["4.2", "4.3", "11.1", "11.2", "11.3", "11.4"] },
    { "id": 6, "tasks": ["5.1", "5.2", "12.1", "12.2", "12.3", "12.4", "13.1"] },
    { "id": 7, "tasks": ["14.1", "14.2", "14.3", "14.4", "14.5", "14.6", "14.7", "14.8", "14.9", "14.10", "14.11", "14.12"] },
    { "id": 8, "tasks": ["16.1", "16.2", "16.3", "16.4", "17.1", "17.2"] },
    { "id": 9, "tasks": ["18.1", "18.2", "19.1"] },
    { "id": 10, "tasks": ["20.1", "20.2", "20.3"] }
  ]
}
```
