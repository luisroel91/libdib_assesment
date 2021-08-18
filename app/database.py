from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
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


"""
Typically you'd want to use Alembric or something else to manage
your database migrations, in this case, we are doing it manually on startup
"""


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
