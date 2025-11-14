#!/usr/bin/env python3
"""
Test Generator Agent

This Claude subagent generates comprehensive unit tests for the entire pipeline.

The agent will:
1. Analyze the codebase
2. Identify all testable components
3. Generate unit tests with good coverage
4. Create integration tests for end-to-end flows
5. Generate test data fixtures
"""


def create_test_generation_prompt(component: str, code_file: str) -> str:
    """
    Creates prompt for Claude agent to generate tests

    The agent will analyze the code and create comprehensive tests
    """

    return f"""
You are a Test Generation Agent creating comprehensive unit tests.

## Component to Test:

**{component}**

File: `{code_file}`

## Your Mission:

Generate comprehensive pytest unit tests that ensure this component works correctly.

### 1. Analyze the Code

Read the code file and identify:
- All public methods/functions
- Edge cases and error conditions
- Dependencies and mocks needed
- Integration points with other systems

### 2. Create Test Cases

For each method, create tests for:
- **Happy path** - Normal usage
- **Edge cases** - Boundary conditions
- **Error handling** - Invalid inputs, exceptions
- **Integration** - Interaction with dependencies

### 3. Generate Test Code

Write pytest tests with:
- Clear test names (test_method_name_should_behavior_when_condition)
- Good test data (fixtures, parametrize)
- Proper mocking (unittest.mock or pytest fixtures)
- Assertions that verify behavior
- Comments explaining complex test logic

### 4. Coverage Goals

Aim for:
- 100% of public methods tested
- All error paths covered
- Integration tests for critical flows
- Performance tests if relevant

## Output Format:

```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from {component} import ClassName

# Fixtures
@pytest.fixture
def mock_dependency():
    '''Fixture for mocking dependencies'''
    return Mock()

# Unit Tests
class TestClassName:
    '''Tests for ClassName'''

    def test_method_should_succeed_when_valid_input(self, mock_dependency):
        '''Test that method succeeds with valid input'''
        # Arrange
        instance = ClassName(dependency=mock_dependency)
        valid_input = "test_data"

        # Act
        result = instance.method(valid_input)

        # Assert
        assert result == expected_value
        mock_dependency.some_call.assert_called_once()

    def test_method_should_raise_error_when_invalid_input(self):
        '''Test that method raises ValueError for invalid input'''
        # Arrange
        instance = ClassName()
        invalid_input = None

        # Act & Assert
        with pytest.raises(ValueError, match="Input cannot be None"):
            instance.method(invalid_input)

    @pytest.mark.parametrize("input,expected", [
        ("case1", "result1"),
        ("case2", "result2"),
        ("edge_case", "edge_result"),
    ])
    def test_method_handles_various_inputs(self, input, expected):
        '''Test method with various inputs'''
        # Arrange
        instance = ClassName()

        # Act
        result = instance.method(input)

        # Assert
        assert result == expected

# Integration Tests
class TestClassNameIntegration:
    '''Integration tests for ClassName'''

    @pytest.mark.asyncio
    async def test_full_workflow_end_to_end(self):
        '''Test complete workflow from start to finish'''
        # Arrange
        instance = ClassName()

        # Act
        result = await instance.full_workflow()

        # Assert
        assert result is not None
        assert result.status == "completed"

# Performance Tests (if relevant)
class TestClassNamePerformance:
    '''Performance tests'''

    def test_method_completes_within_timeout(self):
        '''Test that method completes in reasonable time'''
        import time
        instance = ClassName()

        start = time.time()
        result = instance.method("data")
        duration = time.time() - start

        assert duration < 1.0, f"Method took {duration}s, expected < 1s"
```

## Special Cases:

### For Database Operations:
```python
@pytest.fixture
def db_connection():
    '''In-memory SQLite for testing'''
    import sqlite3
    conn = sqlite3.connect(':memory:')
    # Set up schema
    yield conn
    conn.close()
```

### For Async Functions:
```python
@pytest.mark.asyncio
async def test_async_method():
    mock_client = AsyncMock()
    result = await method(mock_client)
    assert result is not None
```

### For API Calls:
```python
@patch('module.requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {'data': 'test'}
    result = fetch_data()
    assert result == {'data': 'test'}
```

## Instructions:

1. READ the code file carefully
2. IDENTIFY all testable components
3. CREATE comprehensive test cases
4. GENERATE clean, well-documented pytest code
5. INCLUDE fixtures, mocks, and parametrize where appropriate
6. ENSURE good coverage of happy paths and error cases

Return ONLY the test code - no explanations, just pure pytest code ready to run.
"""


