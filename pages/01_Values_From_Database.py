import streamlit as st

import common

from data_validators import ScrapingUrlsSummary, DatabaseColumnChecker

proper_filename_prefix = "scraping_urls"
proper_filename_suffix = "csv"
st.title(f"Check {proper_filename_prefix}.{proper_filename_suffix} before starting scraper")
file = common.check_proper_name_file_input(proper_filename_prefix, proper_filename_suffix)

if file:
    df = common.read_csv(file)

    st.header("File Summary")
    st.text(ScrapingUrlsSummary(df).summarize_all())

    st.header("File Checks")
    database_checker = DatabaseColumnChecker(df)
    for column_check_result in database_checker.check_all():
        message_header = f"{column_check_result.column_name}: {column_check_result.message}"
        if column_check_result.is_success:
            st.success(message_header, icon="✅")
        else:
            st.warning(message_header, icon="⚠️")
    database_checker.no_mismatch_between_same_url_rows()
