import pandas as pd
from pathlib import Path



new_data = pd.read_csv(Path.cwd().parent / "data/pub_equity_jun-sept.csv",
                       parse_dates=True)
old_data_path = Path.cwd().parent / "data/Equity June-Sept FINALIZED - June Data.csv"
old_data = pd.read_csv(old_data_path, header = None)

def check_count(row_tuple, old_data):
    county = (row_tuple[1])
    day = (row_tuple[2]).strftime("%A, %-m/%-d/%y")
    next_day = (row_tuple[2])
    cat = (row_tuple[3])
    count = (row_tuple[4])
    county_row = old_data.iloc[:,0] == county
    day_column = old_data.iloc[0,][old_data.iloc[0,] == day].index[0]
    cat_column = (old_data.iloc[3,]
                .str
                .replace("[ /]", "_", regex=True).str.lower()
                  )
    cat_column = cat_column.iloc[day_column:] == cat


def test(new_df, old_df):
    new_test = new_df[0:5]
    old_test = old_df[0:10]
    for i in new_test.itertuples():
        county = (i[1])
        day = (i[2])
        cat = (i[3])
        count = (i[4])
