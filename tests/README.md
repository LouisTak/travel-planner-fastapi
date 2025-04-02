# Travel Planner API Test Suite

This directory contains comprehensive tests for the Travel Planner API.

## Test Structure

- `conftest.py`: Common fixtures used across tests
- `unit/`: Unit tests for individual components
  - `controllers/`: Tests for controller functions
  - `middleware/`: Tests for middleware components, including JWT auth
  - `repositories/`: Tests for database repository functions
  - `schemas/`: Tests for validation schemas
  - `dependencies/`: Tests for dependency functions
- `integration/`: Integration tests
  - `test_*_api.py`: Tests for API endpoints
  - `test_jwt_middleware.py`: Tests for the JWT middleware in an integration context
- `fixtures/`: Test fixtures (if needed)

## Running Tests

You can use the provided script to run tests with various options:

```bash
# Run all tests
./scripts/run_tests.sh

# Run only unit tests
./scripts/run_tests.sh -u

# Run only integration tests
./scripts/run_tests.sh -i

# Run only API tests
./scripts/run_tests.sh -a

# Run only middleware tests
./scripts/run_tests.sh -m

# Run only repository tests
./scripts/run_tests.sh -r

# Run with coverage report
./scripts/run_tests.sh -c

# Run with verbose output
./scripts/run_tests.sh -v

# Combine options
./scripts/run_tests.sh -u -c -v
```

## Setting up for Testing

1. Install the test requirements:
   ```bash
   pip install -r requirements-test.txt
   ```

2. Make sure the application is properly configured for testing:
   - The tests automatically set `TESTING=1` in the environment
   - Test database connection is configured in the test fixtures
   
## Adding New Tests

1. Place unit tests in the appropriate subdirectory under `unit/`
2. Place integration tests in the `integration/` directory
3. Use the existing fixtures in `conftest.py` whenever possible
4. Follow the naming conventions:
   - Test files: `test_*.py`
   - Test functions: `test_*`
   
## Test Coverage

Run tests with coverage to generate a coverage report:

```bash
./scripts/run_tests.sh -c
```

This will generate:
- Terminal output with coverage statistics
- HTML coverage report in `htmlcov/index.html`

## Debugging Tests

For better debugging:

1. Run with verbose output:
   ```bash
   ./scripts/run_tests.sh -v
   ```

2. Add the `-s` flag to see print statements:
   ```bash
   python -m pytest -s tests/path/to/test.py
   ```

3. Use pytest breakpoints with `pytest.set_trace()`

## Common Test Fixtures

- `mock_db`: MockDB session
- `mock_user`: Mock user object
- `mock_travel_plan`: Mock travel plan
- `auth_token`: Valid authentication token
- `auth_headers`: HTTP headers with valid auth token
- `admin_headers`: HTTP headers with admin auth token
- `expired_headers`: HTTP headers with expired token 