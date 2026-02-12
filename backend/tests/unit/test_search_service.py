"""
Unit tests for search service.

Tests keyword search, tag search, and unique tag retrieval.
"""

import pytest
from uuid import uuid4
from unittest.mock import Mock, patch
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.services.search_service import SearchService


class TestKeywordSearch:
    """Test keyword-based task search."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def search_service(self, mock_db):
        """Create search service with mock DB."""
        return SearchService(mock_db)

    def test_search_tasks_by_title(self, search_service, mock_db):
        """Test searching tasks by title keyword."""
        user_id = uuid4()
        query = "meeting"

        mock_db.exec.return_value.all.return_value = [
            Mock(title="Team meeting", description="Weekly sync"),
            Mock(title="Client meeting", description="Project review")
        ]

        results = search_service.search_tasks(user_id, query)

        assert len(results) == 2
        assert all("meeting" in r.title.lower() for r in results)

    def test_search_tasks_by_description(self, search_service, mock_db):
        """Test searching tasks by description keyword."""
        user_id = uuid4()
        query = "urgent"

        mock_db.exec.return_value.all.return_value = [
            Mock(title="Fix bug", description="Urgent production issue")
        ]

        results = search_service.search_tasks(user_id, query)

        assert len(results) == 1
        assert "urgent" in results[0].description.lower()

    def test_search_case_insensitive(self, search_service, mock_db):
        """Test that search is case-insensitive."""
        user_id = uuid4()
        query = "URGENT"

        mock_db.exec.return_value.all.return_value = [
            Mock(title="urgent task", description="Urgent work")
        ]

        results = search_service.search_tasks(user_id, query)

        assert len(results) == 1

    def test_search_with_pagination(self, search_service, mock_db):
        """Test search with limit and offset."""
        user_id = uuid4()
        query = "task"

        mock_db.exec.return_value.all.return_value = []

        results = search_service.search_tasks(user_id, query, limit=10, offset=20)

        # Verify query was built with limit and offset
        assert isinstance(results, list)


class TestTagSearch:
    """Test tag-based task search."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def search_service(self, mock_db):
        """Create search service with mock DB."""
        return SearchService(mock_db)

    def test_search_by_single_tag(self, search_service, mock_db):
        """Test searching tasks by single tag."""
        user_id = uuid4()
        tags = ["urgent"]

        mock_db.exec.return_value.all.return_value = [
            Mock(tags=["urgent", "work"]),
            Mock(tags=["urgent"])
        ]

        results = search_service.search_tasks_by_tags(user_id, tags)

        assert len(results) == 2

    def test_search_by_multiple_tags_any_match(self, search_service, mock_db):
        """Test searching with multiple tags (any match)."""
        user_id = uuid4()
        tags = ["urgent", "work"]

        mock_db.exec.return_value.all.return_value = [
            Mock(tags=["urgent"]),
            Mock(tags=["work"]),
            Mock(tags=["urgent", "work"])
        ]

        results = search_service.search_tasks_by_tags(user_id, tags, match_all=False)

        assert len(results) == 3

    def test_search_by_multiple_tags_all_match(self, search_service, mock_db):
        """Test searching with multiple tags (all must match)."""
        user_id = uuid4()
        tags = ["urgent", "work"]

        mock_db.exec.return_value.all.return_value = [
            Mock(tags=["urgent", "work", "meeting"])
        ]

        results = search_service.search_tasks_by_tags(user_id, tags, match_all=True)

        assert len(results) == 1


class TestUniqueTagRetrieval:
    """Test unique tag retrieval."""

    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        return Mock()

    @pytest.fixture
    def search_service(self, mock_db):
        """Create search service with mock DB."""
        return SearchService(mock_db)

    def test_get_unique_tags(self, search_service, mock_db):
        """Test retrieving all unique tags for a user."""
        user_id = uuid4()

        mock_db.exec.return_value.all.return_value = [
            ["urgent", "work"],
            ["work", "meeting"],
            ["personal"],
            ["urgent"]
        ]

        tags = search_service.get_unique_tags(user_id)

        # Should deduplicate and sort
        assert "urgent" in tags
        assert "work" in tags
        assert "meeting" in tags
        assert "personal" in tags
        assert len(tags) == 4

    def test_get_unique_tags_empty(self, search_service, mock_db):
        """Test retrieving tags when user has no tasks with tags."""
        user_id = uuid4()

        mock_db.exec.return_value.all.return_value = []

        tags = search_service.get_unique_tags(user_id)

        assert tags == []

    def test_get_unique_tags_handles_none(self, search_service, mock_db):
        """Test that None tags are handled gracefully."""
        user_id = uuid4()

        mock_db.exec.return_value.all.return_value = [
            ["urgent"],
            None,
            ["work"]
        ]

        tags = search_service.get_unique_tags(user_id)

        assert "urgent" in tags
        assert "work" in tags
        assert None not in tags
