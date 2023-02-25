import streamlit as st

import common

st.header("Upload Preparation")

file = st.file_uploader("Upload single file containing all brands", type=[".csv"])

scraping_output_concat = common.read_csv(file)

matching_brand = scraping_output_concat["Brand"] == brand
brand_filtered = scraping_output_concat[matching_brand][common.SCRAPING_URLS_HEADERS_ORDER]
brand_file_path = PathManager.get_created_prepared_file_path(brand)