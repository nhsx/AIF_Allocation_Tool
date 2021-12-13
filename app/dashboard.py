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

# Libs
# -------------------------------------------------------------------------
# 3rd party:
import streamlit as st
import pandas as pd
import utils

# Markdown
# -----------------------------------------------------
st.markdown("PROTOTYPE UNDER DEVELOPMENT - Last Updated 9th December 2021")

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

if st.sidebar.button("Reset Group", key="output",):
    del st.session_state[place_name]

# BODY
# -----------------------------------------------------
option = st.selectbox("Selected Place", ("test", "test"))

st.write("You selected:", option)

st.session_state

cols = [
    "Place Name",
    "GP practice code",
    "GP practice name",
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
    "GP pop",
    "Weighted G&A pop",
    "Weighted Community pop",
    "Weighted Mental Health pop",
    "Weighted Maternity pop",
    "Weighted HCHS pop",
    "Weighted Market Forces Factor pop",
    "Weighted EACA pop",
    "Weighted Prescribing pop",
    "Weighted AM pop",
    "Target exc remote (£k)",
    "Target inc remote (£k)",
    "Overall Weighted pop",
    "Region ODS code",
    "Region name",
    "ICS ODS code",
    "ICS ONS code",
    "ICS name",
    "CCG ODS code",
    "CCG name",
    "PCN ODS code",
    "PCN code",
]

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


if st.button("Calculate", help="s", key="output",):
    place_practices = st.session_state[place_name]
    # get place aggregations
    place_query, place_indices = aggregate(
        data, gp_query, place_name, "Place Name", aggregations
    )
    st.write(ics_choice)
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
    place_indices1.insert(loc=0, column="Group / ICS", value=place_name)
    df_print = pd.concat(
        [ics_indices1, place_indices1], axis=0, join="inner", ignore_index=True
    )
    with st.container():
        utils.write_table(df_print)

    for metric in index_names:
        place_metric = round(place_indices1[metric][0].astype(float), 3)
        ics_metric = round(ics_indices1[metric][0].astype(float), 3)
        st.metric(
            metric, place_metric, ics_metric, delta_color="normal",
        )

