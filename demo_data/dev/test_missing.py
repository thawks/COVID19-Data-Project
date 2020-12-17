from demo_data.dev.check_missing_dates import get_missing_dates
from demo_data.scripts import clean_va
from demo_data.scripts import get_funx

missing = get_missing_dates()

for date in missing['va']:

    QUERY_DATE = get_funx.set_query_date(date.strftime("%Y-%m-%d"))

    HEADER = {"X-App-Token": "P7WdgPRM1h3IfEa2VJBZ7XtTX"}
    QUERY_TYPE = "socrata"
    DATE_TEMPLATE = "${date}T00:00:00.000"

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
        demo_df = clean_va.clean_va_demo(demo_df)
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
        total_df = clean_va.clean_va_total(total_df)
        return total_df

    demo_df = get_demo()
    total_df = get_total()
    df = demo_df.join(total_df, on="health_district_or_health", rsuffix="_total")
    df = df[df["total_cases"].notna()]

    df.to_csv("test" + date.strftime("%Y-%m-%d") + ".csv")