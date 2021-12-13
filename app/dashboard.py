import streamlit as st
from streamlit.elements.legacy_data_frame import LegacyDataFrameMixin

import pandas as pd
import utils

# Temporary prototype notice
st.markdown("PROTOTYPE UNDER DEVELOPMENT - Last Updated 9th December 2021")

# App appearance
st.image(
    "../images/nhs_logo.png", caption=None,
)
st.title("ICS Place Based Allocation Tool")
st.markdown(
    "This tool is designed to allow place, for allocation purposes, to be defined by aggregating GP Practices within an ICS. Please refer to the User Guide for instructions."
)
st.markdown(
    "The Relative Need Index for ICS (i) and Defined Place (p) is given by the formula:"
)
st.latex(r""" (WP_p/GP_p)\over (WP_i/GP_i)""")
st.markdown(
    "This tool utilises weighted populations calculated from the 2018/19 GP Registered Practice Populations"
)

# Import Data
data = utils.get_data()
ics = utils.get_sidebar(data)

# SIDEBAR
ics_choice = st.sidebar.selectbox("Select your ICS:", ics, help="Select an ICS")
ccg_filter = st.sidebar.checkbox("Filter by CCG")
if ccg_filter:
    ccg = data["CCG19"].loc[data["ICS"] == ics_choice].unique().tolist()
    ccg_choice = st.sidebar.selectbox("Select your CCG:", ccg, help="Select a CCG")
    practices = list(data["Practice"].loc[data["CCG19"] == ccg_choice])
else:
    practices = list(data["Practice"].loc[data["ICS"] == ics_choice])

practice_choice = st.sidebar.multiselect(
    "Select practices",
    practices,
    help="Select GP Practices to aggregate into a single defined 'place'",
)
# BODY
place_name = st.text_input(
    "Place Name", "Group 1", help="Give your defined place a name to identify it"
)

# BUTTONS

if st.button("Add Selection to Group", help="s", key="output",):
    if [place_name] not in st.session_state:
        st.session_state[place_name] = practice_choice

if st.button("Reset Group", key="output",):
    del st.session_state[place_name]

st.session_state

aggregations = {
    "GP_pop": "sum",
    "WP_G&A": "sum",
    "WP_CS": "sum",
    "WP_MH": "sum",
    "WP_Mat": "sum",
    "WP_HCHS": "sum",
    "EACA_index": "mean",
    "WP_Presc": "sum",
    "WP_AM": "sum",
    "WP_Overall": "sum",
}

query = "Practice == @place_practices"


def aggregate(data, query, place_name, aggregations):
    df = data.query(query)
    df.insert(loc=0, column="Place Name", value=place_name)
    df_group = df.groupby("Place Name").agg(aggregations)
    return df, df_group


if st.button("Calculate", help="s", key="output",):
    place_practices = st.session_state[place_name]
    df_query, df_indices = aggregate(data, query, place_name, aggregations)

    df_indices.insert(loc=0, column="Place Name", value=place_name)
    df_indices.insert(loc=0, column="Practice", value=place_name + " Totals")
    df_indices = pd.concat([df_indices, df_query], axis=0, join="outer")
    df_indices = df_indices[data.columns.tolist()]
    df_indices.insert(loc=0, column="Place Name", value=place_name)
    with st.container():
        utils.write_table(df_indices)

st.metric("Temperature", "70 °F", "1.2 °F")
