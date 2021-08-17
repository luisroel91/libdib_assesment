from sqlalchemy import Column, Float, Integer, SmallInteger, String

from app.database import Base

"""
Model for a row of census data

Our pop script will read our DF pickle
convert all rows to Record objects and
then dump into PG DB
"""


class CensusRecord(Base):
    __tablename__ = 'census_records'

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    race = Column(String(10))
    age_range = Column(String(10))
    year = Column(SmallInteger)
    # Male Fields
    num_males_with_income = Column(SmallInteger)
    male_median_income_curr_dollars = Column(Float)
    male_median_income_2019_dollars = Column(Float)
    # Female Fields
    num_females_with_income = Column(SmallInteger)
    female_median_income_curr_dollars = Column(Float)
    female_median_income_2019_dollars = Column(Float)
