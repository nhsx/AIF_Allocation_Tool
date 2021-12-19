# -------------------------------------------------------------------------
# Copyright (c) 2021 NHS England and NHS Improvement. All rights reserved.
# Licensed under the MIT License and the Open Government License v3. See
# license.txt in the project root for license information.
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
# python
import json
import time
import base64
import utils
import io
import zipfile
import regex as re
from datetime import datetime

# 3rd party:
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import postcodes_io_api

st.set_page_config(
    page_title="ICB Place Based Allocation Tool",
    page_icon="https://www.england.nhs.uk/wp-content/themes/nhsengland/static/img/favicon.ico",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.england.nhs.uk/allocations/",
        "Report a bug": "https://github.com/nhsengland/AIF_Allocation_Tool",
        "About": "This tool is designed to support allocation at places by allowing places to be defined by aggregating GP Practices within an ICB. Please refer to the User Guide for instructions. For more information on the latest allocations, including contact details, please refer to: [https://www.england.nhs.uk/allocations/](https://www.england.nhs.uk/allocations/)",
    },
)
padding = 1
st.markdown(
    f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
    }} </style> """,
    unsafe_allow_html=True,
)

# Set default place in session
# -------------------------------------------------------------------------
if "Default Group" not in st.session_state:
    st.session_state["Default Group"] = {
        "gps": [
            "B85005: Shepley Health Centre",
            "B85022: Honley Surgery",
            "B85061: Skelmanthorpe Family Doctors",
            "B85026: Kirkburton Health Centre",
        ],
        "icb": "NHS West Yorkshire ICB",
    }
if "places" not in st.session_state:
    st.session_state.places = ["Default Group"]

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


def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


# Download functionality
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")


def metric_calcs(group_need_indices, metric_index):
    place_metric = round(group_need_indices[metric_index][0].astype(float), 2)
    ics_metric = round(place_metric - 1, 2)
    return place_metric, ics_metric


aggregations = {
    "GP pop": "sum",
    "Weighted G&A pop": "sum",
    "Weighted Community pop": "sum",
    "Weighted Mental Health pop": "sum",
    "Weighted Maternity pop": "sum",
    "Weighted HCHS pop": "sum",
    "Weighted Prescribing pop": "sum",
    "Weighted Avoidable Mortality pop": "sum",
    "Weighted Health Inequalities pop": "sum",
    "Overall Weighted pop": "sum",
}

index_numerator = [
    "Weighted G&A pop",
    "Weighted Community pop",
    "Weighted Mental Health pop",
    "Weighted Maternity pop",
    "Weighted HCHS pop",
    "Weighted Prescribing pop",
    "Weighted Avoidable Mortality pop",
    "Weighted Health Inequalities pop",
    "Overall Weighted pop",
]

index_names = [
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
    "HCHS Index",
    "Prescribing Index",
    "Avoidable Mortality Index",
    "Health Inequalities Index",
    "Overall Index",
]

# Markdown
# -------------------------------------------------------------------------
# NHS Logo
svg = """
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 16">
            <path d="M0 0h40v16H0z" fill="#005EB8"></path>
            <path d="M3.9 1.5h4.4l2.6 9h.1l1.8-9h3.3l-2.8 13H9l-2.7-9h-.1l-1.8 9H1.1M17.3 1.5h3.6l-1 4.9h4L25 1.5h3.5l-2.7 13h-3.5l1.1-5.6h-4.1l-1.2 5.6h-3.4M37.7 4.4c-.7-.3-1.6-.6-2.9-.6-1.4 0-2.5.2-2.5 1.3 0 1.8 5.1 1.2 5.1 5.1 0 3.6-3.3 4.5-6.4 4.5-1.3 0-2.9-.3-4-.7l.8-2.7c.7.4 2.1.7 3.2.7s2.8-.2 2.8-1.5c0-2.1-5.1-1.3-5.1-5 0-3.4 2.9-4.4 5.8-4.4 1.6 0 3.1.2 4 .6" fill="white"></path>
          </svg>
