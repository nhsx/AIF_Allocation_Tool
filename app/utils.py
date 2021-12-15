import streamlit as st
from st_aggrid import AgGrid

import pandas as pd

# Load data and cache
@st.cache  # use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "../data/wp_data_2022LAD.csv"  # file containing the gp practice weighted populations
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "GP_pop": "GP pop",
            "WP_G&A": "Weighted G&A pop",
            "WP_CS": "Weighted Community pop",
            "WP_MH": "Weighted Mental Health pop",
            "WP_Mat": "Weighted Maternity pop",
            "WP_HCHS": "Weighted HCHS pop",
            "WP_Presc": "Weighted Prescribing pop",
            "WP_HI": "Weighted Health Inequalities pop",
            "WP_AM": "Weighted Avoidable Mortality pop",
            "WP_Overall": "Overall Weighted pop",
        }
    )
    df["practice_display"] = df["GP Practice code"] + ": " + df["GP Practice name"]
    return df


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Sidebar dropdown list
@st.cache
def get_sidebar(data):
    ics = data["ICS name"].unique().tolist()
    ics.sort()
    return ics


def write_table(data):
    return AgGrid(data)

