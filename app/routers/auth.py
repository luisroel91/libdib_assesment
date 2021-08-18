"""
Router for Auth
"""
import datetime

from fastapi import APIRouter, Depends

from fastapi_jwt_auth import AuthJWT

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Import our dep here to automatically hand db session to routes
from app.database import get_session
from app.core.services.auth import verify_password, denylist
from app.models.user import User
from app.schemas.user import UserIn

# Settings for router
router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


# Take a username + password, hash PW, verify and return token
@router.post("/login")
async def login(req: UserIn, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    """Takes in a UserIn schema, generates a JWT token and returns User

    Returns:
        id: int
        username: str
    """
    # Try to grab user by username
    try:
        result = await session.execute(
            select(User).where(User.username == req.username)
        )
        user_instance = result.scalars().first()
    # If we can't find them, return an exception
    except:
        return {"login_error": "Can't find User"}
    # Keep track of pw_match
    pw_match = False
    # Compare hashes, see if combo was valid
    try:
        pw_match = verify_password(req.password, user_instance.hashed_password)
    except:
        return {"login_error": "Can't verify hash"}
    # If they don't match, return an error
    if not pw_match:
        return {"login_error": "Can't verify info provided"}
    # Generate our access and refresh token setting our User's username as subject
    # We set access token to expire in 30 mins and refresh tokens to expire in 1 hour
    access_token = auth.create_access_token(subject=req.username, expires_time=datetime.timedelta(minutes=30))
    refresh_token = auth.create_refresh_token(subject=req.username, expires_time=datetime.timedelta(hours=1))
    # Return the tokens if login ok
    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/refresh")
async def refresh_access_token(auth: AuthJWT = Depends()):
    """Take a valid refresh token and generate a new access/refresh token"""
    # Make sure User has a valid/unexpired refresh token
    auth.jwt_refresh_token_required()
    # Get username (subject) of token
    curr_username = auth.get_jwt_subject()
    # Gen new access token
    new_access_token = auth.create_access_token(subject=curr_username)
    new_refresh_token = auth.create_refresh_token(subject=curr_username)

    return {"access_token": new_access_token, "refresh_token": new_refresh_token}


# Take a tokens jti and add it to our revoked token list
@router.post('/logout')
async def revoke_access_token(auth: AuthJWT = Depends()):
    # Make sure person making req has valid token
    auth.jwt_required()
    # Grab jti from token used in req
    jti = auth.get_raw_jwt()['jti']
    # Add to deny list
    denylist.add(jti)
    # Let client know
    return {"status": "tokens revoked ok"}


# Take a refresh token jti and add it to our revoked token list
@router.post('/revoke_refresh')
async def revoke_refresh_token(auth: AuthJWT = Depends()):
    # Make sure person making req has valid refresh token
    auth.jwt_refresh_token_required()
    # Get jti or token used to make req
    jti = auth.get_raw_jwt()['jti']
    # Add to deny list
    denylist.add(jti)
    # Let client know
    return {"status": "refresh token revoke ok"}

