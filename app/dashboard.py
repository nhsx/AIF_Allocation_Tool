# -------------------------------------------------------------------------
# Copyright (c) 2021 NHS England and NHS Improvement. All rights reserved.
# Licensed under the MIT License. See license.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
FILE:           dashboard.py
DESCRIPTION:    streamlit weighted capitation tool
USAGE:
CONTRIBUTORS:   
CONTACT:        
CREATED:        2021
VERSION:        0.0.2
"""

# Libraries
# -------------------------------------------------------------------------

import json
import time

# 3rd party:
import streamlit as st
import pandas as pd
import utils

# Set default place in session
# -----------------------------------------------------
if "Group 1" not in st.session_state:
    st.session_state["Group 1"] = [
        "A83005: Whinfield Medical Practice",
        "A83013: Neasham Road Surgery",
        "A83034: Blacketts Medical Practice",
    ]
if "places" not in st.session_state:
    st.session_state.places = ["Group 1"]

# Functions & Calls
# -------------------------------------------------------------------------
# aggregate on a query and set of aggregations
def aggregate(data, query, name, on, aggregations):
    df = data.query(query)
    if on not in df.columns:
        df.insert(loc=0, column=on, value=name)
    df_group = df.groupby(on).agg(aggregations)
    df_group = df_group.astype(int)
    return df, df_group


# calculate index of weighted populations
def get_index(place_indices, ics_indices, index_names, index_numerator):
    ics_indices[index_names] = ics_indices[index_numerator].div(
        ics_indices["GP pop"].values, axis=0
    )
    place_indices[index_names] = (
        place_indices[index_numerator]
        .div(place_indices["GP pop"].values, axis=0)
        .div(ics_indices[index_names].values, axis=0)
    )
    return place_indices, ics_indices


aggregations = {
    "GP pop": "sum",
    "Weighted G&A pop": "sum",
    "Weighted Community pop": "sum",
    "Weighted Mental Health pop": "sum",
    "Weighted Maternity pop": "sum",
    "Weighted HCHS pop": "sum",
    "Weighted Market Forces Factor pop": "sum",
    "Weighted EACA pop": "sum",
    "Weighted Prescribing pop": "sum",
    "Weighted AM pop": "sum",
    "Target exc remote (£k)": "sum",
    "Target inc remote (£k)": "sum",
    "Overall Weighted pop": "sum",
}

index_numerator = [
    "Weighted G&A pop",
    "Weighted Community pop",
    "Weighted Mental Health pop",
    "Weighted Maternity pop",
    "Weighted HCHS pop",
    "Weighted Market Forces Factor pop",
    "Weighted EACA pop",
    "Weighted Prescribing pop",
    "Weighted AM pop",
    "Overall Weighted pop",
]

index_names = [
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
    "HCHS Index",
    "Market Forces Factor Index",
    "EACA Index",
    "Prescribing Index",
    "AM Index",
    "Overall Index",
]

gp_query = "practice_display == @place_practices"
ics_query = "`ICS name` == @ics_choice"  # escape column names with backticks https://stackoverflow.com/a/56157729

# Markdown
# -----------------------------------------------------
st.markdown("PROTOTYPE UNDER DEVELOPMENT - Last Updated 9th December 2021")
# st.image("../images/nhs_logo.png", caption=None, width=100)
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
# -----------------------------------------------------
data = utils.get_data()
ics = utils.get_sidebar(data)

# SIDEBAR
# -----------------------------------------------------
ics_choice = st.sidebar.selectbox("Select your ICS:", ics, help="Select an ICS")
ccg_filter = st.sidebar.checkbox("Filter by CCG")
if ccg_filter:
    ccg = data["CCG name"].loc[data["ICS name"] == ics_choice].unique().tolist()
    ccg_choice = st.sidebar.selectbox("Select your CCG:", ccg, help="Select a CCG")
    practices = list(data["practice_display"].loc[data["CCG name"] == ccg_choice])
else:
    practices = list(data["practice_display"].loc[data["ICS name"] == ics_choice])

practice_choice = st.sidebar.multiselect(
    "Select practices",
    practices,
    help="Select GP Practices to aggregate into a single defined 'place'",
)
place_name = st.sidebar.text_input(
    "Name your Group", "Group 1", help="Give your defined place a name to identify it"
)
if st.sidebar.button("Save Group", help="s", key="output",):
    if [place_name] not in st.session_state:
        st.session_state[place_name] = practice_choice
    if "places" not in st.session_state:
        st.session_state.places = {place_name: ics_choice}
    if place_name not in st.session_state.places:
        st.session_state.places = st.session_state.places + [place_name]

if st.sidebar.button("Reset Group", key="output"):
    del st.session_state[place_name]
    st.session_state.places = st.session_state.places

# BODY
# -----------------------------------------------------
option = st.selectbox("Selected Place", (st.session_state.places))

st.info("**Selected GP Practices: **" + str(st.session_state[option]))

st.write(
    "KPIs shows the Need Indices of **",
    option,
    "** compared to the **",
    ics_choice,
    " ICS** average",
)

place_practices = st.session_state[option]
# get place aggregations
place_query, place_indices = aggregate(
    data, gp_query, option, "Place Name", aggregations
)

# get ICS aggregations
ics_query, ics_indices = aggregate(
    data, ics_query, ics_choice, "ICS name", aggregations
)
# index calcs
place_indices1, ics_indices1 = get_index(
    place_indices, ics_indices, index_names, index_numerator
)

# print all data
ics_indices1.insert(loc=0, column="Group / ICS", value=ics_choice)
place_indices1.insert(loc=0, column="Group / ICS", value=option)
df_print = pd.concat(
    [ics_indices1, place_indices1], axis=0, join="inner", ignore_index=True
)

# tbd: Loop this
(Overall, GA, Community, MentalHealth, Maternity) = st.columns(5)
with Overall:
    place_metric = round(place_indices1["Overall Index"][0].astype(float), 3)
    ics_metric = round(ics_indices1["Overall Index"][0].astype(float) - place_metric, 3)
    st.metric(
        "Overall Index", place_metric, ics_metric, delta_color="normal",
    )
with GA:
    place_metric = round(place_indices1["G&A Index"][0].astype(float), 3)
    ics_metric = round(ics_indices1["G&A Index"][0].astype(float) - place_metric, 3)
    st.metric(
        "G&A Index", place_metric, ics_metric, delta_color="normal",
    )
with Community:
    place_metric = round(place_indices1["Community Index"][0].astype(float), 3)
    ics_metric = round(
        ics_indices1["Community Index"][0].astype(float) - place_metric, 3
    )
    st.metric(
        "Community Index", place_metric, ics_metric, delta_color="normal",
    )
with MentalHealth:
    place_metric = round(place_indices1["Mental Health Index"][0].astype(float), 3)
    ics_metric = round(
        ics_indices1["Mental Health Index"][0].astype(float) - place_metric, 3
    )
    st.metric(
        "Mental Health Index", place_metric, ics_metric, delta_color="normal",
    )
with Maternity:
    place_metric = round(place_indices1["Maternity Index"][0].astype(float), 3)
    ics_metric = round(
        ics_indices1["Maternity Index"][0].astype(float) - place_metric, 3
    )
    st.metric(
        "Maternity Index", place_metric, ics_metric, delta_color="normal",
    )
# add these
(HCHS, MarketForcesFactor, EACA, Prescribing, AM) = st.columns(5)
with HCHS:
    place_metric = round(place_indices1["HCHS Index"][0].astype(float), 3)
    ics_metric = round(ics_indices1["HCHS Index"][0].astype(float) - place_metric, 3)
    st.metric(
        "HCHS Index", place_metric, ics_metric, delta_color="normal",
    )
with MarketForcesFactor:
    place_metric = round(
        place_indices1["Market Forces Factor Index"][0].astype(float), 3
    )
    ics_metric = round(
        ics_indices1["Market Forces Factor Index"][0].astype(float) - place_metric, 3
    )
    st.metric(
        "MFF Index", place_metric, ics_metric, delta_color="normal",
    )
with EACA:
    place_metric = round(place_indices1["EACA Index"][0].astype(float), 3)
    ics_metric = round(ics_indices1["EACA Index"][0].astype(float) - place_metric, 3)
    st.metric(
        "EACA Index", place_metric, ics_metric, delta_color="normal",
    )
with Prescribing:
    place_metric = round(place_indices1["Prescribing Index"][0].astype(float), 3)
    ics_metric = round(
        ics_indices1["Prescribing Index"][0].astype(float) - place_metric, 3
    )
    st.metric(
        "Prescribing Index", place_metric, ics_metric, delta_color="normal",
    )
with AM:
    place_metric = round(place_indices1["AM Index"][0].astype(float), 3)
    ics_metric = round(ics_indices1["AM Index"][0].astype(float) - place_metric, 3)
    st.metric(
        "AM Index", place_metric, ics_metric, delta_color="normal",
    )

session_state_dict = dict.fromkeys(st.session_state.places, [])
for key, value in session_state_dict.items():
    session_state_dict[key] = st.session_state[key]
session_state_dict["places"] = st.session_state.places
# st.write(session_state_dict)

session_state_dump = json.dumps(session_state_dict, indent=4, sort_keys=True)

# st.subheader("Group Metrics", anchor=None)
st.sidebar.markdown(
    """<hr style="height:1px;border:none;color:#333;background-color:#333;" /> """,
    unsafe_allow_html=True,
)
# Use file uploaded to read in groups of practices
advanced_options = st.sidebar.checkbox("Advanced Options")
if advanced_options:
    # downloads
    st.sidebar.download_button(
        label="Download session data as JSON",
        data=session_state_dump,
        file_name="session.json",
        mime="text/json",
    )
    # uploads
    form = st.sidebar.form(key="my-form")
    group_file = form.file_uploader(
        "Upload previous session data as JSON", type=["json"]
    )
    submit = form.form_submit_button("Submit")
    if submit:
        if group_file is not None:
            my_bar = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1)
            d = json.load(group_file)
            st.session_state.places = d["places"]
            for place in d["places"]:
                st.session_state[place] = d[place]

print_table = st.checkbox("Show Dataframe")
if print_table:
    with st.container():
        utils.write_table(df_print)

# Debugging
debug = st.checkbox("Show Session State")
if debug:
    st.markdown("DEBUGGING")
    st.session_state
