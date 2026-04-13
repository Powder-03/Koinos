from fastapi import Request, HTTPException, status
from firebase_admin import auth


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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header. Expected: 'Bearer <token>'"
        )

    token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        uid: str = decoded_token["uid"]
        return uid
    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has expired. Please re-authenticate."
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Firebase token has been revoked."
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials."
        )
