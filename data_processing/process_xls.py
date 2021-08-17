import pandas as pd

# Define our header
col_names = [
    "year",
    "num_males_with_income",
    "male_median_income_curr_dollars",
    "male_median_income_2019_dollars",
    "num_females_with_income",
    "female_median_income_curr_dollars",
    "female_median_income_2019_dollars",
]

# Load Asian census data XLS, skipping all headers
dfa = pd.read_excel(
    r'p08a.xlsx',
    skiprows=8,
    # Make sure PD doesn't use header row for our DF
    header=None,
    # Define col names
    names=col_names,
)
# Load White census data XLS, skipping all headers
dfw = pd.read_excel(
    r'p08w.xlsx',
    skiprows=8,
    # Make sure PD doesn't use header row for our DF
    header=None,
    # Define cold names
    names=col_names
)
# Splinter off rows into age group DFs for both sets of data
dfa1524 = dfa.iloc[:20]
dfa2534 = dfa.iloc[25:45]
dfa3544 = dfa.iloc[50:70]
dfa4554 = dfa.iloc[75:95]
dfa5564 = dfa.iloc[100:120]
dfa6574 = dfa.iloc[125:145]
dfa75 = dfa.iloc[150:170]

dfw1524 = dfw.iloc[:20]
dfw2534 = dfw.iloc[25:45]
dfw3544 = dfw.iloc[50:70]
dfw4554 = dfw.iloc[75:95]
dfw5564 = dfw.iloc[100:120]
dfw6574 = dfw.iloc[125:145]
dfw75 = dfw.iloc[150:170]

# Add Age Range col to each DF
dfa1524.insert(0, 'age_range', '15-24')
dfa2534.insert(0, 'age_range', '25-34')
dfa3544.insert(0, 'age_range', '35-44')
dfa4554.insert(0, 'age_range', '45-54')
dfa5564.insert(0, 'age_range', '55-64')
dfa6574.insert(0, 'age_range', '65-74')
dfa75.insert(0, 'age_range', 'Over 75')

dfw1524.insert(0, 'age_range', '15-24')
dfw2534.insert(0, 'age_range', '25-34')
dfw3544.insert(0, 'age_range', '35-44')
dfw4554.insert(0, 'age_range', '45-54')
dfw5564.insert(0, 'age_range', '55-64')
dfw6574.insert(0, 'age_range', '65-74')
dfw75.insert(0, 'age_range', 'Over 75')

# Stack cleaned DF's vertically
dfa = pd.concat([
    dfa1524,
    dfa2534,
    dfa3544,
    dfa4554,
    dfa5564,
    dfa6574,
    dfa75
], axis=0)

dfw = pd.concat([
    dfw1524,
    dfw2534,
    dfw3544,
    dfw4554,
    dfw5564,
    dfw6574,
    dfw75
], axis=0)

# Add Race col
dfa.insert(0, 'race', 'asian')
dfw.insert(0, 'race', 'white')

# Clean garbage chars in Year col using regex
dfa['year'] = dfa['year'].replace(to_replace=r'(\s\(\d+\))', value='', regex=True)
dfw['year'] = dfw['year'].replace(to_replace=r'(\s\(\d+\))', value='', regex=True)

# Stack our cleaned + normalized data into a single DF
df = pd.concat([
    dfa,
    dfw
], axis=0)

# Pickle the DF
df.to_pickle("./res.pkl")
