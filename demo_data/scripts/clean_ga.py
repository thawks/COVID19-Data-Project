# clean_ga.py
import pandas as pd
import get_funx
import argparse
from pathlib import Path


def clean_ga(df):
    ref_dir = (
        Path(__file__).parent.parent.absolute() / "reference_files/ga_counties.csv"
    )
    counties = pd.read_csv(ref_dir)
    df.columns = df.columns.str.replace("attributes.", "")
    df.columns = df.columns.str.replace("C_", "")
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace("race", "")
    df.columns = df.columns.str.replace("eth", "")
    df = df.assign(ai_an="-", nh_pi="-", two_plus="-")
    df["datestamp"] = pd.to_datetime(df["datestamp"], unit="ms").dt.date
    df = df[
        [
            "datestamp",
            "county",
            "wh",
            "bl",
            "as",
            "ai_an",
            "nh_pi",
            "two_plus",
            "oth",
            "his",
            "nonhis",
            "unk",
            "cum",
        ]
    ]
    df = df.sort_values(by="county")
    df = df[df["county"].isin(counties["county"].to_list())]
    return df


def write_ga(df):
    if (x == df["datestamp"].iloc[0] for x in df["datestamp"]):
        date = df["datestamp"].iloc[0].strftime("%Y-%m-%d")
    else:
        date = "unknown"
        raise Warning("warning: datestamps not all same")
    path = Path(__file__).parent.parent.absolute() / "cleaned_data/ga"
    df.to_csv(path / ("GA_COVID-19_DEMOS_" + date + ".csv"))
    print(
        "{count} counties added from Georgia dated {date}.".format(
            count=df.shape[0], date=date
        )
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store", type=get_funx.input_date)
    args = parser.parse_args()
    if args.d == None:
        query_date = get_funx.set_query_date()
    else:
        query_date = get_funx.set_query_date(args.d)

    url = (
        "https://services7.arcgis.com/Za9Nk6CPIPbvR1t7/arcgis/"
        "rest/services/Georgia_PUI_Data_Download/FeatureServer/0/query?"
    )
    date_template = "DATESTAMP between '${min}' and '${max}'"
    payload = get_funx.set_payload(
        query_type="gis",
        date_template=date_template,
        query_date = query_date,
        query_key = "where",
        outFields = (
            "COUNTY, DATESTAMP, C_New, C_Cum, C_RaceBl, C_RaceAs, C_RaceOth,"
            "C_RaceUnk, C_His, C_NonHis, C_EthUnk, C_RaceWh"
        ),
        outSR = "4326",
        f = "json"
    )
    df = get_funx.get_data(url, payload, query_type = "gis")
    df = clean_ga(df)
    write_ga(df)
    return


if __name__ == "__main__":
    main()
