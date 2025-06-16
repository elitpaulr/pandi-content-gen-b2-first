# Test Suite for B2 First Content Generation Tool

This directory contains the minimal system tests for the B2 First content generation prototype.

## Test Structure

### 📁 Test Files

- **`test_smoke.py`** - Quick smoke tests to verify basic functionality
- **`test_system_core.py`** - Core system tests for end-to-end functionality  
- **`test_services.py`** - Tests for service layer components
- **`conftest.py`** - Pytest configuration and fixtures

### 🏷️ Test Categories

Tests are organized by markers:

- **`@pytest.mark.unit`** - Fast unit tests, no external dependencies
- **`@pytest.mark.integration`** - Integration tests, requires Ollama connection
- **`@pytest.mark.system`** - End-to-end system tests
- **`@pytest.mark.slow`** - Tests that take longer to run (>30 seconds)

## Running Tests

### Quick Start

```bash
# Install test dependencies
pip install pytest pytest-timeout

# Run smoke tests (fastest)
python run_tests.py smoke

# Run all fast tests
python run_tests.py fast
```

### Test Types

| Command | Description | Requirements | Duration |
|---------|-------------|--------------|----------|
| `python run_tests.py smoke` | Basic functionality | None | ~10s |
| `python run_tests.py unit` | Unit tests only | None | ~30s |
| `python run_tests.py integration` | Integration tests | Ollama running | ~60s |
| `python run_tests.py system` | Full system tests | Ollama + models | ~5min |
| `python run_tests.py fast` | All except slow tests | Ollama running | ~2min |
| `python run_tests.py all` | Complete test suite | Ollama + models | ~10min |

### Direct pytest Usage

```bash
# Run specific test file
pytest tests/test_smoke.py -v

# Run tests by marker
pytest tests/ -m unit -v
pytest tests/ -m "not slow" -v

# Run with timeout for slow tests
pytest tests/ -m system --timeout=600 -v
```

## Test Requirements

### Minimal Requirements (Smoke/Unit Tests)
- Python 3.10+
- pytest
- Project dependencies installed

### Full Requirements (Integration/System Tests)
- Ollama service running (`ollama serve`)
- At least one model available (`ollama pull llama3.1:8b`)
- Network connectivity to localhost:11434

## Test Coverage

### ✅ What's Tested

**Core Functionality:**
- End-to-end task generation pipeline
- JSON parsing and validation
- File I/O operations
- Service layer integration
- Basic error handling

**System Integration:**
- Ollama connection and model availability
- Task generation with real LLM
- File saving and loading
- Configuration loading

**Service Layer:**
- ConfigService: topic sets, text types, guidelines
- TaskService: QA status, validation, file operations
- UIComponents: method availability and structure

### ❌ What's NOT Tested (Future Improvements)

- Streamlit UI components (requires browser testing)
- Batch generation edge cases
- Network failure scenarios
- Large-scale performance testing
- Cross-platform compatibility
- Memory usage under load

## Test Data

Tests use:
- **Fixtures** in `conftest.py` for reusable test data
- **Temporary directories** for file operations
- **Sample task data** that matches B2 First requirements
- **Mock objects** where appropriate

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure you're in the project root
cd /path/to/pandi-content-gen-b2-first

# Install dependencies
pip install -r requirements.txt
```

**Ollama Connection Failures:**
```bash
# Start Ollama service
ollama serve

# Verify models are available
ollama list

# Pull required model if missing
ollama pull llama3.1:8b
```

**Test Timeouts:**
```bash
# Increase timeout for slow tests
pytest tests/ -m system --timeout=900 -v
```

### Test Environment

Tests automatically:
- Add required paths to `sys.path`
- Create temporary directories for file operations
- Clean up test artifacts
- Skip tests when dependencies are unavailable

## Adding New Tests

### Guidelines

1. **Use appropriate markers** (`@pytest.mark.unit`, etc.)
2. **Follow naming convention** (`test_*.py` files, `test_*` functions)
3. **Use fixtures** from `conftest.py` for common setup
4. **Clean up** any created files or state
5. **Add docstrings** explaining what each test verifies

### Example Test

```python
@pytest.mark.unit
def test_new_functionality(sample_task_data):
    """Test description of what this verifies"""
    # Given
    input_data = sample_task_data
    
    # When
    result = function_under_test(input_data)
    
    # Then
    assert result is not None
    assert result.meets_expectations()
```

## Performance Benchmarks

The system tests include basic performance benchmarks:

- **Task Generation**: Should complete in <180 seconds
- **Text Length**: 400-800 words per task
- **Question Count**: 5-6 questions per task
- **File I/O**: Save/load operations should be <1 second

## Continuous Integration

For CI/CD integration:

```bash
# Fast tests for PR validation
python run_tests.py fast

# Full tests for release validation  
python run_tests.py all
```

## Future Enhancements

Potential test improvements:
- Browser-based UI testing with Selenium
- Load testing for batch generation
- Cross-platform testing (Windows, macOS, Linux)
- Performance regression testing
- API contract testing
- Security testing for input validation 