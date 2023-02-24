from datetime import datetime
import time
from collections import namedtuple
from pathlib import Path

import pandas as pd
import streamlit as st
import validators





CheckResult = namedtuple("CheckResult", "is_valid error_message")


class ColumnChecker:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def _iterate_column(self, column_name: str):
        return self.df[column_name].to_list()

    def _get_date_error(self, date):
        try:
            datetime.fromisoformat(date)
        except ValueError:
            return f"Date: {date} does not follow YYYY-mm-dd format."

    def _get_price_unit_error(self, unit):
        allowed_units = {'M2', 'Skiva', 'Styck', 'Pallet', 'Paket', 'Säck', 'Storsäck', 'KG'}

        if unit not in allowed_units:
            return f"Row: {i} Unit: {unit} is not any of allowed units: {allowed_units}"

    def _get_price_error(self, price):
        try:
            float(price)
        except ValueError:
            return f"{price} cannot be processed to float"

    def _get_currency_error(self, currency):
        if currency != "SEK":
            return f"{currency} is not equal to SEK"

    def _get_URL_error(self, url):
        if not validators.url(url):
            return f"Invalid url: {url}"

    def _get_brand_error(self, column_name):
        allowed_brand = set("Dalapro Weber Isover Gyproc".split())
        for brand in self._iterate_column(column_name):
            if brand not in allowed_brand:
                return f"Brand {brand} is invalid. Must be one of: {allowed_brand}"

    def run_all_checks(self):
        get_error_list = {
            "Price": self._get_price_error,
            "Price_unit": self._get_price_unit_error,
            "Currency": self._get_currency_error,
            "Article_number": self._get_article_number_error,
            "URL": self._get_URL_error
            "Brand": self._get_brand_error,
        }

        for column_name, get_error in get_error_list.items():
            for value in self._iterate_column(column_name):
                error = get_error(value)
                if error:
                    yield error


after_qa = st.file_uploader("Upload single file containing all scraped rows after QA.", type=["csv"])
column_checker = ColumnChecker(_read_csv(after_qa))
for column_name, check_error in column_checker.run_all_checks():
    st.write()
    feedback = (f"Invalid value: {check_error}" if check_error else "Success") + f" for column: {column_name}"
    st.write(feedback)
