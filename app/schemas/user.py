from pydantic import BaseModel


class UserIn(BaseModel):
    username: str
    password: str

    # Make it so we can use dot notation
    class Config:
        orm_mode = True


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True
