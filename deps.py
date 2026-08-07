from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from database import decode_access_token

bearer_scheme = HTTPBearer()


def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> str:
    """Decode the Bearer token and return the authenticated user's email, or 401."""
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session. Please log in again.",
        )
    return payload["sub"]