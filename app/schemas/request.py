from typing import Optional

from pydantic import BaseModel


# Schema for a request being made to server
class Request(BaseModel):
    base_year: Optional[int] = None
    year: int
    sex: Optional[str]
    race: Optional[str]
    age: int

    class Config:
        orm_mode = True
