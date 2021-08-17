import pandas as pd
from sqlalchemy import Float, SmallInteger, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import sessionmaker

# Grab our app settings
from app.core.config import settings

# Instantiate Async PG SQLAlchemy engine
engine = create_async_engine(settings.DATABASE_URI, echo=True)
# Turn off expire on commit to prevent DB inconsistencies with async
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Declare our base schema class
@as_declarative()
class Base:
    # Declare table name attr in our base schema
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


# We will use this to async create db sessions when needed
async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def load_pickle(dest_engine):
    # Hydrate our pickle back into a DF
    df = pd.read_pickle("../data_processing/res.pkl")
    # Write the DF to table
    df.to_sql(
        # Table we'll write to
        "census_records",
        # Our SQLAlchemy engine
        con=dest_engine,
        # Make sure IDs are handled by SQLAlchemy
        index=False,
        # Specify data types for our cols
        dtype={
            "race": String(10),
            "age_range": String(10),
            "year": SmallInteger,
            "num_males_with_income": SmallInteger,
            "male_median_income_curr_dollars": Float,
            "male_median_income_2019_dollars": Float,
            "num_females_with_income": SmallInteger,
            "female_median_income_curr_dollars": Float,
            "female_median_income_2019_dollars": Float
        }
    )


"""
Typically you'd want to use Alembric or something else to manage
your database migrations, in this case, we are doing it manually
"""


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(load_pickle(conn))
