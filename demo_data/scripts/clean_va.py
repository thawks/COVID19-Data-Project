# clean_va
import pandas as pd
import requests
import get_funx
from pathlib import Path
import argparse


def clean_va_total(df):
    df["total_cases"] = df["total_cases"].astype("int64")
    df = df.groupby(["vdh_health_district"]).sum()
    return df


def clean_va_demo(df):
    df["report_date"] = pd.to_datetime(df["report_date"], format="%Y-%m-%d")
    df["number_of_cases"] = df["number_of_cases"].astype(dtype="int64")
    df = df.pivot(
        index="health_district_or_health",
        columns="race_and_ethnicity",
        values="number_of_cases",
    )
    df = df.assign(Native_Hawaiian="-")
    df = df.assign(Not_latino="-")
    df = df.assign(Not_reported="-")
    df = df[
        [
            "White",
            "Black",
            "Asian or Pacific Islander",
            "Native American",
            "Native_Hawaiian",
            "Two or more races",
            "Other Race",
            "Not Reported",
            "Latino",
            "Not_latino",
            "Not_reported",
        ]
    ]
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(" ", "_")
    return df


def write_va(df, query_date):
    clean_df_path = Path(__file__).parent.parent.absolute()
    clean_df_path = clean_df_path / "cleaned_data" / "va"
    query_date = query_date.strftime("%Y-%m-%d")
    df.to_csv(clean_df_path / ("VA_COVID-19_DEMOS_" + query_date + ".csv"))
    print(
        "Collected data for {count} health districts in Virginia for {date}".format(
            count=df.shape[0], date=query_date
        )
    )
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store", type=get_funx.input_date)
    args = parser.parse_args()
    HEADER = {"X-App-Token": "P7WdgPRM1h3IfEa2VJBZ7XtTX"}
    QUERY_TYPE = "socrata"
    DATE_TEMPLATE = "${date}T00:00:00.000"
    if args.d is None:
        QUERY_DATE = get_funx.set_query_date()
    else:
        QUERY_DATE = get_funx.set_query_date(args.d)

    def get_demo():
        url = "https://data.virginia.gov/resource/9sba-m86n.json"
        select = "report_date, health_district_or_health, race_and_ethnicity, number_of_cases"
        payload = get_funx.set_payload(
            query_type=QUERY_TYPE,
            query_key="report_date",
            date_template=DATE_TEMPLATE,
            query_date=QUERY_DATE,
            header=HEADER,
            select=select,
        )
        demo_df = get_funx.get_data(
            url=url, params=payload[0], headers=payload[1], query_type=QUERY_TYPE
        )
        demo_df = clean_va_demo(demo_df)
        return demo_df

    def get_total():
        url = "https://data.virginia.gov/resource/bre9-aqqr.json"
        select = "report_date, vdh_health_district, total_cases"
        payload = get_funx.set_payload(
            query_type=QUERY_TYPE,
            query_key="report_date",
            date_template=DATE_TEMPLATE,
            query_date=QUERY_DATE,
            header=HEADER,
            select=select,
        )
        total_df = get_funx.get_data(
            url=url, params=payload[0], headers=payload[1], query_type=QUERY_TYPE
        )
        total_df = clean_va_total(total_df)
        return total_df

    demo_df = get_demo()
    total_df = get_total()
    df = demo_df.join(total_df, on="health_district_or_health", rsuffix="_total")
    df = df[df["total_cases"].notna()]

    write_va(df, QUERY_DATE)
    return


if __name__ == "__main__":
    main()
