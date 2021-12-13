import streamlit as st
from st_aggrid import AgGrid

import pandas as pd
import numpy as np

# Load data and cache
@st.cache  # use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "../data/wp_data.csv"  # file containing the gp practice weighted populations
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "R21": "Region ODS code",
            "Region21_7": "Region name",
            "STP21": "ICS ODS code",
            "STP21ons": "ICS ONS code",
            "STP21_42": "ICS name",
            "CCG": "CCG ODS code",
            "CCG19": "CCG name",
            "PCN": "PCN ODS code",
            "PCN_name": "PCN code",
            "Practice": "GP practice code",
            "GP practice name": "GP practice name",
            "GP_pop": "GP pop",
            "WP_G&A": "Weighted G&A pop",
            "WP_CS": "Weighted Community pop",
            "WP_MH": "Weighted Mental Health pop",
            "WP_Mat": "Weighted Maternity pop",
            "WP_HCHS": "Weighted HCHS pop",
            "WP_MFF": "Weighted Market Forces Factor pop",
            "WP_EACA": "Weighted EACA pop",
            "WP_Presc": "Weighted Prescribing pop",
            "WP_AM": "Weighted AM pop",
            "Target_exc_remote_£k": "Target exc remote (£k)",
            "Target_inc_remote_£k": "Target inc remote (£k)",
            "WP_Overall": "Overall Weighted pop",
        }
    )
    df["practice_display"] = df["GP practice code"] + ": " + df["GP practice name"]
    return df


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Sidebar dropdown list
@st.cache
def get_sidebar(data):
    ics = data["ICS name"].unique().tolist()
    return ics


def write_table(data):
    return AgGrid(data)

