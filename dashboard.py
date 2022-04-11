# -------------------------------------------------------------------------
# Copyright (c) 2021 NHS England and NHS Improvement. All rights reserved.
# Licensed under the MIT License and the Open Government License v3. See
# license.txt in the project root for license information.
# -------------------------------------------------------------------------

"""
FILE:           dashboard.py
DESCRIPTION:    Streamlit weighted capitation tool
CONTRIBUTORS:   Craig Shenton, Jonathan Pearson, Mattia Ficarelli   
CONTACT:        england.revenue-allocations@nhs.net
CREATED:        2021-12-14
VERSION:        0.0.1
"""

# Libraries
# -------------------------------------------------------------------------
# python
import json
import time
import base64
import io
import zipfile
import regex as re
from datetime import datetime

# local
import utils

# 3rd party:
import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium

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
if len(st.session_state) < 1:
    st.session_state["Default Place"] = {
        "gps": [
            "B85005: Shepley Health Centre",
            "B85022: Honley Surgery",
            "B85061: Skelmanthorpe Family Doctors",
            "B85026: Kirkburton Health Centre",
        ],
        "icb": "NHS West Yorkshire ICB",
    }
if "places" not in st.session_state:
    st.session_state.places = ["Default Place"]

# Functions & Calls
# -------------------------------------------------------------------------
# aggregate on a query and set of aggregations
#Name is the name of the place in the session state, 'aggregations' tells it how to sum each column, 'on' is what to group it by. Not sure what the not in bit is doing. 
#Query filters to make sure that GP Display (which is the gp name and code joined together by utils) is in the session state place list
# Function outputs filtered data and grouped, filtered data separately
def aggregate(data, query, name, on, aggregations):
    df = data.query(query)
    if on not in df.columns:
        df.insert(loc=0, column=on, value=name)
    df_group = df.groupby(on).agg(aggregations)
    df_group = df_group.astype(int)
    return df, df_group


#Calculate index of weighted populations. Take the groupby output fromn the aggregator and divides it by the population number. Do it by icb and place. 
#get_index(place_groupby, icb_groupby, index_names, index_numerator)
#place index is divided by icb index to get a relative number
#overall index is final_wp / gp pop
def get_index(place_indices, icb_indices, index_names, index_numerator):
    icb_indices[index_names] = icb_indices[index_numerator].div(
        icb_indices["GP pop"].values, axis=0
    )
    place_indices[index_names] = (
        place_indices[index_numerator]
        .div(place_indices["GP pop"].values, axis=0)
        .div(icb_indices[index_names].values, axis=0)
    )
    return place_indices, icb_indices


# render svg image
def render_svg(svg):
    """Renders the given svg string."""
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


# Download functionality
@st.cache
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

#Metric calcs. 
def metric_calcs(group_need_indices, metric_index):
    place_metric = round(group_need_indices[metric_index][0].astype(float), 2)
    icb_metric = round(place_metric - 1, 2)
    return place_metric, icb_metric


aggregations = {
    "GP pop": "sum",
    "Weighted G&A pop": "sum",
    "Weighted Community pop": "sum",
    "Weighted Mental Health pop": "sum",
    "Weighted Maternity pop": "sum",
    "Weighted Prescribing pop": "sum",
    "Overall Weighted pop": "sum",
    "Weighted Primary Care": "sum",
    "Weighted Health Inequalities pop": "sum",
}

index_numerator = [
    "Weighted G&A pop",
    "Weighted Community pop",
    "Weighted Mental Health pop",
    "Weighted Maternity pop",
    "Weighted Prescribing pop",
    "Overall Weighted pop",
    "Weighted Primary Care",
    "Weighted Health Inequalities pop",
]

index_names = [
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
    "Prescribing Index",
    "Overall Core Index",
    "Primary Care Index",
    "Health Inequalities Index",
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
st.markdown("Last Updated 6th January 2022")

# Import Data
# -------------------------------------------------------------------------
data = utils.get_data()
icb = utils.get_sidebar(data)

# SIDEBAR
# -------------------------------------------------------------------------
st.sidebar.subheader("Create New Place")

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
        data["practice_display"].loc[(data["LA District name"].isin(lad_choice)) & (data["ICB name"] == icb_choice)].tolist()
    )

