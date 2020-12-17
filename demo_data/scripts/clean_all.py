import clean_fl
import clean_ga
import clean_in
import clean_va
import clean_wi
import clean_il
import get_funx
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", action="store_true", default=False)
    args = parser.parse_args()

    try:
        clean_fl.main()
    except:
        print("Did not collect fl data.")
        pass
    clean_ga.main()
    try:
        clean_il.main()
    except:
        print("Did not collect il data.")
        pass
    try:
        clean_in.main()
    except:
        print("Did not collect in data.")
        pass
    try:
        clean_va.main()
    except:
        print("Did not collect va data.")
        pass
    clean_wi.main()

    if args.m:
        missing = get_funx.get_missing_dates()
        for state, dates in missing.items():
            if len(dates) == 0:
                continue
            dates = sorted(dates)
            rv = [date.strftime("%Y-%m-%d") for date in dates]
            if state in ["fl", "in"]:
                print("missing dates for {s}:".format(s=state), *rv)
            if state == "il":
                for date in dates:
                    clean_il.main(report_date=date)
            if state == "ga":
                for date in dates:
                    clean_ga.main(query_date=date.strftime("%Y-%m-%d"))
                print("Collected GA data for missing dates:", *rv)
            if state == "va":
                for date in dates:
                    clean_va.main(QUERY_DATE=date.strftime("%Y-%m-%d"))
                print("Collected VA data for missing dates:", *rv)
            if state == "wi":
                for date in dates:
                    clean_wi.main(query_date=date.strftime("%Y-%m-%d"))
                print("Collected data for missing dates for wi:", *rv)
    return


if __name__ == "__main__":
    main()
