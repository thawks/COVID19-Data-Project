import pandas as pd
from pathlib import Path


def prep_old_data(path, county_names=True, FIPS=False):
    # reads in old format equity data file from path;
    # extracts column, index, and count info separately;
    # prepares it for cleaning by creating a multi index;
    # and some small formatting changes
    df = pd.read_csv(path, header=None, na_values="-")
    df = df.dropna(axis=1, how="all")
    dates = df.iloc[0, 3:].fillna(method="ffill")
    dates = pd.to_datetime(dates)
    cats = df.iloc[2, 3:].str.replace("[ /]", "_", regex=True).str.lower().fillna("-")
    if county_names:
        index = pd.Index(df.iloc[3:, 0], name = "county_names")
    elif FIPS:
        index = pd.Index(df.iloc[3:, 2], name="fips_codes")
    totals = df.iloc[3:,3:].values
    multi_cols = pd.MultiIndex.from_frame(pd.DataFrame({'dates': dates, 'categories': cats}))
    return pd.DataFrame(totals, columns=multi_cols, index=index)


def clean_old_data(df):
    # takes prepped dataframe, stacks it to be long, not wide
    # filters out total columns
    long_df = df.stack(level=['dates', 'categories'], dropna=True)
    cats = long_df.index.levels[2]
    shorter_cats = list(cats[~cats.str.contains('total')])
    less_long_df = long_df[long_df.index.get_level_values("categories").isin(shorter_cats)]
    return less_long_df


def main():
    data_path = Path.cwd().parent / "data/Equity June-Sept FINALIZED - JUNE Data.csv"
    prepped_data = prep_old_data(data_path)
    cleaned_data = clean_old_data(prepped_data)
    cleaned_data.to_csv(Path.cwd().parent / "data/pub_equity_jun-sept.csv")
    return cleaned_data

if __name__ == "__main__":
    df = main()




















