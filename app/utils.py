import streamlit as st
from st_aggrid import AgGrid

import pandas as pd
import numpy as np

# Load data and cache
@st.cache  # use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "../data/wp_data.csv"  # file containing the gp practice weighted populations
    df = pd.read_csv(path)
    df = df.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})
    df["Practice"] = df["Practice"] + " " + ":" + " " + df["practice_name"]
    return df


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Sidebar dropdown list
@st.cache
def get_sidebar(data):
    ics = data["ICS"].unique().tolist()
    return ics


def write_table(data):
    return AgGrid(data)
