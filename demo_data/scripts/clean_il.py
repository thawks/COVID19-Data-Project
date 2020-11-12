# clean_il.py
# author: Tyler Hawks
###############
import requests
import pandas as pd
import numpy as np
from datetime import date, datetime
from pathlib import Path

##
def get_ill():
    ### function to request json file from il doh
    ### api requires county by county requests, loops through list of names
    ### prints status codes for any fails
    ### returns list of request objects
    # read in county list
    path = Path(__file__).parent.parent.absolute()
    counties = pd.read_csv(path / "reference_files" / "il_county_list.csv")["County"]
    # create list to hold reqests data
    r_list = [None] * len(counties)
    # set URL
    url = "https://idph.illinois.gov/DPHPublicInformation/api/COVID/GetCountyDemographics?"
    # make requests
    for i in range(0, len(counties)):
        param = {"countyName": "{}".format(counties[i])}
        r_list[i] = requests.get(url, param)
    for i in range(0, len(r_list)):
        if r_list[i].status_code != 200:
            print(
                "Non-200 status code for {county} \n\t Code: {code}".format(
                    county=counties[i], code=r_list[i].status_code
                )
            )
    return r_list


##
def clean_ill(r):
    ### function to clean json data from get_ill()
    ### takes list of requests objects, extracts desired info
    ### and cleans to match data entry sheet
    ### returns formated df
    df = pd.DataFrame()
    # loop through list of requests object
    for i in range(0, len(r)):
        # extract demographic data, made demo df
        demo = r[i].json()["county_demographics"][0]["demographics"]["race"]
        demo_df = pd.json_normalize(demo).drop(columns=["tested", "color"])
        # extract date data
        year = r[i].json()["lastUpdatedDate"]["year"]
        month = r[i].json()["lastUpdatedDate"]["month"]
        day = r[i].json()["lastUpdatedDate"]["day"]
        # extract total case count
        total = r[i].json()["county_demographics"][0]["confirmed_cases"]
        total = {"description": "Total", "count": total}
        # extract county name
        name = r[i].json()["county_demographics"][0]["County"]
        # update demo df
        demo_df = demo_df.append(total, ignore_index=True)
        demo_df = demo_df.assign(county_name=name)
        demo_df = demo_df.assign(date=date(year, month, day))
        # combine to single df
        df = df.append(demo_df)
    # pivot data to match entry sheet
    df = df.groupby(["date", "county_name", "description"]).sum().unstack()
    # remove multiindex, clean
    df = df["count"]
    df.columns = df.columns.str.lower()
    # add, reorder columns to match data entry sheet
    df = df.replace(np.nan, "-")
    df = df.assign(two_plus="-")
    df = df.assign(non_hispanic="-")
    df = df.assign(eth_unknown="-")
    df = df[
        [
            "white",
            "black",
            "asian",
            "ai/an**",
            "nh/pi*",
            "two_plus",
            "other",
            "left blank",
            "hispanic",
            "non_hispanic",
            "eth_unknown",
            "total",
        ]
    ]
    print(
        "Data collected from {count}/102 Illinois counties on {date}".format(
            count=df.shape[0], date=df.index[0][0].strftime("%Y-%m-%d")
        )
    )
    return df


##
def write_ill(df):
    # takes formated df from clean_ill()
    # writes to my illinois directory
    path = Path(__file__).parent.parent.absolute() / "cleaned_data" / "il"
    date = df.index[0][0].strftime("%Y-%m-%d")
    df.to_csv(path / ("IL_COVID-19_DEMOS_" + date + ".csv"))

def main():
    r = get_ill()
    df = clean_ill(r)
    write_ill(df)
if __name__ == "__main__":
    main()
