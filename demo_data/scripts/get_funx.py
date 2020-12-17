import pandas as pd
import requests
from datetime import datetime, timedelta
from string import Template
from pathlib import Path
import sys


def find_demo_path():
    # find root of demo_data directory
    dir = Path(__file__)
    paths = [path.match("demo_data") for path in dir.parents]
    try:
        assert any(paths), "Error, demo_data not in path:"
    except AssertionError as error:
        print(error, dir)
        sys.exit()
    else:
        for path in dir.parents:
            dir = path
            if dir.match("demo_data"):
                break
    return dir


def get_missing_dates():
    demo_root = find_demo_path()
    cleaned_data_path = demo_root / "cleaned_data"
    dates = {}
    for dir in cleaned_data_path.iterdir():
        state = dir.name
        if dir.name.startswith("."):
            continue
        else:
            for file in dir.iterdir():
                if file.name.startswith("."):
                    continue
                split_stem = file.stem.split("_")
                if split_stem[0].lower() == "reformatted":
                    state = "in"
                if split_stem[0].lower() == state or state == "in":
                    date = datetime.strptime(split_stem[-1], "%Y-%m-%d")
                    if state not in dates.keys():
                        dates[state] = [date]
                    elif state in dates.keys():
                        dates[state].append(date)

    missing = {}
    for state, values in dates.items():
        min_date = min(values)
        max_date = max(values)
        dif_dates = max_date - min_date
        date_entries = set(values)
        date_range = set([max_date - timedelta(days=x) for x in range(dif_dates.days)])
        missing[state] = date_range.difference(date_entries)
    return missing


def input_date(string):
    if string != "0":
        rv = datetime.strptime(string, "%Y-%m-%d")
    elif string == "0":
        rv = int(string)
    return rv


def get_data(url, params, headers=None, query_type = str()):
    if headers == None:
        r = requests.get(url, params)
    else:
        r = requests.get(url, params=params, headers=headers)
    if r.status_code != 200:
        print(r.status_code)
        print(r.content)
    if query_type == "gis":
        df = pd.json_normalize(r.json()["features"])
    if query_type == "socrata":
        df = pd.read_json(r.content)
    return df


def set_query_date(
    query_date=None,
    query_format="%Y-%m-%d",
):
    # default query results in todays date, but can specify
    # a date as an optional parameter.
    if query_date == None:
        query_date = datetime.now()
    if isinstance(query_date, str):
        query_date = datetime.strptime(query_date, query_format)
    query_date = query_date.replace(hour=0, minute=0, second=0, microsecond=0)
    return query_date


def format_date_payload(
    query_type=str(),
    date_template=str(),
    query_date=None,
    query_format="%Y-%m-%d",
):
    # date_mods is a dict corresponding to substitution variables for template,
    # date_mods can also be a function that return a dict
    # date_format takes a string written in string.Template format, and the terms to pass to substitute
    # date_format_key take a str to pass to requests.get as the key for the date query
    # query_date defaults to today, otherwase can pass a string that will be converted
    date_format = Template(date_template)
    qtype_opts = {"socrata", "gis"}
    if query_type not in qtype_opts:
        raise ValueError("Invalid query type")
    if query_type == "socrata":
        query_date = set_query_date(query_date, query_format).strftime("%Y-%m-%d")
        date_mods = {"date": query_date}
    if query_type == "gis":
        min_query_date = set_query_date(query_date, query_format).strftime("%Y-%m-%d")
        max_query_date = (
            set_query_date(query_date, query_format) + timedelta(days=1)
        ).strftime("%Y-%m-%d")
        date_mods = {"min": min_query_date, "max": max_query_date}
    formatted_date = date_format.substitute(**date_mods)
    return formatted_date


def set_payload(
    query_key=str(),
    query_type=str(),
    date_template=str(),
    query_date=None,
    query_format="%Y-%m-%d",
    header=None,
    **more_params
):
    if query_date != 0:
        date_query = format_date_payload(
            query_type, date_template, query_date, query_format
        )
        params = {query_key: date_query}
    elif query_type == 0:
        params = {}
    if query_type == "socrata":
        for key, val in more_params.items():
            key = "${0}".format(key)
            params[key] = val
    elif query_type == "gis":
        for key, val in more_params.items():
            params[key] = val
    if header is not None:
        return params, header
    else:
        return params
