# Testing Guide

This directory contains unit and integration tests for PolicyBot.

## Running Tests

### Install test dependencies
```bash
pip install -r requirements.txt
```

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_api.py
pytest tests/test_auth.py
```

### Run specific test function
```bash
pytest tests/test_api.py::test_health_check
pytest tests/test_auth.py::test_create_access_token
```

### Run with coverage report
```bash
pytest tests/ --cov=src --cov-report=html
```

## Test Structure

- **test_auth.py**: Unit tests for JWT token generation and validation
  - Token creation
  - Token signature validation
  - Subject encoding

- **test_api.py**: Integration tests for FastAPI endpoints
  - Health check endpoint
  - Token generation endpoint
  - Protected `/ask` endpoint with authentication
  - Token validation and rejection
  - User tracking in requests

## Test Coverage

Current tests cover:
- ✅ Authentication and authorization
- ✅ API endpoints (public and protected)
- ✅ Token generation with different users
- ✅ Invalid token rejection
- ✅ RAG query functionality with auth

## Future Test Improvements

- [ ] RAG pipeline accuracy tests
- [ ] Performance/load tests
- [ ] Error handling edge cases
- [ ] Database/index availability tests
