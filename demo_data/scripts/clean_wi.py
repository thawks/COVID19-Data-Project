# clean_wi.py
import pandas as pd
import get_funx
import argparse
from pathlib import Path


def clean_wi(df):
    df.columns = [
        "name",
        "date",
        "total_cases",
        "white",
        "other",
        "race_unknown",
        "hispanic",
        "non-hispanic",
        "eth_unknown",
        "american_indian",
        "asian",
        "black",
    ]
    df["date"] = pd.to_datetime(df["date"], unit="ms").dt.date
    df = df.assign(nh_pi="-")
    df = df.assign(two_plus="-")
    # reorder and rename to match entrys sheet
    cor_order = [
        "date",
        "name",
        "white",
        "black",
        "asian",
        "american_indian",
        "nh_pi",
        "two_plus",
        "other",
        "race_unknown",
        "hispanic",
        "non-hispanic",
        "eth_unknown",
        "total_cases",
    ]
    df = df[cor_order]
    # replace -999s with "-"
    df = df.replace(to_replace=-999, value="-")
    #  sort values by county
    df = df.sort_values(by=["name"])
    return df


def write_wi(df):
    if (x == df["date"].iloc[0] for x in df["date"]):
        date = df["date"].iloc[0].strftime("%Y-%m-%d")
    else:
        date = "unknown"
        raise Warning("warning: datestamps not all same")
    path = Path(__file__).parent.parent.absolute() / "cleaned_data" / "wi"
    df.to_csv(path / ("WI_COVID-19_DEMOS_" + date + ".csv"))
    print(
        "{count} counties added from Wisconsin dated {date}.".format(
            count=df.shape[0], date=date
        )
    )


def main(query_date=None):
    if query_date is None:
        query_date = get_funx.set_query_date()

    url = (
        "https://dhsgis.wi.gov/server/rest/services/DHS_COVID19/COVID19_WI/"
        "MapServer/12/query?"
    )
    date_template = (
        "DATE >= TIMESTAMP '${min} 00:00:00' AND DATE <= TIMESTAMP '${max} 00:00:00'"
    )
    outFields = (
        "NAME,DATE,POSITIVE,POS_WHT,POS_MLTOTH,POS_UNK,POS_E_HSP,"
        "POS_E_NHSP,POS_E_UNK,POS_AIAN,POS_ASN,POS_BLK"
    )

    payload = get_funx.set_payload(
        query_key="where",
        query_type="gis",
        date_template=date_template,
        query_date=query_date,
        outFields=outFields,
        outSR="4326",
        f="json",
    )
    try:
        df = get_funx.get_data(url, payload, query_type="gis")
        assert df.shape != (0,0), "Empty df"
        df = clean_wi(df)
    except AssertionError as error:
        print(error)
        print("WI data for {d} not available.".format(d=query_date))
        pass
    except KeyError as key:
        print(key)
        print("WI data for {d} not available.".format(d=query_date))
        pass
    else:
        write_wi(df)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", action="store", type=get_funx.input_date)
    args = parser.parse_args()
    if args.d is None:
        query_date = get_funx.set_query_date()
    else:
        query_date = get_funx.set_query_date(args.d)
    main(query_date)
