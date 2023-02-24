import string
from collections import Counter, namedtuple
from datetime import datetime
from typing import Iterator

import streamlit as st
import pandas as pd
import validators

import common


class ScrapingUrls:
    def __init__(self, scraping_urls: pd.DataFrame):
        self.scraping_urls = scraping_urls


class ScrapingUrlsSummary(ScrapingUrls):
    def _get_domain_counter(self):
        domain_list = self.scraping_urls["URL"].apply(common.get_domain).to_list()
        counter = Counter(domain_list)
        sorted_counter = dict(counter.most_common(len(counter)))
        return sorted_counter

    def _summarize_domain(self):
        summary = ""
        for domain, count in self._get_domain_counter().items():
            summary += f"{domain}: {count}\n"
        return summary

    def _get_category_unique_value_list(self) -> {str: list}:
        category_column_list = "Brand Category Origin Currency".split()
        return {category: self.scraping_urls[category].unique() for category in category_column_list}

    def _summarize_category_columns(self) -> str:
        summary = ""
        for category, value_list in self._get_category_unique_value_list().items():
            summary += f"{category}: {', '.join(value_list)}\n"
        return summary

    def summarize_all(self):
        summary_section_mapping = {
            "Domain": self._summarize_domain,
            "Category Columns": self._summarize_category_columns
        }
        summarization = ""
        for summary_name, summary in summary_section_mapping.items():
            summarization += summary_name + "\n" + summary() + "\n"
        return summarization


ColumnCheckResult = namedtuple("ColumnCheckResult", "column_name is_success message")


class CheckScrapingUrlsFile(ScrapingUrls):
    @staticmethod
    def is_valid_date(date: str) -> bool:
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_time(time: str) -> bool:
        try:
            datetime.strptime(time, "%H:%M:%S")
            return True
        except ValueError:
            return False

    @staticmethod
    def _is_valid_text(text: str):
        space = " "
        nbsp = " "
        special_characters = space + nbsp + string.punctuation + "®"
        return all(c.isalnum() or c in special_characters for c in text)

    def is_valid_pim_name(self, pim_name: str) -> bool:
        return self._is_valid_text(pim_name)

    @staticmethod
    def is_valid_origin(origin: str) -> bool:
        return origin in ["Saint-Gobain", "Competition"]

    def is_valid_competitor(self, competitor: str) -> bool:
        return self._is_valid_text(competitor)

    @staticmethod
    def is_valid_category(category: str) -> bool:
        return all(c.isalpha() or c in "/ -" for c in category)

    # def _is_valid_name(self, name: str) -> bool:
    #     return self.is_valid_text(name)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        return validators.url(url)

    @staticmethod
    def is_valid_brand(brand: str) -> bool:
        return brand.istitle() and brand in "Dalapro Weber Isover Gyproc".split()

    @property
    def columns_and_checkers(self):
        return {
            "Date": self.is_valid_date,
            "Time": self.is_valid_time,
            "PIM_name": self.is_valid_pim_name,
            "Origin": self.is_valid_origin,
            "Competitor": self.is_valid_pim_name,
            "Category": self.is_valid_category,
            "URL": self.is_valid_url,
            "Brand": self.is_valid_brand,
        }

    def check_all(self) -> Iterator[ColumnCheckResult]:
        for column_name, validation_function in self.columns_and_checkers.items():
            is_success = True
            message = "Success"
            for value in self.scraping_urls[column_name].to_list():
                if value != value.strip():
                    is_success = False
                    message = f"Unnecessary white characters preceding or leading in column {column_name}"
                    break
                elif not validation_function(value):
                    is_success = False
                    message = f"Invalid value {value} in column {column_name}"
                    break

            yield ColumnCheckResult(column_name, is_success, message)


proper_filename = "scraping_urls.csv"

st.header(f"Check {proper_filename} before starting scraper.")
file = st.file_uploader(f"Upload {proper_filename}", type=["csv"])

if file:
    if file.name != proper_filename:
        st.write("Invalid filename. QA check is available on the other page.")

    df = common.read_csv(file)

    st.subheader("File Summary")
    st.text(ScrapingUrlsSummary(df).summarize_all())

    st.subheader("File Checks")
    for column_check_result in CheckScrapingUrlsFile(df).check_all():
        message_header = f"{column_check_result.column_name}: {column_check_result.message}"
        if column_check_result.is_success:
            st.success(message_header, icon="✅")
        else:
            st.warning(message_header, icon="⚠️")
