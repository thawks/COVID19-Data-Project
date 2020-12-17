from pathlib import Path
from datetime import datetime, timedelta


def find_demo_path():
    # find root of demo_data directory
    dir = Path.cwd()
    while dir.name != "demo_data":
        dir = dir.parent
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
