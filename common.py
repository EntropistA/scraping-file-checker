from urllib.parse import urlparse

import pandas as pd


def get_domain(url: str) -> str:
    return urlparse(url).netloc


def read_csv(file_location) -> pd.DataFrame:
    return pd.read_csv(file_location, header=0, dtype=str).fillna("")
