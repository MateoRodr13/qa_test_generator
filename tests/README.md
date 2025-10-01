# QA Test Generator - Test Suite

This directory contains comprehensive tests for the QA Test Generator application.

## Test Structure

```
tests/
├── unit/                    # Unit tests for individual components
│   ├── test_output_handler.py    # Tests for file saving functions
│   ├── test_workflow_manager.py  # Tests for workflow orchestration
│   ├── test_ai_generator.py      # Tests for AI prompt generation
│   └── test_prompts.py          # Tests for prompt templates
├── integration/             # Integration tests for component interaction
│   └── test_workflow_integration.py
├── e2e/                     # End-to-end tests for complete workflows
│   └── test_full_workflow.py
├── README.md               # This file
└── __init__.py
```

## Running Tests

### Prerequisites
- Python 3.8+
- Virtual environment with dependencies installed
- pytest installed (`pip install pytest`)

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# End-to-end tests only
pytest tests/e2e/

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_output_handler.py

# Run specific test method
pytest tests/unit/test_output_handler.py::TestSaveCasesToJSON::test_save_bilingual_json
```

## Test Coverage

### Unit Tests (`tests/unit/`)

1. **test_output_handler.py**
   - CSV and JSON file saving functionality
   - Bilingual output handling
   - Error handling for invalid data

2. **test_workflow_manager.py**
   - Workflow state management
   - Component initialization
   - Error handling and recovery

3. **test_ai_generator.py**
   - Prompt building for user stories and test cases
   - AI agent interaction mocking
   - Response validation

4. **test_prompts.py** (existing)
   - Prompt template validation
   - Parameter checking
   - Output format validation

### Integration Tests (`tests/integration/`)

1. **test_workflow_integration.py**
   - Data flow between workflow components
   - Context persistence across operations
   - File naming and path handling

### End-to-End Tests (`tests/e2e/`)

1. **test_full_workflow.py**
   - Complete application workflow testing
   - Output file structure validation
   - Error handling in full execution context

## Key Test Features

### Mocking Strategy
- AI API calls are mocked to avoid external dependencies
- File system operations use temporary directories
- CLI interactions are mocked for consistent testing

### Test Data
- Realistic test data mimicking actual user stories and test cases
- Bilingual content (English/Spanish) testing
- Edge cases and error conditions

### Assertions
- File existence and content validation
- Data structure integrity
- Error handling verification
- Workflow state transitions

## Adding New Tests

### Unit Tests
1. Create test file in `tests/unit/`
2. Use descriptive class and method names
3. Mock external dependencies
4. Test both success and failure scenarios

### Integration Tests
1. Test interaction between multiple components
2. Use realistic data flows
3. Verify data persistence across operations

### E2E Tests
1. Test complete user workflows
2. Mock user interactions
3. Validate final output structure

## Test Configuration

Configuration is in `pytest.ini`:
- Test discovery patterns
- Markers for test categorization
- Warning filters
- Output formatting

## Continuous Integration

Tests are designed to run in CI/CD environments with:
- No external API dependencies (all mocked)
- Isolated file system operations
- Deterministic test execution