# INET-READY Development Guide

This guide provides comprehensive information for developers working on the INET-READY codebase, including project structure, development workflows, code standards, and testing procedures.

## Project Structure

```
inet-ready/
├── .github/                # GitHub workflows and actions
│   └── workflows/          # CI/CD workflow definitions
├── functions/              # Firebase Cloud Functions
├── public/                 # Static assets and data files
│   ├── data/               # CSV data files
│   │   ├── city_coords.csv
│   │   ├── historical_weather_data.csv
│   │   └── predicted_heat_index/
├── src/                    # Source code
│   ├── components/         # Svelte components
│   ├── lib/                # Shared libraries and utilities
│   │   ├── firebase/       # Firebase integration
│   │   └── services/       # Service modules
│   ├── routes/             # SvelteKit routes
│   ├── scripts/            # Python and Node.js scripts
│   │   ├── functions/      # Backend function scripts
│   │   ├── logs/           # Script logs
│   │   └── validation/     # Validation modules
│   └── styles/             # Global CSS styles
├── static/                 # Static files served as-is
│   └── firebase-messaging-sw.js  # Service worker
├── backup_env_to_proton.ps1      # Environment backup script
├── eslint.config.js              # ESLint configuration
├── jsconfig.json                 # JavaScript configuration
├── package.json                  # NPM dependencies
├── recover_env_from_proton.ps1   # Environment recovery script
├── requirements.txt              # Python dependencies
├── svelte.config.js              # Svelte configuration
└── vite.config.js                # Vite configuration
```

## Development Environment Setup

### Prerequisites

- Node.js (v18+ recommended)
- Python 3.8+
- Firebase CLI
- Git

### Initial Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/bpmiranda3099/inet-ready-v2.git
   cd inet-ready-v2
   ```

2. **Install Node.js dependencies**

   ```bash
   npm install
   ```

3. **Create Python virtual environment**

   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate

   # Install Python dependencies
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   - Create a `.env` file in the root with your Firebase configuration

   ```env
   VITE_FIREBASE_API_KEY=...
   VITE_FIREBASE_AUTH_DOMAIN=...
   VITE_FIREBASE_PROJECT_ID=...
   VITE_FIREBASE_STORAGE_BUCKET=...
   VITE_FIREBASE_MESSAGING_SENDER_ID=...
   VITE_FIREBASE_APP_ID=...
   VITE_FIREBASE_MEASUREMENT_ID=...
   VITE_FIREBASE_VAPID_KEY=...
   VITE_MAPBOX_API_KEY=...
   ```

5. **Set up Firebase credentials for backend scripts**
   - Place your Firebase service account key in `config/firebase-credentials.json`

### Running the Development Server

```bash
npm run dev
```

The server will be available at http://localhost:5173

### Running Backend Scripts

1. **Activate Python virtual environment**

   ```bash
   # Windows
   .\venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

2. **Run scripts manually**
   ```bash
   python src/scripts/hourly_heat_index_api.py
   ```

## Development Workflows

### Feature Development

1. **Create a new branch**

   ```bash
   git checkout -b feature/name-of-feature
   ```

2. **Implement the feature**

   - Follow the code standards described below
   - Add tests for new functionality
   - Update documentation as needed

3. **Run tests**

   ```bash
   npm test
   ```

4. **Create pull request**
   - Create a pull request against the `main` branch
   - Include a clear description of the changes
   - Reference any related issues

### Bug Fixes

1. **Create a bug fix branch**

   ```bash
   git checkout -b fix/bug-description
   ```

2. **Fix the bug**

   - Include test cases that reproduce the bug
   - Make the minimal changes needed to fix the issue

3. **Submit pull request**
   - Clearly describe the bug and the fix
   - Include steps to verify the fix works

### Code Reviews

All code changes should go through code review:

1. **Descriptive PR titles and descriptions**
2. **Focus on code quality, readability, and maintainability**
3. **Ensure test coverage for new features**
4. **Verify documentation is updated**
5. **Check for security issues**

## Code Standards

### JavaScript/Svelte

#### Style Guide