select_all_LAD = st.sidebar.checkbox("Select all GP Practices")
if select_all_LAD:
    practice_choice = practices
else:
    practice_choice = st.sidebar.multiselect(
        "Select GP Practices:",
        practices,
        help="Select GP Practices to aggregate into a single defined 'place'",
    )

place_name = st.sidebar.text_input(
    "Name your Place",
    "",
    help="Give your defined place a name to identify it",
)

if st.sidebar.button("Save Place", help="Save place to session data"):
    if practice_choice == [] or place_name == "Default Place":
        if practice_choice == []:
            st.sidebar.error("Please select one or more GP practices")
        if place_name == "Default Place":
            st.sidebar.error(
                "Please rename your place to something other than 'Default Place'"
            )
    if place_name == "":
        st.sidebar.error("Please give your place a name")
    else:
        if practice_choice == [] or place_name == "Default Place":
            print("")
        else:
            if (
                len(st.session_state.places) <= 1
                and st.session_state.places[0] == "Default Place"
            ):
                del [st.session_state["Default Place"]]
                del [st.session_state.places[0]]
                if [place_name] not in st.session_state:
                    st.session_state[place_name] = {
                        "gps": practice_choice,
                        "icb": icb_choice,
                    }
                if "places" not in st.session_state:
                    st.session_state.places = [place_name]
                if place_name not in st.session_state.places:
                    st.session_state.places = st.session_state.places + [place_name]
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

st.sidebar.write("-" * 34)  # horizontal separator line.

session_state_dict = dict.fromkeys(st.session_state.places, [])
for key, value in session_state_dict.items():
    session_state_dict[key] = st.session_state[key]
session_state_dict["places"] = st.session_state.places

session_state_dump = json.dumps(session_state_dict, indent=4, sort_keys=False)

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
            d = json.load(group_file)
            st.session_state.places = d["places"]
            for place in d["places"]:
                st.session_state[place] = d[place]
            my_bar = st.sidebar.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                my_bar.progress(percent_complete + 1)
            my_bar.empty()

see_session_data = st.sidebar.checkbox("Show Session Data")

# BODY
# -------------------------------------------------------------------------

select_index = len(st.session_state.places) - 1  # find n-1 index
placeholder = st.empty()
option = placeholder.selectbox(
    "Select Place", (st.session_state.places), index=select_index, key="before"
)

# DELETE PLACE
# -------------------------------------------------------------------------
if "after" not in st.session_state:
    st.session_state.after = st.session_state.before

label = "Delete Current Selection"
delete_place = st.button(label, help=label)
my_bar_delete = st.empty()
if delete_place:
    if len(st.session_state.places) <= 1:
        del [st.session_state[st.session_state.after]]
        if "Default Group" not in st.session_state:
            st.session_state["Default Place"] = {
                "gps": [
                    "B85005: Shepley Health Centre",
                    "B85022: Honley Surgery",
                    "B85061: Skelmanthorpe Family Doctors",
                    "B85026: Kirkburton Health Centre",
                ],
                "icb": "NHS West Yorkshire ICB",
            }
        if "places" not in st.session_state:
            st.session_state.places = ["Default Place"]
        else:
            st.session_state["Default Place"] = {
                "gps": [
                    "B85005: Shepley Health Centre",
                    "B85022: Honley Surgery",
                    "B85061: Skelmanthorpe Family Doctors",
                    "B85026: Kirkburton Health Centre",
                ],
                "icb": "NHS West Yorkshire ICB",
            }
        st.session_state.places = ["Default Place"]
        st.session_state.after = "Default Place"
        st.warning(
            "All places deleted. 'Default Place' reset to default. Please create a new place."
        )
        my_bar_delete.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar_delete.progress(percent_complete + 1)
        my_bar_delete.empty()
    else:
        del [st.session_state[st.session_state.after]]
        del [
            st.session_state.places[
                st.session_state.places.index(st.session_state.after)
            ]
        ]
        my_bar_delete.progress(0)
        for percent_complete in range(100):
            time.sleep(0.01)
            my_bar_delete.progress(percent_complete + 1)
        my_bar_delete.empty()

