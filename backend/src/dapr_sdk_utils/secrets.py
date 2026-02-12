"""
Dapr Secrets API Utility Functions

This module provides utility functions for retrieving secrets from Dapr Secret Store.
It eliminates direct environment variable access and enables cloud-agnostic
secret management.

Key Features:
- Retrieve secrets from Kubernetes Secret Store
- Bulk secret retrieval
- Automatic caching for performance
- Type-safe secret access
"""

from typing import Dict, Optional
from dapr.clients import DaprClient
import json


class DaprSecretStore:
    """
    Wrapper for Dapr Secret Store operations.

    Provides methods for retrieving secrets from configured secret stores
    (Kubernetes Secrets, Azure Key Vault, AWS Secrets Manager, etc.)
    """

    def __init__(self, store_name: str = "secretstore"):
        """
        Initialize Dapr Secret Store client.

        Args:
            store_name: Name of the Dapr Secret Store component (default: "secretstore")
        """
        self.store_name = store_name
        self.client = DaprClient()
        self._cache: Dict[str, str] = {}

    def get_secret(
        self,
        key: str,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        Retrieve a secret from Dapr Secret Store.

        Args:
            key: Secret key (e.g., "DATABASE_URL", "JWT_SECRET")
            use_cache: Whether to use cached value (default: True)

        Returns:
            Secret value as string, or None if not found

        Example:
            >>> secrets = DaprSecretStore()
            >>> db_url = secrets.get_secret("DATABASE_URL")
        """
        # Check cache first
        if use_cache and key in self._cache:
            return self._cache[key]

        try:
            secret_response = self.client.get_secret(
                store_name=self.store_name,
                key=key
            )

            if secret_response.secret:
                # Dapr returns secrets as dict with key as the field name
                value = secret_response.secret.get(key)
                if value and use_cache:
                    self._cache[key] = value
                return value
        except Exception as e:
            print(f"Error retrieving secret '{key}': {e}")
            return None

    def get_bulk_secrets(
        self,
        keys: list[str],
        use_cache: bool = True
    ) -> Dict[str, Optional[str]]:
        """
        Retrieve multiple secrets in a single operation.

        Args:
            keys: List of secret keys
            use_cache: Whether to use cached values (default: True)

        Returns:
            Dictionary mapping keys to secret values

        Example:
            >>> secrets = DaprSecretStore()
            >>> config = secrets.get_bulk_secrets([
            ...     "DATABASE_URL",
            ...     "JWT_SECRET",
            ...     "GROQ_API_KEY"
            ... ])
        """
        result = {}

        for key in keys:
            result[key] = self.get_secret(key, use_cache=use_cache)

        return result

    def get_all_secrets(self) -> Dict[str, str]:
        """
        Retrieve all secrets from the secret store.

        Returns:
            Dictionary of all secrets

        Example:
            >>> secrets = DaprSecretStore()
            >>> all_secrets = secrets.get_all_secrets()
        """
        try:
            bulk_response = self.client.get_bulk_secret(
                store_name=self.store_name
            )

            result = {}
            if bulk_response.secrets:
                for key, secret_dict in bulk_response.secrets.items():
                    # Extract the actual secret value
                    if isinstance(secret_dict, dict):
                        result[key] = secret_dict.get(key, "")
                    else:
                        result[key] = str(secret_dict)

            # Update cache
            self._cache.update(result)
            return result
        except Exception as e:
            print(f"Error retrieving all secrets: {e}")
            return {}

    def clear_cache(self) -> None:
        """
        Clear the secret cache.

        Use this when secrets have been rotated and need to be refreshed.
        """
        self._cache.clear()


# Singleton instance for application-wide use
_secret_store_instance: Optional[DaprSecretStore] = None


def get_secret_store() -> DaprSecretStore:
    """
    Get the singleton DaprSecretStore instance.

    Returns:
        DaprSecretStore instance

    Example:
        >>> from dapr_sdk_utils.secrets import get_secret_store
        >>> secrets = get_secret_store()
        >>> db_url = secrets.get_secret("DATABASE_URL")
    """
    global _secret_store_instance
    if _secret_store_instance is None:
        _secret_store_instance = DaprSecretStore()
    return _secret_store_instance


# Secret key constants
SECRET_DATABASE_URL = "DATABASE_URL"
SECRET_JWT_SECRET = "JWT_SECRET"
SECRET_BETTER_AUTH_SECRET = "BETTER_AUTH_SECRET"
SECRET_GROQ_API_KEY = "GROQ_API_KEY"
SECRET_KAFKA_BOOTSTRAP_SERVERS = "KAFKA_BOOTSTRAP_SERVERS"


def get_database_url() -> str:
    """
    Convenience function to get database URL.

    Returns:
        Database connection URL

    Raises:
        ValueError: If DATABASE_URL secret is not found
    """
    secrets = get_secret_store()
    db_url = secrets.get_secret(SECRET_DATABASE_URL)
    if not db_url:
        raise ValueError("DATABASE_URL secret not found in Dapr Secret Store")
    return db_url


def get_jwt_secret() -> str:
    """
    Convenience function to get JWT secret.

    Returns:
        JWT secret key

    Raises:
        ValueError: If JWT_SECRET secret is not found
    """
    secrets = get_secret_store()
    jwt_secret = secrets.get_secret(SECRET_JWT_SECRET)
    if not jwt_secret:
        raise ValueError("JWT_SECRET secret not found in Dapr Secret Store")
    return jwt_secret


def get_groq_api_key() -> str:
    """
    Convenience function to get Groq API key.

    Returns:
        Groq API key

    Raises:
        ValueError: If GROQ_API_KEY secret is not found
    """
    secrets = get_secret_store()
    api_key = secrets.get_secret(SECRET_GROQ_API_KEY)
    if not api_key:
        raise ValueError("GROQ_API_KEY secret not found in Dapr Secret Store")
    return api_key
