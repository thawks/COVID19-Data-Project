# clean_il_dev.py
# author: Tyler Hawks
###############
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
import argparse


def get_ill(API=str()):
    r = requests.get(url=API)
    raw_df = pd.DataFrame(r.json())
    return raw_df


def clean_ill(raw_df):
    df = raw_df[["CountyName", "confirmed_cases", "deaths"]]
    df = df[~df["CountyName"].isin(("Chicago", "Illinois"))]
    df.columns = ["county", "tstpos_", "mort_"]
    df = df.set_index("county")
    df = df.assign(pb_pos_=0, pbmort_=0)
    df = df[["tstpos_", "pb_pos_", "mort_", "pbmort_"]]
    date = datetime.now().date().strftime("%m%d%y")
    clean_df = df.rename(columns=lambda c: "".join((c, date)))
    return clean_df


def write_ill_new(clean_df, reportDate):
    # takes formatted df from clean_ill() and reportDate from query
    # writes to my illinois directory
    path = Path(__file__).parent.parent.absolute() / "cleaned_data" / "il"
    reportDate = reportDate.strftime("%Y-%m-%d")
    clean_df.to_csv(path / ("IL_COVID-19_DEMOS_" + reportDate + ".csv"))
    print(
        "Data collected from {count}/102 Illinois counties on {date}".format(
            count=clean_df.shape[0], date=reportDate
        )
    )

def parse_date_arg(str):
    reportDate = datetime.strptime(str, "%Y-%m-%d")
    return reportDate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        action="store",
        help="pass date to query records from. if 'none', defaults to today",
        type=parse_date_arg,
    )
    args = parser.parse_args()
    if args.d is None:
        url = (
            "https://idph.illinois.gov/DPHPublicInformation/"
            "api/COVIDExport/GetCountyTestResults"
        )
        reportDate = datetime.now().date()
    else:
        reportDate = args.d
        url = (
            "https://idph.illinois.gov/DPHPublicInformation/"
            "api/COVIDExport/GetCountyHistoricalTestResults?reportDate={reportDate}".format(
                reportDate=reportDate.strftime("%m/%d/%Y")
            )
        )
    r = get_ill(API=url)
    df = clean_ill(r)
    write_ill_new(df, reportDate)
    return df


if __name__ == "__main__":
    df = main()
