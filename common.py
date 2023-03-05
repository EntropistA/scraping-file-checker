import pandas as pd
import streamlit as st


def read_csv(file_location) -> pd.DataFrame:
    return pd.read_csv(file_location, header=0, dtype=str).fillna("")


def check_proper_name_file_input(proper_filename: str, proper_file_suffix: str):
    file = st.file_uploader(f"Upload {proper_filename}", type=[proper_file_suffix])
    if file and file.name != f"{proper_filename}.{proper_file_suffix}":
        st.write(f"Invalid filename (Expected {proper_filename}.{proper_file_suffix}). Check other pages.")
    return file
