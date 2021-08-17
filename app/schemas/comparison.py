from typing import Optional

from pydantic import BaseModel


# Schema for comparison included responses
class Comparison(BaseModel):
    income_difference: int
    head: str
    population_difference: int
    percent_change_pop: Optional[float] = None
    percent_change_income: Optional[float] = None

    class Config:
        orm_mode = True
