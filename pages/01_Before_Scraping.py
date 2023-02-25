import streamlit as st

import common

from data_validators import ScrapingUrlsSummary, FromFileColumnsChecker

proper_filename = "scraping_df.csv"

st.header(f"Check {proper_filename} before starting scraper")
file = st.file_uploader(f"Upload {proper_filename}", type=["csv"])

if file:
    if file.name != proper_filename:
        st.write(f"Invalid filename (Expected {proper_filename}). QA check is available on the other page.")

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
