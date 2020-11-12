# clean_florida_test.py
import tabula
import pandas as pd
import argparse
from datetime import datetime
from pathlib import Path


def get_loc():
    ### get from user specific location on pdf
    ### to extract content
    # Option to try with most recent location inputs
    try_prev = input("Use most recent location inputs? y/n: ")
    root_path = Path(__file__).parent.parent.absolute()
    prev_file = root_path / "reference_files" / "fl_content_loc_info.csv"
    old_entries = pd.read_csv(prev_file)
    old_entries["date"] = pd.to_datetime(old_entries["date"])
    while try_prev.lower() not in ["y", "yes", "n", "no"]:
        try_prev = input(
            "Use most recent location inputs? ** y/n ** (cancel w/ cntrl+c): "
        )
    if try_prev.lower() in ["y", "yes"]:
        old_entries["date"] = pd.to_datetime(old_entries["date"])
        prev_loc = old_entries[old_entries["date"] == max(old_entries["date"])]
        prev_loc = prev_loc.drop(columns="date")
        return prev_loc
    # option to enter new input data
    elif try_prev.lower() in ["n", "no"]:
        try_2prev = input("Use second most recent location inputs? y/n: ")
        while try_2prev not in ["y", "yes", "n", "no"]:
            try_2prev = input(
                "Use second recent location inputs? ** y/n ** (cancel w/ cntrl+c): "
            )
        if try_2prev.lower() in ["yes", "y"]:
            old_entries["date"] = pd.to_datetime(old_entries["date"])
            prev_loc = old_entries[
                old_entries["date"]
                == max(
                    old_entries[old_entries["date"] != max(old_entries["date"])]["date"]
                )
            ]
            return prev_loc
        elif try_2prev.lower() in {"no", "n"}:
            name_loc = [None] * 4
            table_loc = [None] * 4
            date_loc = [None] * 4
            input_loc = [name_loc, table_loc, date_loc]
            # set user prompts
            county_prm = ["county_name", "table", "date_loc"]
            loc_prm = ["left", "width", "top", "height"]
            # collect location information (in points from top left corner)
            for i in range(0, len(county_prm)):
                for j in range(0, len(loc_prm)):
                    input_loc[i][j] = float(
                        input(county_prm[i] + " " + loc_prm[j] + ": ")
                    )
            # convert to df
            left = [name_loc[0], table_loc[0], date_loc[0]]
            width = [name_loc[1], table_loc[1], date_loc[1]]
            top = [name_loc[2], table_loc[2], date_loc[2]]
            height = [name_loc[3], table_loc[3], date_loc[3]]
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            today_loc = pd.DataFrame(
                data={
                    "left": left,
                    "width": width,
                    "top": top,
                    "height": height,
                    "content_type": county_prm,
                    "date": date,
                },
            )
            # update location info file
            old_entries = old_entries.append(today_loc, ignore_index=True)
            old_entries.to_csv(
                root_path / "reference_files/fl_content_loc_info.csv", index=False
            )
            # return the url and today's location info
            return today_loc.drop(columns="date")


def get_pdf_fl(file, pages=None):
    ### from get_loc() passes url and location info to tablua.read_pdf
    ### returns a list of dfs from each county page on the fl report
    loc_df = get_loc()
    # format location data to pass to read_pdf
    name_loc = (
        loc_df[loc_df["content_type"] == "county_name"]
        .drop(columns="content_type")
        .values[0]
    )
    table_loc = (
        loc_df[loc_df["content_type"] == "table"].drop(columns="content_type").values[0]
    )
    date_loc = (
        loc_df[loc_df["content_type"] == "date_loc"]
        .drop(columns="content_type")
        .values[0]
    )
    # format pages parameter to pass to read_pdf
    if pages == None:
        pages = str()
        for i in range(3, 136, 2):
            pages = pages + str(i) + ","
        pages = pages[:-1]
    # run tablua.read_pdf, extra table info from pdf
    dfs = tabula.read_pdf(
        file,
        pages=pages,
        multiple_tables=True,
        stream=True,
        area=[
            [
                name_loc[2],
                name_loc[0],
                name_loc[2] + name_loc[3],
                name_loc[0] + name_loc[1],
            ],
            [
                table_loc[2],
                table_loc[0],
                table_loc[2] + table_loc[3],
                table_loc[0] + table_loc[1],
            ],
            [
                date_loc[2],
                date_loc[0],
                date_loc[2] + date_loc[3],
                date_loc[0] + date_loc[1],
            ],
        ],
    )
    print("DL successful: {}".format(isinstance(dfs, list)))
    # returns list of dfs
    return dfs