- Use ES6+ syntax
- Follow standard JavaScript naming conventions
  - camelCase for variables and functions
  - PascalCase for components and classes
  - UPPER_SNAKE_CASE for constants
- Use async/await instead of Promises/callbacks
- Use destructuring where appropriate
- Prefer const over let, avoid var

#### Component Structure

```svelte
<script>
	// 1. Imports
	import { onMount } from 'svelte';
	import OtherComponent from './OtherComponent.svelte';

	// 2. Props
	export let propName = defaultValue;

	// 3. Local state
	let localState = initialValue;

	// 4. Reactive declarations
	$: derivedValue = someCalculation(localState);

	// 5. Lifecycle functions
	onMount(() => {
		// Setup code

		return () => {
			// Cleanup code
		};
	});

	// 6. Event handlers
	function handleClick() {
		// Handle the event
	}

	// 7. Other functions
	function helperFunction() {
		// Implementation
	}
</script>

<!-- HTML markup -->
<div class="component">
	<h2>{propName}</h2>
	<p>{derivedValue}</p>
	<button on:click={handleClick}>Click me</button>
	<OtherComponent />
</div>

<style>
	/* Scoped styles */
	.component {
		margin: 1rem;
	}

	h2 {
		color: #333;
	}
</style>
```

### Python

#### Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use f-strings for string formatting
- Use docstrings for functions and classes
- Use type hints where possible

#### Script Structure

```python
#!/usr/bin/env python3
"""
Module docstring describing the purpose of the script.
"""

# 1. Standard library imports
import os
import json
import logging
from datetime import datetime

# 2. Third-party imports
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import firestore

# 3. Local imports
from validation import data_validation

# 4. Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, 'logs')
DATA_DIR = os.path.join(os.path.dirname(BASE_DIR), '..', 'public', 'data')

# 5. Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f'{datetime.now().strftime("%Y-%m-%d")}_script.log')),
        logging.StreamHandler()
    ]
)

# 6. Helper functions
def helper_function(param1, param2):
    """
    Description of what the function does.

    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2

    Returns:
        Description of the return value
    """
    # Implementation
    pass

# 7. Main function
def main():
    """Main function that runs the script."""
    try:
        logger.info("Starting script")

        # Implementation

        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Error in script execution: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
```

## Testing

### Frontend Testing

#### Component Testing

Use Svelte Testing Library for component tests:

```javascript
// Example component test
import { render, fireEvent, screen } from '@testing-library/svelte';
import CityPreferences from '../src/components/city-preferences.svelte';

describe('CityPreferences', () => {
	it('renders the city preferences component', () => {
		const { getByText } = render(CityPreferences);
		expect(getByText('City Preferences')).toBeInTheDocument();
	});

	it('allows adding a new city', async () => {
		const { getByLabelText, getByText } = render(CityPreferences);

		// Type a city name
		await fireEvent.input(getByLabelText('Search for a city'), {
			target: { value: 'Manila' }
		});

		// Click the add button
		await fireEvent.click(getByText('Add'));

		// Verify the city was added
		expect(getByText('Manila')).toBeInTheDocument();
	});
});
```

#### End-to-End Testing

Use Playwright for end-to-end testing:

```javascript
// Example E2E test
const { test, expect } = require('@playwright/test');

test('user can sign in and view dashboard', async ({ page }) => {
	// Navigate to the app
	await page.goto('http://localhost:5173');

	// Fill in login form
	await page.fill('input[type="email"]', 'test@example.com');
	await page.fill('input[type="password"]', 'password123');

	// Click login button
	await page.click('button[type="submit"]');

	// Verify navigation to dashboard
	await expect(page).toHaveURL(/.*\/dashboard/);

	// Verify dashboard content
	await expect(page.locator('h1')).toContainText('Dashboard');
	await expect(page.locator('.city-card')).toBeVisible();
});
```

### Backend Testing

#### Python Script Testing

Use pytest for Python script testing:

```python
# Example test for heat index calculation
import pytest
from src.scripts.heat_index_alert_service import calculate_heat_index

def test_calculate_heat_index():
    # Test normal conditions
    assert abs(calculate_heat_index(30, 50) - 30.8) < 0.1

    # Test extreme conditions
    assert abs(calculate_heat_index(40, 80) - 57.0) < 0.1

    # Test edge cases
    assert calculate_heat_index(0, 0) == 0
```

