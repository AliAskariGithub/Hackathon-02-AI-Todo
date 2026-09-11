"""
Event payload optimization utilities.

Provides functions to minimize event payload size by:
- Removing unnecessary fields
- Compressing large payloads
- Validating payload size limits
"""

import json
import gzip
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime

# Maximum uncompressed payload size (1MB)
MAX_PAYLOAD_SIZE = 1048576

# Compression threshold (compress if payload > 10KB)
COMPRESSION_THRESHOLD = 10240

# Fields to exclude from events (internal/redundant data)
EXCLUDED_FIELDS = {
    "created_at",  # Use event timestamp instead
    "updated_at",  # Use event timestamp instead
    "__v",  # MongoDB version field
    "_sa_instance_state",  # SQLAlchemy internal state
}


def remove_unnecessary_fields(data: Dict[str, Any], excluded: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Remove unnecessary fields from event payload.

    Args:
        data: Event payload data
        excluded: Additional fields to exclude (beyond EXCLUDED_FIELDS)

    Returns:
        Optimized payload with unnecessary fields removed
    """
    if excluded is None:
        excluded = []

    fields_to_remove = EXCLUDED_FIELDS.union(set(excluded))

    # Create a copy to avoid modifying original
    optimized = {}

    for key, value in data.items():
        # Skip excluded fields
        if key in fields_to_remove:
            continue

        # Recursively optimize nested dictionaries
        if isinstance(value, dict):
            optimized[key] = remove_unnecessary_fields(value, excluded)
        # Recursively optimize lists of dictionaries
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            optimized[key] = [remove_unnecessary_fields(item, excluded) for item in value]
        else:
            optimized[key] = value

    return optimized


def compress_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compress event payload if it exceeds compression threshold.

    Args:
        data: Event payload data

    Returns:
        Compressed payload with metadata, or original if below threshold
    """
    # Serialize to JSON
    json_str = json.dumps(data, separators=(',', ':'))  # Compact JSON
    payload_size = len(json_str.encode('utf-8'))

    # Check if compression is needed
    if payload_size < COMPRESSION_THRESHOLD:
        return data

    # Compress using gzip
    compressed = gzip.compress(json_str.encode('utf-8'))
    compressed_size = len(compressed)

    # Only use compression if it actually reduces size
    if compressed_size >= payload_size:
        return data

    # Encode compressed data as base64
    compressed_b64 = base64.b64encode(compressed).decode('utf-8')

    return {
        "_compressed": True,
        "_original_size": payload_size,
        "_compressed_size": compressed_size,
        "_compression_ratio": round(compressed_size / payload_size, 2),
        "data": compressed_b64
    }


def decompress_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Decompress event payload if it was compressed.

    Args:
        data: Potentially compressed payload

    Returns:
        Decompressed payload data
    """
    if not isinstance(data, dict) or not data.get("_compressed"):
        return data

    # Decode base64 and decompress
    compressed = base64.b64decode(data["data"])
    decompressed = gzip.decompress(compressed)
    json_str = decompressed.decode('utf-8')

    return json.loads(json_str)


def validate_payload_size(data: Dict[str, Any]) -> bool:
    """
    Validate that payload size is within limits.

    Args:
        data: Event payload data

    Returns:
        True if within limits, False otherwise
    """
    json_str = json.dumps(data, separators=(',', ':'))
    payload_size = len(json_str.encode('utf-8'))

    return payload_size <= MAX_PAYLOAD_SIZE


def optimize_event_payload(
    event_data: Dict[str, Any],
    excluded_fields: Optional[List[str]] = None,
    enable_compression: bool = True
) -> Dict[str, Any]:
    """
    Optimize event payload by removing unnecessary fields and compressing if needed.

    Args:
        event_data: Original event payload
        excluded_fields: Additional fields to exclude
        enable_compression: Whether to enable compression

    Returns:
        Optimized event payload

    Raises:
        ValueError: If payload exceeds maximum size even after optimization
    """
    # Step 1: Remove unnecessary fields
    optimized = remove_unnecessary_fields(event_data, excluded_fields)

    # Step 2: Validate size before compression
    if not validate_payload_size(optimized):
        raise ValueError(
            f"Event payload exceeds maximum size ({MAX_PAYLOAD_SIZE} bytes) "
            f"even after removing unnecessary fields"
        )

    # Step 3: Compress if enabled and beneficial
    if enable_compression:
        optimized = compress_payload(optimized)

    return optimized


def get_payload_stats(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get statistics about event payload.

    Args:
        data: Event payload data

    Returns:
        Dictionary with payload statistics
    """
    json_str = json.dumps(data, separators=(',', ':'))
    payload_size = len(json_str.encode('utf-8'))

    return {
        "size_bytes": payload_size,
        "size_kb": round(payload_size / 1024, 2),
        "is_compressed": data.get("_compressed", False),
        "compression_ratio": data.get("_compression_ratio"),
        "within_limits": payload_size <= MAX_PAYLOAD_SIZE,
        "should_compress": payload_size >= COMPRESSION_THRESHOLD
    }


# Example usage:
if __name__ == "__main__":
    # Example event with unnecessary fields
    event = {
        "event_type": "todo.task.created",
        "payload": {
            "task_id": "123",
            "user_id": "456",
            "task_data": {
                "title": "Complete project documentation",
                "description": "Write comprehensive docs for all features",
                "status": "pending",
                "priority": "High",
                "created_at": "2024-02-14T10:00:00Z",  # Unnecessary
                "updated_at": "2024-02-14T10:00:00Z",  # Unnecessary
                "__v": 0,  # Unnecessary
                "tags": ["documentation", "high-priority"]
            }
        },
        "timestamp": "2024-02-14T10:00:00Z",
        "correlation_id": "test-123"
    }

    print("Original payload:")
    print(json.dumps(event, indent=2))
    print(f"\nOriginal stats: {get_payload_stats(event)}")

    # Optimize payload
    optimized = optimize_event_payload(event)

    print("\nOptimized payload:")
    print(json.dumps(optimized, indent=2))
    print(f"\nOptimized stats: {get_payload_stats(optimized)}")

    # Test decompression
    if optimized.get("_compressed"):
        decompressed = decompress_payload(optimized)
        print("\nDecompressed payload:")
        print(json.dumps(decompressed, indent=2))
