"""
Router for Record objs
"""
import pandas as pd

from fastapi import APIRouter, Depends

from fastapi_jwt_auth import AuthJWT

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.record import CensusRecord
from app.core.services.record import make_comparison
from app.schemas.record import RecordIn, RecordOut
from app.schemas.request import Request

# Router settings
router = APIRouter(
    prefix="/data",
    tags=["data"],
)


# Load our pickle into DB
@router.post("/load_pickle")
async def load_pickle(session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    """Loads XLS data that was converted to DF into DB"""
    # Make sure requested has valid JWT token
    auth.jwt_required()
    # Hydrate our pickle back into a DF
    df = pd.read_pickle("../data_processing/res.pkl")
    # Create dict of to load into db
    data = df.to_dict(orient='records')
    # Build a list of CensusRecord objs
    inst_list = []
    for row in data:
        inst_list.append(CensusRecord(**row))
    # Try adding this list to DB session and committing
    session.add_all(inst_list)
    try:
        await session.commit()
    except:
        return {"status": "failed to load pickle"}
    return {"status": "pickle loaded"}


# Use FastAPI's dependency injection to automatically gran our db session
@router.get("/{record_id}", response_model=RecordOut)
async def get_record_by_id(record_id: int, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Make sure requester has valid JWT token
    auth.jwt_required()
    # Try grabbing record from DB
    try:
        result = await session.execute(
            select(CensusRecord).where(CensusRecord.id == record_id)
        )
    except NoResultFound:
        return {"get_record_error": "record not found"}
    # Turn our list of one into an obj
    return result.scalars().first()


@router.post("/new_record", response_model=RecordOut)
async def create_record(new_record: RecordIn, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Make sure requester has valid JWT token
    auth.jwt_required()
    # Take data that was POSTd and instantiate new record
    print(new_record.dict())
    new_instance = CensusRecord(**new_record.dict())
    # Add new instance to DB session
    session.add(new_instance)
    # Try persisting to DB (committing) object
    try:
        await session.commit()
        return new_instance
        # If we have an integrity error, rollback our transaction
    except IntegrityError:
        await session.rollback()
        return {"error": "DB integrity error saving object"}


# Take a request for a comparison, process & return it
@router.post("/get_comparison")
async def get_comparison(request: Request, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Make sure request contains valid token
    auth.jwt_required()
    # Make our comparison, returns result in format reqd by spec
    result = await make_comparison(request, session)
    # Return our result
    return result