select_index = len(st.session_state.places) - 1  # find n-1 index
option = placeholder.selectbox(
    "Select Place", (st.session_state.places), index=select_index, key="after"
)
icb_name = st.session_state[st.session_state.after]["icb"]
group_gp_list = st.session_state[st.session_state.after]["gps"]

# MAP
# -------------------------------------------------------------------------

map = folium.Map(location=[52, 0], zoom_start=10, tiles="openstreetmap")
lat = []
long = []
for gp in group_gp_list:
    latitude = data["Latitude"].loc[data["practice_display"] == gp].item()
    longitude = data["Longitude"].loc[data["practice_display"] == gp].item()
    lat.append(latitude)
    long.append(longitude)
    folium.Marker(
        [latitude, longitude],
        popup=str(gp),
        icon=folium.Icon(color="darkblue", icon="fa-user-md", prefix="fa"),
    ).add_to(map)

# bounds method https://stackoverflow.com/a/58185815
map.fit_bounds(
    [[min(lat) - 0.02, min(long)], [max(lat) + 0.02, max(long)]]
)  # add buffer to north
# call to render Folium map in Streamlit
folium_static(map, width=700, height=300)

# Group GP practice display
list_of_gps = re.sub(
    "\w+:",
    "",
    str(group_gp_list).replace("'", "").replace("[", "").replace("]", ""),
)
st.info("**Selected GP Practices: **" + list_of_gps)

gp_query = "practice_display == @place_state"
icb_query = "`ICB name` == @icb_state"  # escape column names with backticks https://stackoverflow.com/a/56157729

# dict to store all dfs sorted by ICB
dict_obj = {}
df_list = []

#FOR EACH PLACE in the SESSION STATE aggregate the data at the ICB and Place level, calculate indices 
#adds them to a dictionary object
for place in st.session_state.places:
    place_state = st.session_state[place]["gps"]
    icb_state = st.session_state[place]["icb"]
    # get place aggregations
    place_data, place_groupby = aggregate(
        data, gp_query, place, "Place Name", aggregations
    )
    # get ICB aggregations
    icb_data, icb_groupby = aggregate(
        data, icb_query, icb_state, "ICB name", aggregations
    )
    # index calcs
    place_indices, icb_indices = get_index(
        place_groupby, icb_groupby, index_names, index_numerator
    )
    icb_indices.insert(loc=0, column="Place / ICB", value=icb_state)
    place_indices.insert(loc=0, column="Place / ICB", value=place)
    
    if icb_state not in dict_obj:
        dict_obj[icb_state] = [icb_indices, place_indices]
    else:
        dict_obj[icb_state].append(place_indices)

# add dict values to list
for obj in dict_obj:
    df_list.append(dict_obj[obj])

# flaten list for concatination
flat_list = [item for sublist in df_list for item in sublist]
large_df = pd.concat(flat_list, ignore_index=True)
large_df = large_df.round(decimals=3)

# "Weighted G&A pop",
# "Weighted Community pop",
# "Weighted Mental Health pop",
# "Weighted Maternity pop",
# "Weighted Health Inequalities pop",
# "Weighted Prescribing pop",
# "Overall Weighted pop",

# order = [
#     0,
#     -9,
#     -8,
#     -7,
#     -6,
#     -5,
#     -4,
#     -2,
#     -3,
#     -1,
#     1,
#     2,
#     3,
#     4,
#     5,
#     6,
#     7,
#     8,
#     9,
#     10,
# ]  # setting column's order
# large_df = large_df[[large_df.columns[i] for i in order]]

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
#             place_metric, icb_metric = metric_calcs(dict_obj[option][count], metric,)
#             cols[metric_cols.index(metric)].metric(
#                 name, place_metric,  # icb_metric, delta_color="inverse"
#             )

