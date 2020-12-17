import pandas as pd
import requests
import argparse
from datetime import datetime
from pathlib import Path
import sys


def get_from_xl_link(url, **sheets):
    r = requests.get(url)
    if sheets is None:
        return pd.read_excel(r.content)
    else:
        rv = {}
        for key, val in sheets.items():
            rv[key] = pd.read_excel(r.content, val)
        return rv


def clean_in(race_df, ethnicity_df, record_date=None):
    # Drop the rows corresponding to districts, since we only need county information.
    if record_date is None:
        record_date = datetime.now().strftime("%Y-%m-%d")
    elif isinstance(record_date, datetime):
        record_date = record_date.strftime("%Y-%m-%d")
    else:
        raise TypeError("Incorrect record date format")
    race_df = race_df.drop(race_df.loc[race_df["location_level"] == "d"].index)
    ethnicity_df = ethnicity_df.drop(
        ethnicity_df.loc[ethnicity_df["location_level"] == "d"].index
    )

    # Drop unneeded columns. We only need county name, race, and number of confirmed cases.
    race_df = race_df.drop(
        columns=[
            "location_level",
            "location_id",
            "covid_test",
            "covid_deaths",
            "covid_test_pct",
            "covid_count_pct",
            "covid_deaths_pct",
        ]
    )
    ethnicity_df = ethnicity_df.drop(
        columns=[
            "location_level",
            "location_id",
            "covid_test",
            "covid_deaths",
            "covid_test_pct",
            "covid_count_pct",
            "covid_deaths_pct",
        ]
    )

    # Create pivot tables to match the format of our spreadsheet.
    race_df = race_df.pivot(index="county_name", columns="race", values="covid_count")
    ethnicity_df = ethnicity_df.pivot(
        index="county_name", columns="ethnicity", values="covid_count"
    )

    # Add columns missing from the Indiana data, but tracked by COVID19 Data Project.
    race_df = race_df.assign(
        American_Indian_Alaska_Native="-",
        Native_Hawaiian_Pacific_Islander="-",
        Two_races="-",
        Race_total=race_df.sum(axis=1),
    )

    ethnicity_df = ethnicity_df.assign(Ethnicity_total=ethnicity_df.sum(axis=1))

    # Join race and ethnicity DataFrames.
    ethnicity_df = ethnicity_df.rename(columns={"Unknown": "Not Specified"})
    race_and_ethnicity_df = race_df.merge(ethnicity_df, on="county_name")
    race_and_ethnicity_df = race_and_ethnicity_df.assign(Date=record_date)
    race_and_ethnicity_df = race_and_ethnicity_df[
        [
            "Date",
            "White",
            "Black or African American",
            "Asian",
            "American_Indian_Alaska_Native",
            "Native_Hawaiian_Pacific_Islander",
            "Two_races",
            "Other Race",
            "Unknown",
            "Hispanic or Latino",
            "Not Hispanic or Latino",
            "Not Specified",
        ]
    ]
    race_and_ethnicity_df = race_and_ethnicity_df.assign(
        Total=race_df["Race_total"][
            race_df["Race_total"] == ethnicity_df["Ethnicity_total"]
        ]
    )

    # Rename two counties and sort to match our spreadsheet, then write to a new CSV file.
    race_and_ethnicity_df = race_and_ethnicity_df.rename(
        index={"De Kalb": "Dekalb", "La Porte": "Laporte"}
    )
    race_and_ethnicity_df = race_and_ethnicity_df.sort_index()
    return race_and_ethnicity_df


def write_in(df):
    if (x == df["Date"].iloc[0] for x in df["Date"]):
        date = df["Date"].iloc[0]
    else:
        date = "unknown"
        raise Warning("warning: datestamps not all same")
    path = Path(__file__).parent.parent.absolute() / "cleaned_data/in"
    df.to_csv(path / ("reformatted_covid_report_indiana_" + date + ".csv"))
    df.drop("Date", axis=1).to_clipboard(sep=",", index=False, header=False)
    print(
        "{count} counties added from Indiana dated {date}.".format(
            count=df.shape[0], date=date
        )
    )
    print("Copied to clipboard")


def parse_date_arg(arg=str()):
    rv = datetime.strptime(arg, "%Y-%m-%d")
    return rv


def main(path=None, record_date=None):
    if path is None and record_date is None:
        url = "https://hub.mph.in.gov/dataset/07e12c46-eb38-43cf-b9e1-46a9c305beaa/resource/9ae4b185-b81d-40d5-aee2-f0e30405c162/download/covid_report_demographics_county_district.xlsx"
        dfs = get_from_xl_link(url, race="Race", eth="Ethnicity")
        df = clean_in(dfs["race"], dfs["eth"])
    elif path is not None and record_date is not None:
        race_df = pd.read_excel(args.path, "Race")
        eth_df = pd.read_excel(args.path, "Ethnicity")
        df = clean_in(race_df, eth_df, record_date=args.record_date)
    test_value = (path is not None and record_date is not None) or (path is None and record_date is None)
    try:
        assert test_value, "Key value error, must input path and record date, or neither."
    except AssertionError as error:
        print(error)
        sys.exit()
    else:
        write_in(df)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="pass filepath to clean_in")
    parser.add_argument(
        "--record_date",
        help="pass date as (yyyy-mm-dd) to clean_in",
        type=parse_date_arg,
    )
    args = parser.parse_args()
    main(args.path, record_date=args.record_date)
