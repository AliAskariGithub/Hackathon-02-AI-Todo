from sqlmodel import create_engine
from ..config import settings
import urllib.parse


# Create sync engine - adjust driver for sync operations
try:
    original_url = settings.database_url
    if "postgresql" in original_url:
        # Replace postgresql+asyncpg:// with postgresql+psycopg2:// for sync operations
        sync_db_url = original_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
        # Handle case where it might be just postgresql://
        if sync_db_url == original_url:  # No replacement happened
            sync_db_url = original_url.replace("postgresql://", "postgresql+psycopg2://")

        # Parse the URL to handle query parameters properly
        parsed = urllib.parse.urlparse(sync_db_url)

        # Remove problematic query parameters for psycopg2
        query_params = urllib.parse.parse_qs(parsed.query)

        # Keep only parameters that are compatible with psycopg2
        allowed_params = {}
        for key, value_list in query_params.items():
            # For psycopg2, remove problematic parameters that may cause issues
            if key not in ['channel_binding']:
                # Take first value from the list
                allowed_params[key] = value_list[0] if value_list else ''

        new_query = urllib.parse.urlencode(allowed_params)
        sync_db_url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))

        # Create engine with additional connection parameters for Neon compatibility
        sync_engine = create_engine(
            sync_db_url,
            pool_pre_ping=True,  # Helps with connection issues in serverless environments
            pool_recycle=300,    # Recycle connections to handle serverless timeouts
            pool_timeout=30,     # Increase timeout to handle DNS resolution delays
            max_overflow=0,      # Limit overflow connections for serverless
            pool_size=5,         # Smaller pool for serverless
            connect_args={
                "connect_timeout": 30,  # Longer timeout for initial connection
            }
        )
    elif "sqlite" in original_url:
        sync_engine = create_engine(original_url, connect_args={"check_same_thread": False})
    else:
        sync_engine = create_engine(original_url)
except Exception as e:
    print(f"Error initializing sync database engine: {e}")
    # Fallback to a dummy engine for graceful degradation
    sync_engine = create_engine("sqlite:///:memory:")
    import logging
    logging.error(f"Failed to initialize database engine: {e}")