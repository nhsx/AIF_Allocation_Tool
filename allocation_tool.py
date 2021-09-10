# import packages
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import SessionState

# Download NHS Logo from an online source
url = "https://www.digitalartsonline.co.uk/cmsdata/features/3655443/nhs-logo-opener.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content))
if img.mode != 'RGB':
    img = img.convert('RGB')

# App appearance
st.image(img, width=100)
st.title("ICS Place Based Allocation Tool")
st.markdown(
    "This tool is designed to allow place, for allocation purposes, to be defined by aggregating GP Practices within an ICS. Please refer to the User Guide for instructions.")
st.markdown("The Relative Need Index for ICS (i) and Defined Place (p) is given by the formula:")
st.latex(r''' (WP_p/GP_p)\over (WP_i/GP_i)''')
st.markdown("This tool utilises weighted populations calculated from the 2018/19 GP Registered Practice Populations")

# Load data and cache
@st.cache
def get_data():
    path = "~/PycharmProjects/pythonProject3/gp_practice_weighted_population_by_ics v2.xlsx"
    return pd.read_excel(path, 1, 0, usecols="F,H,J,L,M:AC")


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Manipulate loaded dataframe
data = get_data()
data = data.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})  # Rename some columns with more sensible names
data["Practice"] = data["Practice"] + " " + ":" + " " + data["practice_name"]  # Concatenate practice name with practice code to ensure all practices are unique
data = data.drop(["practice_name"], axis=1)  #

# Session state initialisation and variables
col_list = list(data.columns.to_list())
col_list = col_list.append("Place_Name")
output_df = pd.DataFrame(columns=col_list)
session_state = SessionState.get(df=output_df, list=[])
flat_list = [item for sublist in session_state.list for item in sublist]  # session state list is a list of lists so this unpacks them into one single flat list to use later

# Drop downs for user manipulation/selection of data
ics = data['ICS'].drop_duplicates()
ics_choice = st.sidebar.selectbox("Select your ICS:", ics, help="Select an ICS")
ccgs = list(data['CCG19'].loc[data['ICS'] == ics_choice])
pcns = list(data['PCN_name'].loc[data['ICS'] == ics_choice])
practices = list(data["Practice"].loc[data["ICS"] == ics_choice])
practices = [x for x in practices if x not in flat_list]
practice_choice = st.sidebar.multiselect("Select practices", practices,
                                         help="Select GP Practices to aggregate into a single defined 'place'")
place_name = st.text_input("Place Name", "Group 1", help="Give your defined place a name to identify it")


# Buttons that provide functionality 
left, middle, right = st.columns(3)
with left:
    if st.button("Calculate", help="Calculate allocations and relative need for places"):
        session_state.df = session_state.df.apply(round)
        session_state.df = session_state.df.append(session_state.df.sum().rename('Total'))
        session_state.df["G&A_Index"] = (session_state.df["WP_G&A"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 1])/(session_state.df.iloc[-1, 0]))
        session_state.df["CS_Index"] = (session_state.df["WP_CS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 2])/(session_state.df.iloc[-1, 0]))
        session_state.df["MH_Index"] = (session_state.df["WP_MH"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 3])/(session_state.df.iloc[-1, 0]))
        session_state.df["Mat_Index"] = (session_state.df["WP_Mat"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 4])/(session_state.df.iloc[-1, 0]))
        session_state.df["HCHS_Index"] = (session_state.df["WP_HCHS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 5])/(session_state.df.iloc[-1, 0]))
with middle:
    if st.button("Save Place", help="Save the selected practices to the named place", key="output"):
        store_data().append({place_name: practice_choice})
        new_place = store_data()[0]
        place_practices = list(new_place.values())
        place_practices = place_practices[0]
        session_state.list.append(place_practices)
        place_key = list(new_place.keys())
        place_name = place_key[0]
        df_1 = data.query("Practice == @place_practices")
        df_1["Place_Name"] = place_name
        df_2 = df_1.groupby('Place_Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum',
             'Target_inc_remote_£k': 'sum'})
        session_state.df = session_state.df.append(df_2)
        store_data().clear()
with right:
    if st.button("Reset", help="Reset the place selections and start again. Press a second time to restore Practice dropdown list"):
        session_state.df.drop(session_state.df.index[:], inplace=True)
        session_state.list.clear()

# Write out dataframe
st.write(session_state.df)

# Temporary prototype notice
st.markdown("PROTOTYPE UNDER DEVELOPMENT")
