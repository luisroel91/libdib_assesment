"""
Router for User objs
"""
import datetime

from fastapi import APIRouter, Depends

from fastapi_jwt_auth import AuthJWT

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select

# Import our dep here to automatically hand db session to routes
from app.database import get_session
from app.core.services.auth import verify_password, denylist
from app.models.user import User
from app.schemas.user import UserIn, UserOut

router = APIRouter()


# Take a username + password, hash PW, verify and return token
@router.post("/login")
async def login(user: UserIn, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Try to grab user by username
    try:
        user_instance = await session.execute(
            select(User).where(
                usermame=user.username
            )
        )
    # If we can't find them, return an exception
    except NoResultFound:
        return {"login_error": "Can't find User"}
    # Otherwise, get hash for the password in req
    pw_match = await verify_password(user.password, user_instance.hashed_password)
    # If they don't match, return an error
    if not pw_match:
        return {"login_error": "Can't verify info provided"}
    # Generate our access and refresh token setting our User's username as subject
    # We set access token to expire in 30 mins and refresh tokens to expire in 1 hour
    access_token = auth.create_access_token(subject=user.username, expires_time=datetime.timedelta(minutes=30))
    refresh_token = auth.create_refresh_token(subject=user.username, expires_time=datetime.timedelta(hours=1))
    # Set them as cookies
    auth.set_access_cookies(access_token)
    auth.set_refresh_cookies(refresh_token)
    # Return the User obj if login ok
    return UserOut(**user_instance.dict())


# Take a valid JWT token from the request and unset httponly cookies
# httponly cannot be manipulated by FE, making them safer albeit, a bit harder to log out
@router.get("/logout")
async def delete_token_cookies(auth: AuthJWT = Depends()):
    # Make sure request contains valid token
    auth.jwt_required()
    # Unset JWT httponly cookies
    auth.unset_jwt_cookies()
    # Let client know
    return {"status": "logout ok"}


# Take a valid/unexpired refresh token and return a new access token
@router.post("/refresh")
async def refresh_access_token(auth: AuthJWT = Depends()):
    # Make sure User has a valid/unexpired refresh token
    auth.jwt_refresh_token_required()
    # Get username (subject) of token
    curr_username = auth.get_jwt_subject()
    # Gen new access token
    new_access_token = auth.create_access_token(subject=curr_username)
    # Set it as cookie
    auth.set_access_cookies(new_access_token)
    return {"status": "access token refreshed"}


# Take a tokens jti and add it to our revoked token list
@router.post('revoke_access_token')
async def revoke_access_token(auth: AuthJWT = Depends()):
    # Make sure person making req has valid token
    auth.jwt_required()
    # Grab jti from token used in req
    jti = auth.get_raw_jwt()['jti']
    # Add to deny list
    denylist.add(jti)
    # Let client know
    return {"status": "token revoke ok"}


# Take a refresh token jti and add it to our revoked token list
@router.post('revoke_refresh_token')
async def revoke_refresh_token(auth: AuthJWT = Depends()):
    # Make sure person making req has valid refresh token
    auth.jwt_refresh_token_required()
    # Get jti or token used to make req
    jti = auth.get_raw_jwt()['jti']
    # Add to deny list
    denylist.add(jti)
    # Let client know
    return {"status": "refresh token revoke ok"}