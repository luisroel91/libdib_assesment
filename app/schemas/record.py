from pydantic import BaseModel


# Schema's for our CensusRecord objs
class RecordIn(BaseModel):
    race: str
    age_range: str
    year: int
    # Male fields
    num_males_with_income: int
    male_median_income_curr_dollars: float
    male_median_income_2019_dollars: float
    # Female fields
    num_females_with_income: int
    female_median_income_curr_dollars: float
    female_median_income_2019_dollars: float

    class Config:
        orm_mode = True


class RecordOut(RecordIn):
    id: int

    class Config:
        orm_mode = True
