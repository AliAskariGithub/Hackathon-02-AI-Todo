"""
Natural language query parser for chatbot integration.

Extracts filters from natural language queries.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List


class NLPQueryService:
    """Service for parsing natural language queries into filters."""

    # Priority keywords
    PRIORITY_KEYWORDS = {
        'high': ['high', 'urgent', 'important', 'critical', 'asap'],
        'medium': ['medium', 'normal', 'moderate'],
        'low': ['low', 'minor', 'trivial']
    }

    # Status keywords
    STATUS_KEYWORDS = {
        'pending': ['pending', 'todo', 'not started', 'upcoming'],
        'in_progress': ['in progress', 'working on', 'active', 'ongoing'],
        'completed': ['completed', 'done', 'finished', 'complete']
    }

    # Recurrence keywords
    RECURRENCE_KEYWORDS = {
        'Daily': ['daily', 'every day', 'each day'],
        'Weekly': ['weekly', 'every week', 'each week'],
        'Monthly': ['monthly', 'every month', 'each month']
    }

    # Time-related patterns
    TIME_PATTERNS = {
        'today': timedelta(days=0),
        'tomorrow': timedelta(days=1),
        'this week': timedelta(days=7),
        'next week': timedelta(days=14),
        'this month': timedelta(days=30)
    }

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured filters.

        Args:
            query: Natural language query string

        Returns:
            Dictionary of extracted filters

        Examples:
            "show me high priority tasks" -> {"priority": "High"}
            "find completed tasks from today" -> {"status": "completed", "due_after": <today>}
            "urgent tasks due this week" -> {"priority": "High", "due_before": <week_end>}
        """
        query_lower = query.lower()
        filters = {}

        # Extract priority
        priority = self._extract_priority(query_lower)
        if priority:
            filters['priority'] = priority

        # Extract status
        status = self._extract_status(query_lower)
        if status:
            filters['status'] = status

        # Extract recurrence
        recurrence = self._extract_recurrence(query_lower)
        if recurrence:
            filters['recurrence'] = recurrence

        # Extract time constraints
        time_filters = self._extract_time_constraints(query_lower)
        filters.update(time_filters)

        # Extract tags
        tags = self._extract_tags(query_lower)
        if tags:
            filters['tags'] = tags

        # Extract search keywords (remaining words after filter extraction)
        keywords = self._extract_keywords(query_lower, filters)
        if keywords:
            filters['search_query'] = keywords

        return filters

    def _extract_priority(self, query: str) -> Optional[str]:
        """Extract priority from query."""
        for priority, keywords in self.PRIORITY_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                return priority.capitalize()
        return None

    def _extract_status(self, query: str) -> Optional[str]:
        """Extract status from query."""
        for status, keywords in self.STATUS_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                return status
        return None

    def _extract_recurrence(self, query: str) -> Optional[str]:
        """Extract recurrence pattern from query."""
        for recurrence, keywords in self.RECURRENCE_KEYWORDS.items():
            if any(keyword in query for keyword in keywords):
                return recurrence
        return None

    def _extract_time_constraints(self, query: str) -> Dict[str, datetime]:
        """Extract time-based filters from query."""
        filters = {}
        now = datetime.utcnow()

        # Check for "due" keyword
        if 'due' in query:
            for time_phrase, delta in self.TIME_PATTERNS.items():
                if time_phrase in query:
                    if 'before' in query or 'by' in query:
                        filters['due_before'] = now + delta
                    elif 'after' in query:
                        filters['due_after'] = now + delta
                    else:
                        # Default to "due within"
                        filters['due_before'] = now + delta

        # Check for "created" or "updated" keywords
        if 'created' in query or 'added' in query:
            for time_phrase, delta in self.TIME_PATTERNS.items():
                if time_phrase in query:
                    filters['created_after'] = now - delta

        return filters

    def _extract_tags(self, query: str) -> Optional[List[str]]:
        """Extract tags from query."""
        # Look for patterns like "tagged with X" or "tag:X"
        tag_patterns = [
            r'tagged?\s+(?:with\s+)?([a-zA-Z0-9_-]+)',
            r'tag:([a-zA-Z0-9_-]+)',
            r'#([a-zA-Z0-9_-]+)'
        ]

        tags = []
        for pattern in tag_patterns:
            matches = re.findall(pattern, query)
            tags.extend(matches)

        return tags if tags else None

    def _extract_keywords(self, query: str, extracted_filters: Dict[str, Any]) -> Optional[str]:
        """Extract remaining keywords for text search."""
        # Remove filter keywords from query
        remaining = query

        # Remove priority keywords
        for keywords in self.PRIORITY_KEYWORDS.values():
            for keyword in keywords:
                remaining = remaining.replace(keyword, '')

        # Remove status keywords
        for keywords in self.STATUS_KEYWORDS.values():
            for keyword in keywords:
                remaining = remaining.replace(keyword, '')

        # Remove time phrases
        for phrase in self.TIME_PATTERNS.keys():
            remaining = remaining.replace(phrase, '')

        # Remove common words
        common_words = ['show', 'find', 'get', 'list', 'tasks', 'task', 'me', 'my', 'the', 'a', 'an', 'due', 'with']
        for word in common_words:
            remaining = remaining.replace(f' {word} ', ' ')

        # Clean up
        remaining = ' '.join(remaining.split()).strip()

        return remaining if remaining else None

    def generate_query_description(self, filters: Dict[str, Any]) -> str:
        """
        Generate human-readable description of filters.

        Args:
            filters: Dictionary of filters

        Returns:
            Human-readable description
        """
        parts = []

        if filters.get('priority'):
            parts.append(f"{filters['priority']} priority")

        if filters.get('status'):
            parts.append(filters['status'])

        if filters.get('recurrence'):
            parts.append(f"{filters['recurrence']} recurring")

        if filters.get('tags'):
            tags_str = ', '.join(filters['tags'])
            parts.append(f"tagged with {tags_str}")

        if filters.get('due_before'):
            parts.append(f"due before {filters['due_before'].strftime('%Y-%m-%d')}")

        if filters.get('search_query'):
            parts.append(f"matching '{filters['search_query']}'")

        if not parts:
            return "All tasks"

        return "Tasks: " + ", ".join(parts)


def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """
    Convenience function to parse natural language query.

    Args:
        query: Natural language query string

    Returns:
        Dictionary of extracted filters
    """
    service = NLPQueryService()
    return service.parse_query(query)
