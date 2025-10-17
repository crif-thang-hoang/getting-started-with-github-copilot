# Tests for High School Management System API

This directory contains comprehensive tests for the FastAPI backend of the Mergington High School Activities Management System.

## Test Structure

### Files

- **`conftest.py`**: Pytest configuration and fixtures
  - `client`: TestClient fixture for making API requests
  - `reset_activities`: Fixture to reset activity data before/after each test

- **`test_api.py`**: Main test suite with 18 tests organized into classes:
  - `TestRootEndpoint`: Tests for root redirect
  - `TestGetActivities`: Tests for listing activities
  - `TestSignupForActivity`: Tests for student signup
  - `TestUnregisterFromActivity`: Tests for student unregistration
  - `TestActivityManagement`: Integration tests

## Running Tests

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run with Coverage

```bash
pytest tests/ -v --cov=src --cov-report=term-missing
```

### Run Specific Test Class

```bash
pytest tests/test_api.py::TestSignupForActivity -v
```

### Run Specific Test

```bash
pytest tests/test_api.py::TestSignupForActivity::test_signup_for_existing_activity_success -v
```

## Test Coverage

Current test coverage: **100%** of `src/app.py`

## Test Scenarios Covered

### Root Endpoint
- ✅ Redirects to static index.html

### GET /activities
- ✅ Returns 200 OK status
- ✅ Returns dictionary of activities
- ✅ Contains all expected activities
- ✅ Each activity has required fields
- ✅ Participants field is a list

### POST /activities/{activity_name}/signup
- ✅ Successful signup for existing activity
- ✅ Participant is actually added
- ✅ 404 error for non-existent activity
- ✅ 400 error for duplicate signup
- ✅ Multiple students can sign up

### DELETE /activities/{activity_name}/unregister
- ✅ Successful unregistration of existing participant
- ✅ Participant is actually removed
- ✅ 404 error for non-existent activity
- ✅ 404 error for non-participant
- ✅ Complete signup and unregister workflow

### Integration Tests
- ✅ Operations on different activities are independent
- ✅ Participant counts are accurate

## Continuous Integration

These tests can be integrated into CI/CD pipelines using GitHub Actions, GitLab CI, or other CI systems.

Example GitHub Actions workflow:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -v --cov=src
```
