from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.record import *
from app.schemas.comparison import Comparison
from app.schemas.request import Request


async def get_age_range_from_req(age: int) -> str:
    # Figure out what age range our request is in to query data
    if age < 15:
        return "age_too_low"
    elif 15 <= age <= 24:
        return "15-24"
    elif 25 <= age <= 34:
        return "25-34"
    elif 35 <= age <= 44:
        return "35-44"
    elif 45 <= age <= 54:
        return "45-54"
    return "age_error"


# This is what actually does the bulk of the work in this API, it takes in a request
# as per the spec and then does the comparison
async def make_comparison(request: Request, session: AsyncSession):
    age_range = await get_age_range_from_req(request.age)
    # To make the comparison, we need to grab pertinent data for both races
    try:
        # Get a sample of our data for w race
        w_data_req = await session.execute(
            select(CensusRecord).where(
                CensusRecord.race == "white",
                CensusRecord.year == request.year,
                CensusRecord.age_range == age_range,
            )
        )
        # Convert our results list into into a single obj
        w_data = w_data_req.scalars().first()
        # Specs said get largest number for comp for both sexes
        wm_income = max(
            w_data.male_median_income_curr_dollars,
            w_data.male_median_income_2019_dollars,
        )
        wf_income = max(
            w_data.female_median_income_curr_dollars,
            w_data.female_median_income_2019_dollars,
        )
        """
        If we have a base year in our req, we'll
        also need data for a diff year for comp

        The spec said do that only when sending all params but really,
        since you're outputting a Comparison for either gender, and only
        comparing two races, you only need to detect if the req contained base_year
        and then calculate percent changes only for the race requested
        """
        if request.base_year:
            # If it did, get another sample of our data to compare
            # and calc percent change
            w_data1_req = await session.execute(
                select(CensusRecord).where(
                    CensusRecord.race == "white",
                    CensusRecord.year == request.base_year,
                    CensusRecord.age_range == age_range,
                )
            )
            w_data1 = w_data1_req.scalars().first()

            wm_base_income = max(
                w_data1.male_median_income_curr_dollars,
                w_data1.male_median_income_2019_dollars,
            )
            wf_base_income = max(
                w_data1.female_median_income_curr_dollars,
                w_data1.female_median_income_2019_dollars
            )
            # Calculate percent change if needed
            if request.race == 'white':
                wm_percent_change_income = wm_income / wm_base_income * 100
                wf_percent_change_income = wf_income / wf_base_income * 100
                wm_percent_change_pop = w_data.num_males_with_income / w_data1.num_males_with_income * 100
                wf_percent_change_pop = w_data.num_females_with_income / w_data1.num_females_with_income * 100
        else:
            # Set them all to None
            wm_percent_change_income = None
            wf_percent_change_income = None
            wm_percent_change_pop = None
            wf_percent_change_pop = None
    except NoResultFound:
        return {"error": "query does not match any data for race w"}

    # Now that we have our w data, we grab our a data
    try:
        # Get a sample of our data for a race
        a_data_req = await session.execute(
            select(CensusRecord).where(
                CensusRecord.race == "asian",
                CensusRecord.year == request.year,
                CensusRecord.age_range == age_range,
            )
        )
        a_data = a_data_req.scalars().first()

        am_income = max(
            a_data.male_median_income_curr_dollars,
            a_data.male_median_income_2019_dollars,
        )
        af_income = max(
            a_data.female_median_income_curr_dollars,
            a_data.female_median_income_2019_dollars,
        )

        if request.base_year:
            a_data1_req = await session.execute(
                select(CensusRecord).where(
                    CensusRecord.race == "asian",
                    CensusRecord.year == request.base_year,
                    CensusRecord.age_range == age_range,
                )
            )
            a_data1 = a_data1_req.scalars().first()

            am_base_income = max(
                a_data1.male_median_income_curr_dollars,
                a_data1.male_median_income_2019_dollars,
            )
            af_base_income = max(
                a_data1.female_median_income_curr_dollars,
                a_data1.female_median_income_2019_dollars,
            )

            if request.race == "asian":
                # Calculate percent changes
                am_percent_change_income = am_income / am_base_income * 100
                af_percent_change_income = af_income / af_base_income * 100
                am_percent_change_pop = a_data.num_males_with_income / a_data1.num_males_with_income * 100
                af_percent_change_pop = a_data.num_females_with_income / a_data1.num_females_with_income * 100
        else:
            am_percent_change_income = None
            af_percent_change_income = None
            am_percent_change_pop = None
            af_percent_change_pop = None

    except NoResultFound:
        return {"error": "query does not match any data for race a"}
    # Calculate attribs for each sex
    m_head = "white" if wm_income > am_income else "asian"
    f_head = "white" if wf_income > af_income else "asian"
    # See if we need to use percent changes and which to use
    if request.base_year:
        # If no race is provided, all of these fields get set to None
        m_percent_change_income = (
            wm_percent_change_income if request.race == "white" else am_percent_change_income if request.race == "asian"
            else None)

        f_percent_change_income = (
            wf_percent_change_income if request.race == "white" else af_percent_change_income if request.race == "asian"
            else None)

        m_percent_change_pop = (
            wm_percent_change_pop if request.race == "white" else am_percent_change_pop if request.race == "asian"
            else None)
        f_percent_change_pop = (
            wf_percent_change_pop if request.race == "white" else af_percent_change_pop if request.race == "asian"
            else None)
    # Otherwise, set all those fields to None so we can react accordingly to the request
    else:
        m_percent_change_income = None
        f_percent_change_income = None
        m_percent_change_pop = None
        f_percent_change_pop = None
    m_comparison = Comparison(**{
        # Make sure we subtract the largest number by the smallest by doing max -
        # min for all vals
        "income_difference": max(wm_income, am_income) - min(wm_income, am_income),
        "head": m_head,
        "population_difference": max(w_data.num_males_with_income, a_data.num_males_with_income) - min(
            w_data.num_males_with_income, a_data.num_males_with_income),
        # If we need to include percent change, serialize it, if not, set to None
        # and Pydantic will ignore the field
        "percent_change_income": m_percent_change_income if request.base_year else None,
        "percent_change_pop": m_percent_change_pop if request.base_year else None,
    })
    f_comparison = Comparison(**{"income_difference": max(wf_income, af_income) - min(wf_income, af_income),
                                 "head": f_head,
                                 "population_difference": max(w_data.num_females_with_income,
                                                              a_data.num_females_with_income) - min(
                                     w_data.num_females_with_income,
                                     a_data.num_females_with_income),
                                 "percent_change_income": f_percent_change_income if request.base_year else None,
                                 "percent_change_pop": f_percent_change_pop if request.base_year else None,
                                 })

    return {
        "year": request.year,
        "sex": request.sex if request.sex else None,
        "age": request.age,
        "comparison": {
            "male": m_comparison,
            "female": f_comparison,
        }
    }
