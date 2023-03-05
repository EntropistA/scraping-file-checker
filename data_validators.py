import string
from abc import abstractmethod
from collections import Counter, namedtuple
from datetime import datetime
from typing import Iterator
from urllib.parse import urlparse

import pandas as pd
import validators

ALLOWED_PRICE_UNITS = {'L', 'M2', 'Skiva', 'Styck', 'Pallet', 'Paket', 'Säck', 'Storsäck', 'KG'}


def is_valid_price_unit(unit):
    return unit in ALLOWED_PRICE_UNITS


def get_domain(url: str) -> str:
    return urlparse(url).netloc


class ScrapingDataFrame:
    def __init__(self, scraping_df: pd.DataFrame):
        self.scraping_df = scraping_df


class ScrapingUrlsSummary(ScrapingDataFrame):
    def _get_domain_counter(self):
        domain_list = self.scraping_df["URL"].apply(get_domain).to_list()
        counter = Counter(domain_list)
        sorted_counter = dict(counter.most_common(len(counter)))
        return sorted_counter

    def _summarize_domain(self):
        summary = ""
        for domain, count in self._get_domain_counter().items():
            summary += f"{domain}: {count}\n"
        return summary

    def _get_category_unique_value_list(self) -> {str: list}:
        category_column_list = "Brand Category Origin Currency Price_unit Competitor Customer_name".split()
        return {category: sorted(self.scraping_df[category].unique()) for category in category_column_list}

    def _summarize_descriptive_columns(self) -> str:
        summary = ""
        for category, value_list in self._get_category_unique_value_list().items():
            summary += f"{category}: {', '.join(value_list)}\n"
        return summary

    def summarize_all(self):
        summary_section_mapping = {
            "Domain Count": self._summarize_domain,
            "Category Columns": self._summarize_descriptive_columns
        }
        summarization = ""
        for summary_name, summary in summary_section_mapping.items():
            summarization += summary_name + "\n" + summary() + "\n"
        return summarization


ColumnCheckResult = namedtuple("ColumnCheckResult", "column_name is_success message")


class Checker(ScrapingDataFrame):
    @staticmethod
    def _is_valid_text(text: str):
        space = " "
        nbsp = " "
        special_characters = space + nbsp + string.punctuation + "®"
        return all(c.isalnum() or c in special_characters for c in text)

    @property
    @abstractmethod
    def columns_and_checkers(self) -> dict:
        pass

    def get_column_check_result(self, column_name, validation_function) -> ColumnCheckResult:
        for row_index, value in enumerate(self.scraping_df[column_name].to_list()):
            location_identifier = f" at index ({row_index}, {column_name})"
            if value != value.strip():
                is_success = False
                message = "Unnecessary white characters preceding or leading"
            elif not validation_function(value):
                # print("debug", value, len(value), bool(validation_function(value)), validation_function)
                is_success = False
                message = f"Invalid value: {value}" if value else f"blank field"
            else:
                is_success = True
                message = "Success"
            message += location_identifier if not is_success else ""
            return ColumnCheckResult(column_name, is_success, message)

    def check_all(self) -> Iterator[ColumnCheckResult]:
        for column_name, validation_function in self.columns_and_checkers.items():
            yield self.get_column_check_result(column_name, validation_function)


class FromFileColumnsChecker(Checker):
    @staticmethod
    def is_valid_brand(brand: str) -> bool:
        return brand.istitle() and brand in "Dalapro Weber Isover Gyproc".split()

    @staticmethod
    def is_valid_category(category: str) -> bool:
        return category and all(c.isalpha() or c in "/ -" for c in category)

    @staticmethod
    def is_valid_origin(origin: str) -> bool:
        return origin in ["Saint-Gobain", "Competition"]

    @staticmethod
    def is_valid_currency(currency):
        return currency == "SEK"

    def is_valid_competitor(self, competitor: str) -> bool:
        return self._is_valid_text(competitor)

    def is_valid_url(self, url: str) -> bool:
        row_with_url = self.scraping_df[self.scraping_df["URL"] == url]
        if row_with_url.shape[0] == 2:
            column_must_match = self.columns_and_checkers.keys()
            row_with_url = row_with_url[column_must_match]
            if row_with_url[0].to_list() != row_with_url[1].to_list():
                return False
        return validators.url(url)

    def is_valid_pim_name(self, pim_name: str) -> bool:
        return pim_name and self._is_valid_text(pim_name)

    @property
    def columns_and_checkers(self) -> dict:
        return {
            "PIM_name": self.is_valid_pim_name,
            "Origin": self.is_valid_origin,
            "Competitor": self.is_valid_competitor,
            "Category": self.is_valid_category,
            "Price_unit": is_valid_price_unit,
            "Currency": self.is_valid_currency,
            "URL": self.is_valid_url,
            "Brand": self.is_valid_brand,
        }


class ScrapedColumnChecker(Checker):

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

    def is_valid_name(self, name: str) -> bool:
        return name and self._is_valid_text(name)

    @staticmethod
    def is_valid_price(price):
        try:
            float(price)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_valid_article_number(article_number: str):
        return all(c.isdigit() for c in article_number)

    @property
    def columns_and_checkers(self):
        return {
            "Date": self.is_valid_date,
            "Time": self.is_valid_time,
            "Name": self.is_valid_name,
            "Price": self.is_valid_price,
            "Article_number": self.is_valid_article_number,
        }
