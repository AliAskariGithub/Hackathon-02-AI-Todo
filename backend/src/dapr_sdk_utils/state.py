"""
Dapr State API Utility Functions

This module provides utility functions for interacting with Dapr State Store.
It abstracts direct database access and enables cloud-agnostic data persistence.

Key Features:
- Save/retrieve state with automatic serialization
- Bulk operations for performance
- State query support
- Transaction support
- TTL (Time-To-Live) for temporary data
"""

from typing import Any, Dict, List, Optional, TypeVar, Generic
from uuid import UUID
from dapr.clients import DaprClient
from dapr.clients.grpc._state import StateItem, StateOptions
import json
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class DaprStateStore:
    """
    Wrapper for Dapr State Store operations.

    Provides type-safe, async-compatible methods for state management.
    """

    def __init__(self, store_name: str = "statestore"):
        """
        Initialize Dapr State Store client.

        Args:
            store_name: Name of the Dapr State Store component (default: "statestore")
        """
        self.store_name = store_name
        self.client = DaprClient()

    def save_state(
        self,
        key: str,
        value: Any,
        etag: Optional[str] = None,
        options: Optional[StateOptions] = None
    ) -> None:
        """
        Save state to Dapr State Store.

        Args:
            key: State key (e.g., "task:user-id:task-id")
            value: State value (will be JSON serialized)
            etag: Optional ETag for optimistic concurrency
            options: Optional state options (consistency, concurrency)

        Example:
            >>> store = DaprStateStore()
            >>> store.save_state("task:123:456", {"title": "Buy groceries"})
        """
        # Serialize Pydantic models to dict
        if isinstance(value, BaseModel):
            value = value.model_dump()

        self.client.save_state(
            store_name=self.store_name,
            key=key,
            value=json.dumps(value),
            etag=etag,
            options=options
        )

    def get_state(
        self,
        key: str,
        model_class: Optional[type[T]] = None
    ) -> Optional[T | Dict[str, Any]]:
        """
        Retrieve state from Dapr State Store.

        Args:
            key: State key
            model_class: Optional Pydantic model class for deserialization

        Returns:
            State value (deserialized to model_class if provided, else dict)
            Returns None if key doesn't exist

        Example:
            >>> store = DaprStateStore()
            >>> task = store.get_state("task:123:456", Task)
        """
        state_response = self.client.get_state(
            store_name=self.store_name,
            key=key
        )

        if not state_response.data:
            return None

        data = json.loads(state_response.data)

        if model_class:
            return model_class(**data)
        return data

    def delete_state(
        self,
        key: str,
        etag: Optional[str] = None,
        options: Optional[StateOptions] = None
    ) -> None:
        """
        Delete state from Dapr State Store.

        Args:
            key: State key to delete
            etag: Optional ETag for optimistic concurrency
            options: Optional state options

        Example:
            >>> store = DaprStateStore()
            >>> store.delete_state("task:123:456")
        """
        self.client.delete_state(
            store_name=self.store_name,
            key=key,
            etag=etag,
            options=options
        )

    def save_bulk_state(
        self,
        states: List[tuple[str, Any]]
    ) -> None:
        """
        Save multiple states in a single operation (bulk save).

        Args:
            states: List of (key, value) tuples

        Example:
            >>> store = DaprStateStore()
            >>> store.save_bulk_state([
            ...     ("task:123:456", {"title": "Task 1"}),
            ...     ("task:123:789", {"title": "Task 2"})
            ... ])
        """
        state_items = []
        for key, value in states:
            if isinstance(value, BaseModel):
                value = value.model_dump()

            state_items.append(StateItem(
                key=key,
                value=json.dumps(value)
            ))

        self.client.save_bulk_state(
            store_name=self.store_name,
            states=state_items
        )

    def get_bulk_state(
        self,
        keys: List[str],
        model_class: Optional[type[T]] = None
    ) -> Dict[str, Optional[T | Dict[str, Any]]]:
        """
        Retrieve multiple states in a single operation (bulk get).

        Args:
            keys: List of state keys
            model_class: Optional Pydantic model class for deserialization

        Returns:
            Dictionary mapping keys to values

        Example:
            >>> store = DaprStateStore()
            >>> tasks = store.get_bulk_state(["task:123:456", "task:123:789"], Task)
        """
        bulk_response = self.client.get_bulk_state(
            store_name=self.store_name,
            keys=keys
        )

        result = {}
        for item in bulk_response.items:
            if item.data:
                data = json.loads(item.data)
                if model_class:
                    result[item.key] = model_class(**data)
                else:
                    result[item.key] = data
            else:
                result[item.key] = None

        return result

    def query_state(
        self,
        query: Dict[str, Any],
        model_class: Optional[type[T]] = None
    ) -> List[T | Dict[str, Any]]:
        """
        Query state using Dapr State Query API.

        Args:
            query: Query specification (filter, sort, pagination)
            model_class: Optional Pydantic model class for deserialization

        Returns:
            List of matching state values

        Example:
            >>> store = DaprStateStore()
            >>> query = {
            ...     "filter": {
            ...         "EQ": {"status": "pending"}
            ...     },
            ...     "sort": [{"key": "created_at", "order": "DESC"}],
            ...     "page": {"limit": 10}
            ... }
            >>> tasks = store.query_state(query, Task)
        """
        query_response = self.client.query_state(
            store_name=self.store_name,
            query=json.dumps(query)
        )

        results = []
        for item in query_response.results:
            data = json.loads(item.value)
            if model_class:
                results.append(model_class(**data))
            else:
                results.append(data)

        return results


# Key pattern helpers for consistent state key naming
def task_key(user_id: UUID, task_id: UUID) -> str:
    """Generate state key for a task."""
    return f"task:{user_id}:{task_id}"


def user_tasks_key(user_id: UUID) -> str:
    """Generate state key for user's task list."""
    return f"tasks:user:{user_id}"


def user_tasks_by_status_key(user_id: UUID, status: str) -> str:
    """Generate state key for user's tasks filtered by status."""
    return f"tasks:user:{user_id}:status:{status}"


def reminder_key(user_id: UUID, reminder_id: UUID) -> str:
    """Generate state key for a reminder."""
    return f"reminder:{user_id}:{reminder_id}"


def correlation_id_key(correlation_id: UUID) -> str:
    """Generate state key for correlation ID tracking (idempotency)."""
    return f"correlation:{correlation_id}"
