import streamlit as st

import common
from data_validators import ScrapedColumnChecker

proper_filename_prefix = "output_concatenated"
proper_filename_suffix = "csv"

st.title(f"Check {proper_filename_prefix}.{proper_filename_suffix} for QA")
file = common.check_proper_name_file_input(proper_filename_prefix, "csv")

if file:
    df = common.read_csv(file)

    st.header("Scraping Checks")
    for column_check_result in ScrapedColumnChecker(df).check_all():
        message_header = f"{column_check_result.column_name}: {column_check_result.message}"
        if column_check_result.is_success:
            st.success(message_header, icon="✅")
        else:
            st.warning(message_header, icon="⚠️")
