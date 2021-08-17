"""
Router for Record objs
"""
from fastapi import APIRouter, Depends

from fastapi_jwt_auth import AuthJWT

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.record import CensusRecord
from app.schemas.record import RecordIn, RecordOut

router = APIRouter()


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
    return result


@router.post("/new_record", response_model=RecordOut)
async def create_record(new_record: RecordIn, session: AsyncSession = Depends(get_session), auth: AuthJWT = Depends()):
    # Make sure requester has valid JWT token
    auth.jwt_required()
    # Take data that was POSTd and instantiate new record
    new_instance = CensusRecord(**new_record.dict())
    # Add new instance to DB session
    session.add(new_instance)
    # Check that we don't already have a record for this race, sex and year
    try:
        dupe = await session.execute(
            select(CensusRecord).where(
                race=new_record.race,
                age_range=new_record.age_range,
                year=new_record.year,
            )
        )
    # If we find no result
    except NoResultFound:
        # Try persisting to DB (committing) object
        try:
            await session.commit()
            return RecordOut(**new_instance.dict())
        # If we have an integrity error, rollback our transaction
        except IntegrityError:
            await session.rollback()
            return {"error": "DB integrity error saving object"}
    else:
        return {"error": "duplicate record entry exists"}
