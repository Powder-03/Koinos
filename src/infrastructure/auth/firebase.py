import logging
from fastapi import Request, HTTPException, status
from firebase_admin import auth

logger = logging.getLogger(__name__)


async def verify_firebase_token(request: Request) -> str:
    """
    FastAPI dependency that extracts and verifies the Firebase ID token
    from the Authorization header. Returns the Firebase UID.

    Usage:
        @router.get("/")
        async def endpoint(user_id: str = Depends(verify_firebase_token)):
            ...
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("Missing or malformed Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected: 'Bearer <token>'"
        )

    token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        uid: str = decoded_token["uid"]
        logger.debug("✅ Token verified for UID: %s", uid)
        return uid
    except auth.ExpiredIdTokenError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired. Please re-authenticate."
        )
    except auth.RevokedIdTokenError:
        logger.warning("Token revoked")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has been revoked."
        )
    except auth.InvalidIdTokenError as e:
        logger.error("Invalid Firebase token: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token."
        )
    except Exception as e:
        logger.error("Unexpected auth error: %s — %s", type(e).__name__, e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        )