def get_n_combn_fl(file, dfs=None):
    ### gets list of dfs from get_pdf_fl, combines into a single df
    ### returns df and a df of dates
    try:
        if dfs == None:
            dfs = get_pdf_fl(file)
    except Exception as exception:
        print("DL error, try different inputs")
        print(exception)
        return
    df = pd.DataFrame()
    date = []
    rv = int()
    for i in range(1, len(dfs), 3):
        try:
            rv = i
            if dfs[i]["Cases"].dtype == "object":
                dfs[i]["Cases"] = pd.to_numeric(dfs[i]["Cases"].str.replace(",", ""))
            dfs[i] = dfs[i].assign(County_name=dfs[i - 1].columns[0])
            df = df.append(dfs[i])
            date.append(dfs[i + 1].columns[0])
        except:
            print("Formatting failed on iteration: {}".format(rv))
            print(dfs[rv - 1])
            print(dfs[rv])
            print(dfs[rv + 1])
            return
    return (df, date)


def get_n_clean_fl(file=str(), df=None, date=None):
    ### gets df of county info from get_n_combn_fl
    ### cleans to match data entry sheet
    ### check that dates are all same
    ### returns cleaned df
    def inner(file=str(), df=None, date=None):
        if df is None and date is None:
            df, date = get_n_combn_fl(file)

        try:
            df = df.groupby(["County_name", "Race, ethnicity"]).sum().unstack()
        except:
            print("Error, try different inputs")
            df, date = get_n_combn_fl(file)

        if all(x == date[0] for x in date):
            date = datetime.strptime(date[0], "%b %d, %Y").strftime("%Y-%m-%d")
        elif not all(x == date[0] for x in date):
            raise Exception("Date error; not all same")
        df = df["Cases"]
        df.columns = df.columns.str.replace(" ", "_")
        df = df.rename(columns=str.lower)
        df = df.assign(date=date)
        df = df.assign(asian="-")
        df = df.assign(american_indian="-")
        df = df.assign(nh_pi="-")
        df = df.assign(two_plus="-")

        df = df[
            [
                "date",
                "white",
                "black",
                "asian",
                "american_indian",
                "nh_pi",
                "two_plus",
                "other",
                "unknown_race",
                "hispanic",
                "non-hispanic",
                "unknown_ethnicity",
                "total",
            ]
        ]
        return df

    try:
        df = inner(file=file, df=df, date=date)
    except:
        print(df)
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


def main():
    root_path = Path(__file__).parent.parent.absolute()
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-s", "--single", help="run script on single file")
    group.add_argument(
        "-b" "--batch",
        help="runs script on a batch of files (default reference file in dir)",
        type=Path,
        const=root_path / "reference_files/old_fl_dates.csv",
        nargs="?",
    )
    args = parser.parse_args()
    if args.single is not None:
        file = args.single
        df = get_n_clean_fl(file=file)
        write_fl(df)
        return
    elif args.b__batch is not None:
        file_paths = pd.read_csv(root_path / "reference_files/old_fl_dates.csv")
        for i in range(0, file_paths.shape[0]):
            df = get_n_clean_fl(file_paths["url"].iloc[i])
            write_fl(df)
        return


if __name__ == "__main__":
    main()