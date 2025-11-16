# PAuth Tests

This directory contains the test suite for PAuth.

## Running Tests

### Run all tests:
```bash
python -m unittest discover src/tests
```

### Run specific test file:
```bash
python -m unittest src.tests.test_oauth2_client
python -m unittest src.tests.test_storage
python -m unittest src.tests.test_models
```

### Run with coverage (requires coverage.py):
```bash
pip install coverage
coverage run -m unittest discover src/tests
coverage report
coverage html  # Generate HTML report
```

## Test Structure

- `test_oauth2_client.py` - Tests for the main OAuth2Client class
- `test_storage.py` - Tests for token storage backends
- `test_models.py` - Tests for data models (TokenResponse, UserInfo, Providers)

## Adding New Tests

When adding new tests:

1. Create a new test file following the naming convention `test_*.py`
2. Import unittest and the modules to test
3. Create test classes inheriting from `unittest.TestCase`
4. Name test methods starting with `test_`
5. Use descriptive docstrings
6. Clean up resources in `tearDown()` if needed

Example:
```python
import unittest
from src.your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.instance = YourClass()

    def test_your_feature(self):
        """Test description."""
        result = self.instance.method()
        self.assertEqual(result, expected_value)
```

## CI/CD

These tests should be run automatically in your CI/CD pipeline before deploying or merging code.
