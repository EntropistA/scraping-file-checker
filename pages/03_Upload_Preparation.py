import streamlit as st

import common

ALLOWED_BRANDS = tuple("Dalapro Weber Isover Gyproc".split())
SCRAPING_URLS_HEADERS_ORDER = [
    'Date',
    'Time',
    'PIM_name',
    'Origin',
    'Competitor',
    'Category',
    'Name',
    'Price',
    'Price_unit',
    'Currency',
    'Article_number',
    'URL',
    'Brand'
    ]


st.title("Upload Preparation")

file = common.check_proper_name_file_input("output_concatenated", "csv")


def get_duplicates_message(duplicate_number: int) -> str:
    if duplicate_number:
        return f"{row_number_change} duplicate" + ("s" if row_number_change > 1 else "") + " were found and deleted"
    else:
        return "No duplicates found"


def get_remaining_rows_message(remaining_rows: int) -> str:
    return f"\n{scraping_output_concat.shape[0]} rows without duplicates are split below"


if file:
    # Subset is needed because Time column may differ
    before_dropping_duplicates = common.read_csv(file)
    scraping_output_concat = before_dropping_duplicates.drop_duplicates(subset=["URL", "Article_number"])

    row_number_change = before_dropping_duplicates.shape[0] - scraping_output_concat.shape[0]
    st.text(get_duplicates_message(row_number_change) + get_remaining_rows_message(scraping_output_concat.shape[0]))

    for brand in ALLOWED_BRANDS:
        matching_brand = scraping_output_concat["Brand"] == brand
        brand_filtered = scraping_output_concat[matching_brand][SCRAPING_URLS_HEADERS_ORDER]

        st.download_button(
            label=f"Download CSV for brand: {brand}",
            data=brand_filtered.to_csv().encode('utf-8'),
            file_name=f'{brand}.csv',
            mime='text/csv',
        )