# Metrics
# -------------------------------------------------------------------------

df = large_df.loc[large_df["Place / ICB"] == st.session_state.after]
df = df.reset_index(drop=True)

#Main Row
metric_cols = [
    "G&A Index",
    "Community Index",
    "Mental Health Index",
    "Maternity Index",
    "Prescribing Index",
]

metric_names = [
    "Gen & Acute",
    "Community*",
    "Mental Health",
    "Maternity",
    "Prescribing",
]

#Core Index
place_metric, icb_metric = metric_calcs(df, "Overall Core Index")
st.header("Core Index: " + str(place_metric))

with st.expander("Core Sub Indices", expanded  = True):

    cols = st.columns(len(metric_cols))
    for metric, name in zip(metric_cols, metric_names):
        place_metric, icb_metric = metric_calcs(
            df,
            metric,
        )
        cols[metric_cols.index(metric)].metric(
            name,
            place_metric,  # icb_metric, delta_color="inverse"
        )

#Primary Care Index
st.header("Primary Care Index: " + str(place_metric))
with st.expander("Primary Care Sub Indices", expanded  = True):
    st.write("None")

#Health Inequals row
place_metric, icb_metric = metric_calcs(df, "Health Inequalities Index")
cols = st.columns([2,3,2])
cols[1].subheader("Health Inequalities: " +str(place_metric))

# Downloads
# -------------------------------------------------------------------------
current_date = datetime.now().strftime("%Y-%m-%d")

st.subheader("Download Data")

print_table = st.checkbox("Preview data download", value=True)
if print_table:
    with st.container():
        utils.write_table(large_df)

csv = convert_df(large_df)

with open("docs/ICB allocation tool documentation.txt", "rb") as fh:
    readme_text = io.BytesIO(fh.read())

session_state_dict = dict.fromkeys(st.session_state.places, [])
for key, value in session_state_dict.items():
    session_state_dict[key] = st.session_state[key]
session_state_dict["places"] = st.session_state.places
session_state_dump = json.dumps(session_state_dict, indent=4, sort_keys=False)

# https://stackoverflow.com/a/44946732
zip_buffer = io.BytesIO()
with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
    for file_name, data in [
        ("ICB allocation calculations.csv", io.BytesIO(csv)),
        ("ICB allocation tool documentation.txt", readme_text),
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

st.subheader("Help and Support")
with st.expander("About the ICB Place Based Allocation Tool"):
    st.subheader("Allocations")
    st.markdown(
        "This tool is designed to support allocation at places by allowing places to be defined by aggregating GP Practices within an ICB. Please refer to the User Guide for instructions."
    )
    st.markdown("The tool estimates the relative need for places within the ICB.")
    st.markdown(
        "The Relative Need Index for ICB (i) and Defined Place (p) is given by the formula:"
    )
    st.latex(r""" (WP_p/GP_p)\over (WP_i/GP_i)""")
    st.markdown(
        "Where *WP* is the weighted population for a given need and *GP* is the GP practice population."
    )
    st.markdown(
        "This tool is based on estimated need for 2022/23 by utilising weighted populations projected from the October 2021 GP Registered Practice Populations."
    )
    st.markdown(
        "More information on the latest allocations, including contact details, can be found [here](https://www.england.nhs.uk/allocations/)."
    )
    st.subheader("Caveats and Notes")
    st.markdown(
        "*The Community Services index relates to the half of Community Services that are similarly distributed to district nursing. The published Community Services target allocation is calculated using the Community Services model. This covers 50% of Community Services. The other 50% is distributed through the General & Acute model."
    )
    st.markdown("")
st.info(
    "For support with using the AIF Allocation tool please email: [england.revenue-allocations@nhs.net](mailto:england.revenue-allocations@nhs.net)"
)

# Show Session Data
# -------------------------------------------------------------------------
if see_session_data:
    st.subheader("Session Data")
    st.session_state
