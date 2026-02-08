import jwt
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import os
from src.config import settings

SECRET_KEY = os.getenv("BETTER_AUTH_SECRET", settings.better_auth_secret)
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a new access token with the provided data.

    Args:
        data: Dictionary containing the data to encode in the token
        expires_delta: Optional timedelta for token expiration (defaults to 15 minutes)

    Returns:
        Encoded JWT token as string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and verify a JWT token.

    Args:
        token: The JWT token to decode

    Returns:
        Decoded token payload as dictionary

    Raises:
        jwt.PyJWTError: If the token is invalid or expired
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload


def verify_user_id_match(token_user_id: str, path_user_id: str) -> bool:
    """
    Verify that the user ID in the JWT token matches the user ID in the URL path.

    Args:
        token_user_id: User ID extracted from the JWT token
        path_user_id: User ID from the URL path parameter

    Returns:
        True if the IDs match, False otherwise
    """
    return str(token_user_id) == str(path_user_id)