"""
render_svg(svg)

st.title("ICB Place Based Allocation Tool")
st.markdown("Last Updated 20th December 2021")

# Import Data
# -------------------------------------------------------------------------
data = utils.get_data()
icb = utils.get_sidebar(data)

# SIDEBAR
# -------------------------------------------------------------------------
st.sidebar.subheader("Create New Group")
icb_choice = st.sidebar.selectbox("ICB Filter:", icb, help="Select an ICB")
lad = data["LA District name"].loc[data["ICB name"] == icb_choice].unique().tolist()
lad_choice = st.sidebar.multiselect(
    "Local Authority District Filter:", lad, help="Select a Local Authority District"
)
if lad_choice == []:
    practices = (
        data["practice_display"].loc[data["ICB name"] == icb_choice].unique().tolist()
    )
else:
    practices = (
        data["practice_display"].loc[data["LA District name"].isin(lad_choice)].tolist()
    )

practice_choice = st.sidebar.multiselect(
    "Select GP Practices:",
    practices,
    help="Select GP Practices to aggregate into a single defined 'place'",
)
place_name = st.sidebar.text_input(
    "Name your Group", "Default Group", help="Give your defined place a name to identify it"
)

if st.sidebar.button("Save Group", help="Save group to session state", key="output",):
    if practice_choice == []:
        st.sidebar.error("Please select one or more GP practices")
    else:
        if [place_name] not in st.session_state:
            st.session_state[place_name] = {
                "gps": practice_choice,
                "icb": icb_choice,
            }
        if "places" not in st.session_state:
            st.session_state.places = [place_name]
        if place_name not in st.session_state.places:
            st.session_state.places = st.session_state.places + [place_name]

session_state_dict = dict.fromkeys(st.session_state.places, [])
for key, value in session_state_dict.items():
    session_state_dict[key] = st.session_state[key]
session_state_dict["places"] = st.session_state.places

session_state_dump = json.dumps(session_state_dict, indent=4, sort_keys=False)

st.sidebar.write("-" * 34)  # horizontal separator line.

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
            my_bar = st.sidebar.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1)
            d = json.load(group_file)
            st.session_state.places = d["places"]
            for place in d["places"]:
                st.session_state[place] = d[place]

debug = st.sidebar.checkbox("Show Session State")


# BODY
# -------------------------------------------------------------------------

gp_query = "practice_display == @place_state"
icb_query = "`ICB name` == @icb_state"  # escape column names with backticks https://stackoverflow.com/a/56157729

# dict to store all dfs sorted by ICB
dict_obj = {}
df_list = []
for place in st.session_state.places:
    place_state = st.session_state[place]["gps"]
    icb_state = st.session_state[place]["icb"]
    # get place aggregations
    place_data, place_groupby = aggregate(
        data, gp_query, place, "Place Name", aggregations
    )
    # get ICS aggregations
    icb_data, icb_groupby = aggregate(
        data, icb_query, icb_state, "ICS name", aggregations
    )
    # index calcs
    place_indices, icb_indices = get_index(
        place_groupby, icb_groupby, index_names, index_numerator
    )
    icb_indices.insert(loc=0, column="Group / ICB", value=icb_state)
    place_indices.insert(loc=0, column="Group / ICB", value=place)

    if icb_state not in dict_obj:
        dict_obj[icb_state] = [icb_indices, place_indices]
    else:
        dict_obj[icb_state].append(place_indices)

metric_cols = [
    "Overall Index",
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
]

# add dict values to list
for obj in dict_obj:
    df_list.append(dict_obj[obj])

# flaten list for concatination
flat_list = [item for sublist in df_list for item in sublist]
large_df = pd.concat(flat_list, ignore_index=True)
large_df = large_df.round(decimals = 2)

# All metrics - didn't work well, but might be useful
# for option in dict_obj:
#     st.write("**", option, "**")
#     for count, df in enumerate(dict_obj[option][1:]):  # skip first (ICB) metric
#         # Group GP practice display
#         group_name = dict_obj[option][count + 1]["Group / ICB"].item()
#         group_gps = (
#             "**"
#             + group_name
#             + " : **"
#             + re.sub(
#                 "\w+:",
#                 "",
#                 str(st.session_state[group_name]["gps"])
#                 .replace("'", "")
#                 .replace("[", "")
#                 .replace("]", ""),
#             )
#         )
#         st.info(group_gps)
#         cols = st.columns(len(metric_cols))
#         for metric, name in zip(metric_cols, metric_names):
#             place_metric, ics_metric = metric_calcs(dict_obj[option][count], metric,)
#             cols[metric_cols.index(metric)].metric(
#                 name, place_metric,  # ics_metric, delta_color="inverse"
#             )


# One group at a time
# -------------------------------------------------------------------------
option = st.selectbox("Select Group", (st.session_state.places))

icb_name = st.session_state[option]["icb"]
group_gp_list = st.session_state[option]["gps"]

# MAP
# -------------------------------------------------------------------------

api = postcodes_io_api.Api(debug_http=True)
map = folium.Map(location=[52, 0], zoom_start=10, tiles="openstreetmap")
lat = []
long = []
for gp in group_gp_list:
    post_code = data["GP Practice postcode"].loc[data["practice_display"] == gp].item()
    api_results = api.get_postcode(post_code)
    latitude = api_results["result"]["latitude"]
    longitde = api_results["result"]["longitude"]
    lat.append(latitude)
    long.append(longitde)
    folium.Marker(
        [latitude, longitde],
        popup=str(gp),
        icon=folium.Icon(color="blue", icon="fa-user-md", prefix="fa"),
    ).add_to(map)

# bounds method https://stackoverflow.com/a/58185815
map.fit_bounds([[min(lat), min(long)], [max(lat), max(long)]])
# call to render Folium map in Streamlit
folium_static(map, width=700, height=300)

# Group GP practice display
list_of_gps = re.sub(
    "\w+:", "", str(group_gp_list).replace("'", "").replace("[", "").replace("]", ""),
)
st.info("**Selected GP Practices: **" + list_of_gps)

# Metrics
# -------------------------------------------------------------------------
metric_cols = [
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
    "Prescribing Index",
    "Health Inequalities Index",
    "Overall Index",
]
metric_names = [
    "Gen & Acute",
    "Community*",
    "Mental Health",
    "Maternity",
    "Prescribing",
    "Health Inequal",
    "Overall Index",
]


df = large_df.loc[large_df["Group / ICB"] == option]
df = df.reset_index(drop=True)


st.write("**Relative Need Index**")
cols = st.columns(len(metric_cols))
for metric, name in zip(metric_cols, metric_names):
    place_metric, ics_metric = metric_calcs(df, metric,)
    cols[metric_cols.index(metric)].metric(
        name, place_metric,  # ics_metric, delta_color="inverse"
    )

with st.expander("About the ICB Place Based Allocation Tool"):
    st.markdown(
        "This tool is designed to support allocation at places by allowing places to be defined by aggregating GP Practices within an ICB. Please refer to the User Guide for instructions."
    )
    st.markdown("The tool estimates the relative need for places within the ICB.")
    st.markdown(
        "The Relative Need Index for ICB (i) and Defined Place (p) is given by the formula:"
    )
    st.latex(r""" (WP_p/GP_p)\over (WP_i/GP_i)""")
    st.markdown(
        "This tool is based on estimated need for 2022/23 by utilising weighted populations projected from the October 2021 GP Registered Practice Populations."
    )
    st.markdown(
        "For more information on the latest allocations, including contact details, please refer to: [https://www.england.nhs.uk/allocations/](https://www.england.nhs.uk/allocations/)"
    )
with st.expander("Caveats and Notes"):
    st.markdown(
        "The Community Services index relates to the half of Community Services that are similarly distributed to district nursing. The published Community Services target allocation is calculated using the Community Services model. This covers 50% of Community Services. The other 50% is distributed through the General & Acute model."
    )

if st.button("Delete", help="Delete this group", key="output",):
    if len(st.session_state.places) <= 1:
        st.warning("No groups left in memory, 'Default Group' reset to default")
        if "Default Group" not in st.session_state:
            st.session_state["Default Group"] = {
                "gps": [
                    "B85005: Shepley Health Centre",
                    "B85022: Honley Surgery",
                    "B85061: Skelmanthorpe Family Doctors",
                    "B85026: Kirkburton Health Centre",
                ],
                "icb": "NHS West Yorkshire ICB",
            }
    else:
        del st.session_state[option]
        del st.session_state.places[option]

# Downloads
# -------------------------------------------------------------------------
current_date = datetime.now().strftime("%Y-%m-%d")

st.subheader("Download all Group Data")

print_table = st.checkbox("Preview data download")
if print_table:
    with st.container():
        utils.write_table(large_df)

csv = convert_df(large_df)

# https://stackoverflow.com/a/44946732
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
    for file_name, data in [
        ("ICB allocation calculations.csv", io.BytesIO(csv)),
        ("ICB allocation tool documentation.txt", io.BytesIO(b"222")),
        (
            "ICB allocation tool configuration file.json",
            io.StringIO(session_state_dump),
        ),
    ]:
        zip_file.writestr(file_name, data.getvalue())

btn = st.download_button(
    label="Download ZIP",
    data=zip_buffer.getvalue(),
    file_name="ICB allocation tool %s.zip" % current_date,
    mime="application/zip",
)

# Debugging
# -------------------------------------------------------------------------
if debug:
    st.markdown("DEBUGGING")
    st.session_state
