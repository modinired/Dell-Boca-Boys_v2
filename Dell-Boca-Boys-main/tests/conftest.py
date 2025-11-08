"""
Pytest configuration and fixtures for Dell Boca Boys V2 Test Suite.
Provides comprehensive test fixtures for all components.
"""
import pytest
import asyncio
import os
import tempfile
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Set test environment
os.environ['TESTING'] = 'true'
os.environ['PGDATABASE'] = 'test_dell_boca_boys'
os.environ['REDIS_DB'] = '15'  # Use separate Redis DB for testing


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_session():
    """Provide async session for async tests."""
    return asyncio.get_event_loop()


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine."""
    from sqlalchemy import create_engine
    engine = create_engine(
        f"postgresql://{os.getenv('PGUSER', 'n8n_agent')}:"
        f"{os.getenv('PGPASSWORD', 'test_password')}@"
        f"{os.getenv('PGHOST', 'localhost')}:5432/"
        f"{os.getenv('PGDATABASE', 'test_dell_boca_boys')}",
        echo=False
    )
    return engine


@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Provide database session with automatic rollback."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=test_db_engine)
    session = Session()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def redis_client():
    """Provide Redis client for testing."""
    client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 15)),
        decode_responses=True
    )

    # Clear test database before each test
    client.flushdb()

    yield client

    # Clean up after test
    client.flushdb()
    client.close()


@pytest.fixture(scope="function")
def mock_ollama():
    """Mock Ollama API client."""
    mock = Mock()
    mock.generate = AsyncMock(return_value={
        "response": "Test response from Ollama",
        "model": "qwen2.5-coder:7b",
        "created_at": datetime.utcnow().isoformat(),
        "done": True
    })
    return mock


@pytest.fixture(scope="function")
def mock_gemini():
    """Mock Google Gemini API client."""
    mock = Mock()
    mock.generate_content = AsyncMock(return_value=Mock(
        text="Test response from Gemini",
        candidates=[Mock(content=Mock(parts=[Mock(text="Test response from Gemini")]))],
        finish_reason="STOP"
    ))
    return mock


@pytest.fixture(scope="function")
def mock_mem0_client():
    """Mock Mem0 memory client."""
    mock = Mock()
    mock.add = AsyncMock(return_value={"id": "test_memory_id"})
    mock.search = AsyncMock(return_value=[
        {
            "id": "test_memory_1",
            "memory": '{"content": "test memory 1"}',
            "score": 0.95
        }
    ])
    mock.get = AsyncMock(return_value={
        "id": "test_memory_id",
        "memory": '{"content": "test memory"}',
        "metadata": {}
    })
    return mock


@pytest.fixture(scope="function")
def sample_workflow():
    """Provide sample workflow JSON for testing."""
    return {
        "id": "test_workflow_001",
        "name": "Test Workflow",
        "nodes": [
            {
                "id": "webhook",
                "type": "n8n-nodes-base.webhook",
                "position": [250, 300],
                "parameters": {
                    "path": "test-webhook",
                    "method": "POST"
                }
            },
            {
                "id": "transform",
                "type": "n8n-nodes-base.function",
                "position": [450, 300],
                "parameters": {
                    "functionCode": "return items;"
                }
            }
        ],
        "connections": {
            "webhook": {
                "main": [[{"node": "transform", "type": "main", "index": 0}]]
            }
        },
        "active": False,
        "settings": {},
        "tags": []
    }


@pytest.fixture(scope="function")
def sample_memory_entry():
    """Provide sample memory entry for testing."""
    from core.memory.google_sheets_memory_manager import MemoryEntry, MemoryType
    return MemoryEntry(
        memory_id="test_mem_001",
        memory_type=MemoryType.AGENT_COMMUNICATION,
        agent_id="test_agent_001",
        content={"message": "Test communication", "action": "test_action"},
        metadata={"source": "test", "priority": "high"},
        timestamp=datetime.utcnow(),
        importance_score=0.8,
        access_count=0,
        last_accessed=None,
        retention_period=None
    )


@pytest.fixture(scope="function")
def temp_workspace():
    """Provide temporary workspace directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture(scope="function")
def mock_n8n_api():
    """Mock n8n API client."""
    mock = Mock()
    mock.get_workflows = AsyncMock(return_value=[
        {"id": "1", "name": "Test Workflow 1", "active": True}
    ])
    mock.create_workflow = AsyncMock(return_value={"id": "new_workflow_id"})
    mock.execute_workflow = AsyncMock(return_value={"executionId": "exec_001"})
    return mock


@pytest.fixture(scope="function")
def cesar_agent_config():
    """Provide CESAR agent configuration."""
    return {
        "agent_id": "test_agent",
        "agent_type": "terry_delmonaco",
        "llm_config": {
            "provider": "ollama",
            "model": "qwen2.5-coder:7b",
            "temperature": 0.7
        },
        "memory_config": {
            "provider": "mem0",
            "cache_enabled": True
        }
    }


@pytest.fixture(scope="function")
def collective_intelligence_config():
    """Provide collective intelligence framework configuration."""
    return {
        "emergence_threshold": 0.7,
        "stability_requirement": 0.6,
        "minimum_participants": 3,
        "insight_confidence_threshold": 0.75,
        "trust_decay_rate": 0.05,
        "collaboration_bonus": 0.2,
        "max_swarm_iterations": 10,
        "max_learning_rounds": 5
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset singleton instances between tests."""
    # Clear any global state or singletons
    from core.cache.redis_cache import cache_client
    global cache_client
    cache_client = None

    yield

    # Clean up after test
    cache_client = None


# Markers for different test categories
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_redis: mark test as requiring Redis"
    )
    config.addinivalue_line(
        "markers", "requires_postgres: mark test as requiring PostgreSQL"
    )
    config.addinivalue_line(
        "markers", "requires_llm: mark test as requiring LLM access"
    )
