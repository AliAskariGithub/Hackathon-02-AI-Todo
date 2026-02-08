import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_session():
    """Mock database session for testing"""
    session = AsyncMock()
    session.add = lambda x: None
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = lambda x: None
    return session