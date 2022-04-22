import streamlit as st
from st_aggrid import AgGrid

import pandas as pd

# Load data and cache
@st.cache  # use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "data/wp_data_2022LAD.csv"  # file containing the gp practice weighted populations
    df = pd.read_csv(path)
    df = df.rename(
        columns={
            "Practice_Code": "GP Practice code",
            "GP_Practice_Name": "GP Practice name",
            "Practice_Postcode": "GP Practice postcode",
            "CCG21": "CCG code",
            "Former CCG": "CCG name",
            "PCN_Code": "PCN code",
            "PCN_Name": "PCN name",
            "LOC22": "Location code",
            "LOC22name": "Location name",
            "ICS22": "ICB code",
            "ICS22name": "ICB name",
            "R22": "Region code",
            "Region22": "Region name",
            "LAD21": "LA District code",
            "LTLA21": "LA District name",
            "LA21": "LA code",
            "UTLA21": "LA name",
            "Patients": "Registered Patients",
            "pop 2022/23": "GP pop",
            "G&A WP": "Weighted G&A pop",
            "CS WP": "Weighted Community pop",
            "MH WP": "Weighted Mental Health pop",
            "Mat WP": "Weighted Maternity pop",
            "Health Ineq WP": "Weighted Health Inequalities pop",
            "Prescr WP": "Weighted Prescribing pop",
            "Final WP": "Overall Weighted pop",
            "Final PMC WP": "Weighted Primary Care",
            

        }
    )
    df = df.fillna(1).replace(0, 1)
    df["practice_display"] = df["GP Practice code"] + ": " + df["GP Practice name"]
    return df


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Sidebar dropdown list
@st.cache
def get_sidebar(data):
    icb = data["ICB name"].unique().tolist()
    icb.sort()
    return icb


def write_table(data):
    return AgGrid(data)