#### API Testing

Use supertest for testing API endpoints:

```javascript
// Example API test
const request = require('supertest');
const express = require('express');
const app = express();

app.use(require('../src/api/medical-data'));

describe('Medical Data API', () => {
	it('should get medical data for authenticated user', async () => {
		// Mock authentication middleware
		app.use((req, res, next) => {
			req.user = { uid: 'test-user-id' };
			next();
		});

		const res = await request(app).get('/get-medical-data');

		expect(res.status).toBe(200);
		expect(res.body).toHaveProperty('medicalData');
	});
});
```

## Deployment

### Frontend Deployment

#### Vercel Deployment

1. Connect your GitHub repository to Vercel
2. Configure the project settings:
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`
3. Add environment variables from your `.env` file
4. Deploy

### Backend Deployment

#### Firebase Functions

1. **Install Firebase CLI globally**

   ```bash
   npm install -g firebase-tools
   ```

2. **Login to Firebase**

   ```bash
   firebase login
   ```

3. **Initialize Firebase Functions**

   ```bash
   firebase init functions
   ```

4. **Deploy Functions**
   ```bash
   firebase deploy --only functions
   ```

#### GitHub Actions

INET-READY uses GitHub Actions for automated data collection, processing, and notifications. Workflows are defined in `.github/workflows/`.

Key workflows:

- `hourly_weather_update.yml`: Runs every hour to collect current weather data
- `daily_historical_weather_update.yml`: Runs daily to update historical weather records
- `daily_heat_index_forecast_update.yml`: Runs daily to generate future heat index predictions
- `daily_weather_insights.yml`: Runs daily to generate weather insights
- `heat_index_notifications.yml`: Runs after hourly weather update to send notifications

## Troubleshooting

### Common Issues

#### Firebase Authentication Issues

- **Issue**: Unable to authenticate with Firebase
- **Solution**:
  - Verify API keys in `.env` file
  - Check Firebase console for authentication providers
  - Ensure email/password authentication is enabled

#### Python Script Errors

- **Issue**: ModuleNotFoundError
- **Solution**:
  - Ensure virtual environment is activated
  - Verify all dependencies are installed: `pip install -r requirements.txt`
  - Check the Python path

#### Svelte Build Issues

- **Issue**: Build fails with component errors
- **Solution**:
  - Check for syntax errors in Svelte components
  - Verify component props and types
  - Run `npm run lint` to identify issues

### Debugging

#### Frontend Debugging

1. Use browser developer tools (F12)
2. Check the console for errors
3. Use the Network tab to inspect API calls
4. Add `console.log()` statements for debugging

#### Backend Debugging

1. Use logging in Python scripts

   ```python
   import logging
   logging.info("Debug information")
   ```

2. Check script logs in `src/scripts/logs/`

3. Use Python debugger
   ```python
   import pdb
   pdb.set_trace()  # Add breakpoint
   ```

## Performance Optimization

### Frontend Optimization

1. **Code Splitting**

   - Use dynamic imports for large components
   - Split vendor and application code

2. **Asset Optimization**

   - Optimize images using WebP format
   - Use SVG for icons where possible

3. **Runtime Performance**
   - Avoid unnecessary reactivity
   - Use `keyed each` blocks
   - Limit DOM updates

### Backend Optimization

1. **Database Queries**

   - Use indexing for frequently queried fields
   - Limit query results
   - Use batched operations

2. **API Performance**
   - Implement caching for expensive operations
   - Use compression for response data
   - Optimize payload size

## Contributing

We welcome contributions to INET-READY! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

Please follow the code standards and workflows described in this document.

## Resources

### Documentation

- [Svelte Documentation](https://svelte.dev/docs)
- [SvelteKit Documentation](https://kit.svelte.dev/docs)
- [Firebase Documentation](https://firebase.google.com/docs)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

### Tools

- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)
- [Vite](https://vitejs.dev/)
- [Playwright](https://playwright.dev/)
- [Jest](https://jestjs.io/)
- [pytest](https://docs.pytest.org/)