# Test scenarios to generate
TEST_SCENARIOS = [
    {
        "component": "ClaudeOrchestrator",
        "file": "claude_orchestrator.py",
        "priority": "high",
        "focus": [
            "Platform discovery agent spawning",
            "Database save operations (Turso and local)",
            "Configuration loading",
            "Error handling for network failures"
        ]
    },
    {
        "component": "PlatformDiscoveryAgent",
        "file": "agents/platform_discovery_agent.py",
        "priority": "high",
        "focus": [
            "Platform search and validation",
            "Regional platform detection",
            "Data structure parsing"
        ]
    },
    {
        "component": "DeepAnalysisAgent",
        "file": "agents/deep_analysis_agent.py",
        "priority": "medium",
        "focus": [
            "Market sizing calculations",
            "Competitive analysis",
            "Pain signal quantification"
        ]
    },
    {
        "component": "TursoMigration",
        "file": "migrate_to_turso.py",
        "priority": "high",
        "focus": [
            "Schema creation",
            "Data migration",
            "Verification"
        ]
    }
]


def create_integration_test_prompt() -> str:
    """
    Creates prompt for end-to-end integration tests
    """

    return """
You are generating END-TO-END integration tests for the entire pipeline.

## Pipeline to Test:

```
1. Platform Discovery Agent
   ↓
2. Save to Turso Database
   ↓
3. Frontend Queries Turso
   ↓
4. User sees platforms
```

## Integration Test Goals:

Test that the ENTIRE flow works:
1. Agent discovers platform
2. Data is saved to database (Turso or SQLite)
3. Data can be queried back
4. Frontend can render data

## Generate Tests:

```python
import pytest
from claude_orchestrator import ClaudeOrchestrator
import asyncio

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_pipeline_platform_discovery_to_database():
    '''
    Test complete flow: Agent discovers → Saves to DB → Query returns data
    '''
    # Arrange
    orchestrator = ClaudeOrchestrator(use_turso=False)  # Use local for testing

    # Act - Spawn agent to discover platforms for test region
    test_platform = {
        'region': 'TEST_REGION',
        'country': 'TEST',
        'name': 'Test Platform',
        'url': 'https://test.com',
        'type': 'forum',
        'language': 'English',
        'description': 'Test description'
    }

    await orchestrator._save_platform_to_db(test_platform)

    # Assert - Query database to verify save
    # (For local SQLite)
    import sqlite3
    conn = sqlite3.connect(orchestrator.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM local_platforms WHERE name = 'Test Platform'")
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[3] == 'Test Platform'  # name column
    assert result[1] == 'TEST_REGION'  # region column


@pytest.mark.integration
def test_frontend_can_query_database():
    '''Test that frontend query logic works with database'''
    # This would test the query patterns used by explorer_turso.html
    pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_parallel_agent_execution():
    '''Test that multiple agents can run simultaneously'''
    # Spawn 5 agents in parallel
    # Verify all complete successfully
    # Verify all data is saved
    pass
```

Generate comprehensive integration tests covering all critical paths.
"""


if __name__ == "__main__":
    print("Test Generator Agent")
    print("=" * 80)
    print()
    print("This agent generates comprehensive unit and integration tests.")
    print()
    print("To use:")
    print("1. Spawn Claude agent with test generation prompt")
    print("2. Agent analyzes code and generates pytest tests")
    print("3. Save generated tests to tests/test_*.py")
    print("4. Run: pytest tests/")
    print()
    print("Test scenarios defined:")
    for scenario in TEST_SCENARIOS:
        print(f"  • {scenario['component']} ({scenario['priority']} priority)")
