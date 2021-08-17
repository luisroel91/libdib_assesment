"""
Router for User objs
"""
import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from fastapi_jwt_auth import AuthJWT

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import select

# Import our dep here to automatically hand db session to routes
from app.database import get_session
from app.core.services.auth import get_password_hash, verify_password, denylist
from app.models.user import User
from app.schemas.user import UserIn, UserOut

router = APIRouter()


# Create a user, has their password and then return it
@router.post("/create")
async def create_user(user: UserIn, session: AsyncSession = Depends(get_session)):
    # Take our request and convert to User instance
    new_user = User(**user.dict())
    # Get hash for PW
    hashed_pw = await get_password_hash(user.password)
    # Add hash to new User instance
    new_user.hashed_password = hashed_pw
    # Add to db session
    session.add(new_user)
    # Try to persist to DB
    try:
        await session.commit()
        # If we're successful, return the object in our UserOur schema
        return UserOut(**new_user.dict())
    except IntegrityError:
        # If we fail, roll back the transaction
        await session.rollback()
        return {"error": "DB integrity error saving object"}


# Delete a user, if the user is requesting to delete themselves
@router.post("/delete/{u_id}")
async def delete_user(u_id: int, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Make sure requester has valid JWT token
    auth.jwt_required()
    # Get username for token provided
    token_subject = auth.get_jwt_subject()
    # Try getting User with id in our u_id param
    try:
        requested_user = await session.execute(
            select(User).where(
                id=u_id
            )
        )
    except NoResultFound:
        return {"error": "delete failed, no User with that ID found"}
    # Check if username in token == username in User obj we grabbed
    if token_subject == requested_user.username:
        # If it does, lets try setting it to delete and then committing
        try:
            await session.delete(requested_user)
            await session.commit()
            # If we can commit, let the client know
            return {"status": "deleting user successful"}
        except:
            return {"error": "delete failed, could not commit change to db"}
    # If not, reject delete request
    return {"status": "request rejected"}
