import streamlit as st

import common
from Checkers import ScrapingUrlsSummary, FromFileColumnsChecker, ScrapedColumnChecker

proper_filename_prefix = "output_concatenated"

st.header(f"Check {proper_filename_prefix}.csv after QA")
file = st.file_uploader(f"Upload {proper_filename_prefix}.csv", type=["csv"])

if file:
    if not file.name.startswith(proper_filename_prefix):
        st.write(f"Invalid filename (Expected {proper_filename_prefix} prefix).")

    df = common.read_csv(file)

    st.subheader("File Summary")
    st.text(ScrapingUrlsSummary(df).summarize_all())

    st.subheader("File Checks")
    for column_check_result in FromFileColumnsChecker(df).check_all():
        message_header = f"{column_check_result.column_name}: {column_check_result.message}"
        if column_check_result.is_success:
            st.success(message_header, icon="✅")
        else:
            st.warning(message_header, icon="⚠️")

    st.subheader("Scraping Checks")
    for column_check_result in ScrapedColumnChecker(df).check_all():
        message_header = f"{column_check_result.column_name}: {column_check_result.message}"
        if column_check_result.is_success:
            st.success(message_header, icon="✅")
        else:
            st.warning(message_header, icon="⚠️")
