# clean_va
import pandas as pd
import get_funx
from datetime import datetime
from pathlib import Path
import argparse


def clean_fl(df):
    df.columns = [
        "county",
        "white",
        "black",
        "other",
        "race_unknown",
        "hispanic",
        "non-hispanic",
        "eth_unknown",
        "total",
    ]
    df = df[df["county"].str.isupper()]
    today = datetime.now().strftime("%Y-%m-%d")
    df = df.assign(asian="-", ai_an="-", nh_pi="-", two_plus="-", date=today)
    df = df[
        [
            "date",
            "county",
            "black",
            "white",
            "ai_an",
            "nh_pi",
            "two_plus",
            "other",
            "race_unknown",
            "hispanic",
            "non-hispanic",
            "eth_unknown",
            "total",
        ]
    ]
    return df


def write_fl(df):
    if (x == df["date"].iloc[0] for x in df["date"]):
        date = df["date"].iloc[0]
    else:
        date = "unknown"
        raise Warning("warning: datestamps not all same")
    path = Path(__file__).parent.parent.absolute() / "cleaned_data/fl"
    df.to_csv(path / ("FL_COVID-19_DEMOS_" + date + ".csv"))
    print(
        "{count} counties added from Florida dated {date}.".format(
            count=df.shape[0], date=date
        )
    )


def main(query_date=None):
    if query_date is None:
        query_date = get_funx.set_query_date()
    elif query_date is not None:
        query_date = get_funx.set_query_date(query_date)
    url = (
        "https://services1.arcgis.com/CY1LXxl9zlJeBuRZ/arcgis/rest/services/"
        "Florida_COVID19_Cases/FeatureServer/0/query?"
    )
    payload = get_funx.set_payload(
        query_type="gis",
        query_date=query_date,
        where="1=1",
        outFields=(
            "COUNTYNAME,C_RaceWhite, C_RaceBlack, C_RaceOther,C_RaceUnknown,"
            "C_HispanicYES,C_HispanicNO,C_HispanicUnk,C_RaceWhite,PUIsTotal"
        ),
        returnGeometry="false",
        outSR="4326",
        f="json",
    )
    df = get_funx.get_data(url, payload, query_type="gis")
    df = clean_fl(df)
    write_fl(df)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store", type=get_funx.input_date)
    args = parser.parse_args()
    if args.d is not None:
        query_date = args.d
    elif args.d is None:
        query_date = get_funx.set_query_date()
    main(query_date)
