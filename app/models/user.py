from sqlalchemy import Column, Integer, String

from app.database import Base


# User Model
class User(Base):
    # Define our table name
    __tablename__ = "users"

    # Fields
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    # Make username field 50 chars max and unique
    username = Column(String(50), name="username", nullable=False, unique=True)
    # We will never store our users PW plaintext, but we need the hash for comp
    hashed_password = Column(String, name="hashed_password")
