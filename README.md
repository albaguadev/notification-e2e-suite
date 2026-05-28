# Notification E2E Suite

A comprehensive end-to-end testing suite for the MultiChannelNotifier backend system, featuring a React frontend application and Playwright-based automated tests.

## Project Structure

```
notification-e2e-suite/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # React UI components
│   │   ├── api/        # API client module (see frontend/src/api/README.md)
│   │   └── utils/      # Utility functions
│   └── package.json
├── tests/              # Playwright E2E test suite (Python)
│   ├── pages/          # Page Object Models
│   ├── unit/           # Unit tests
│   ├── property/       # Property-based tests
│   ├── e2e/            # End-to-end flow tests
│   └── data/           # Test data files
└── .kiro/
    └── specs/          # Specification documents
```

## Technology Stack

**Frontend:**
- React 19+ with TypeScript
- Vite as build tool
- CSS Modules for styling
- Fetch API for HTTP requests

**Testing:**
- Playwright (Python)
- pytest as test runner
- Hypothesis for property-based testing
- pytest-html for reporting

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Git
- MultiChannelNotifier backend running on `http://localhost:8081`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Test Suite Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Run all tests
pytest

# Run specific test categories
pytest -m unit_test      # Unit tests only
pytest -m property_test  # Property-based tests only
pytest -m e2e_test       # E2E tests only

# Run with specific browser
pytest --browser firefox

# Run in headed mode (see browser)
pytest --headed
```

## Features

### Frontend Application

- **Notification Form**: Send notifications via EMAIL, SMS, or WHATSAPP
- **Notification Query**: View and filter notification history
- **Real-time Validation**: Client-side validation for all input fields
- **Error Handling**: Comprehensive error handling with user-friendly messages

### API Client Module

The frontend includes a robust API client module (`frontend/src/api/`) that handles all communication with the backend:

- Type-safe TypeScript interfaces
- Comprehensive error handling
- Silent failure for malformed responses
- Network error handling
- No authentication required

For detailed API client documentation, see [frontend/src/api/README.md](frontend/src/api/README.md)

### Test Suite

- **Page Object Models**: Maintainable test automation using POM pattern
- **Property-Based Testing**: Validates universal correctness properties with Hypothesis
- **Unit Tests**: Specific examples and edge cases
- **E2E Tests**: Complete user flow validation
- **HTML Reports**: Detailed test reports with screenshots
- **Multi-Browser Support**: Chromium, Firefox, and WebKit

## Backend Integration

The frontend communicates with the MultiChannelNotifier backend running on `http://localhost:8081`.

**API Endpoints:**
- `POST /api/v1/notifications` - Send notification
- `GET /api/v1/notifications` - Query notifications

Ensure the backend is running before testing the frontend or executing E2E tests.

## Documentation

- **Specifications**:
  - [Requirements](/.kiro/specs/notification-e2e-suite/requirements.md)
  - [Design](/.kiro/specs/notification-e2e-suite/design.md)
  - [Implementation Tasks](/.kiro/specs/notification-e2e-suite/tasks.md)

- **Testing**:
  - [Testing Configuration Guide](TESTING_CONFIGURATION.md)
  - [Quick Start Testing](QUICK_START_TESTING.md)
  - [Test Suite README](tests/README.md)

- **API**:
  - [API Client Documentation](frontend/src/api/README.md)

## Development

### Running the Frontend

```bash
cd frontend
npm run dev     # Development server
npm run build   # Production build
npm run preview # Preview production build
```

### Running Tests

```bash
# Run all tests with HTML report
pytest --html=reports/test_report.html

# Run tests in parallel (faster)
pytest -n auto

# Run with coverage
pytest --cov=tests --cov-report=html
```

### Code Quality

```bash
# Frontend
cd frontend
npm run lint    # ESLint
npm run format  # Prettier

# Tests
cd tests
black .         # Format Python code
flake8 .        # Lint Python code
```

## CI/CD

The test suite is designed to run in CI/CD environments:

```bash
# Headless mode (default)
pytest

# Generate artifacts
pytest --html=reports/test_report.html --self-contained-html
```

Exit codes:
- `0`: All tests passed
- `1`: One or more tests failed

## License

MIT
