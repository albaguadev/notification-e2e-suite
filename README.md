# Notification E2E Suite

A comprehensive end-to-end testing suite for the MultiChannelNotifier backend system, featuring a React frontend application and Playwright-based automated tests.

## Project Structure

```
notification-e2e-suite/
├── frontend/           # React frontend application
│   ├── src/
│   │   ├── components/ # React UI components
│   │   ├── api/        # API client module
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

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Test Suite Setup

```bash
cd tests
pip install -r requirements.txt
playwright install
pytest
```

## Backend Integration

The frontend communicates with the MultiChannelNotifier backend running on `http://localhost:8081`.

Ensure the backend is running before testing the frontend or executing E2E tests.

## Documentation

- [Requirements](/.kiro/specs/notification-e2e-suite/requirements.md)
- [Design](/.kiro/specs/notification-e2e-suite/design.md)
- [Implementation Tasks](/.kiro/specs/notification-e2e-suite/tasks.md)

## License

MIT
