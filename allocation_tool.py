# import packages
import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
import SessionState  # this is a script within the working directory

# Download NHS Logo from an online source
url = "https://www.digitalartsonline.co.uk/cmsdata/features/3655443/nhs-logo-opener.png"
response = requests.get(url)  # fetch NHS logo from URL
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
@st.cache  # Use Streamlit cache decorator to cache this operation so data doesn't have to be read in everytime script is re-run
def get_data():
    path = "gp_practice_weighted_population_by_ics v2.xlsx"  # excel file containing the gp practice level data
    return pd.read_excel(path, 1, 0, usecols="F,H,J,L,M:AC")  # Dataframe with specific columns that will be used


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


# Manipulate loaded dataframe
data = get_data()
data = data.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})  # Rename some columns with more sensible names
data["Practice"] = data["Practice"] + " " + ":" + " " + data["practice_name"]  # Concatenate practice name with practice code to ensure all practices are unique
data = data.drop(["practice_name"], axis=1)  # Remove practice name column which is not needed anymore

# Session state initialisation and variables, this ensures that everytime a user adds a place, the previous places remain.
col_list = list(data.columns.to_list())  # create a list of columns exactly the same as those in the original data for the output df
col_list = col_list.append("Place_Name")  # add a Place Name column which will be used to group practices by defined place
output_df = pd.DataFrame(columns=col_list)  # initialise empty output dataframe with defined column names
session_state = SessionState.get(df=output_df, list=[], places=[])  # initialise session state, empty df that will hold places and empty list that will hold assigned practices
flat_list = [item for sublist in session_state.list for item in sublist]  # session state list is a list of lists so this unpacks them into one single flat list to use later

# Drop downs for user manipulation/selection of data
ics = data['ICS'].drop_duplicates()  # list of unique ICSs for dropdown list
ics_choice = st.sidebar.selectbox("Select your ICS:", ics, help="Select an ICS")  # dropdown for selecting ICS
practices = list(data["Practice"].loc[data["ICS"] == ics_choice])  # dynamic list of practices that changes based on selected ICS
practices = [x for x in practices if x not in flat_list]  # this removes practices that have been assigned to a place from the practices dropdown list
practice_choice = st.sidebar.multiselect("Select practices", practices,
                                         help="Select GP Practices to aggregate into a single defined 'place'")  # Dynamic practice dropdown
place_name = st.text_input("Place Name", "Group 1", help="Give your defined place a name to identify it")


# Buttons that provide functionality 
left, middle, right = st.columns(3)  # set 3 buttons on the same line
with left:
    if st.button("Calculate", help="Calculate allocations and relative need for places"):
        session_state.df = session_state.df.apply(round)
        session_state.df = session_state.df.append(session_state.df.sum().rename('{ics}'.format(ics=ics_choice)))
        session_state.df["G&A_Index"] = (session_state.df["WP_G&A"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 1])/(session_state.df.iloc[-1, 0]))
        session_state.df["CS_Index"] = (session_state.df["WP_CS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 2])/(session_state.df.iloc[-1, 0]))
        session_state.df["MH_Index"] = (session_state.df["WP_MH"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 3])/(session_state.df.iloc[-1, 0]))
        session_state.df["Mat_Index"] = (session_state.df["WP_Mat"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 4])/(session_state.df.iloc[-1, 0]))
        session_state.df["HCHS_Index"] = (session_state.df["WP_HCHS"]/session_state.df["GP_pop"])/((session_state.df.iloc[-1, 5])/(session_state.df.iloc[-1, 0]))
with middle:
    if st.button("Save Place", help="Save the selected practices to the named place", key="output"):
        store_data().append({place_name: practice_choice})  # append a dictionary to the cached list that has the place name as the key and a list of th
        new_place = store_data()[0]  # Extract the dictionary from the list
        session_state.places.append(new_place)  # Append the dictionary to a list that keeps track of practices in each place
        place_practices = list(new_place.values())  # Assign the practices in the newly defined place to a list
        place_practices = place_practices[0]  # place_practices is a list of lists so this turns it into a flat list
        session_state.list.append(place_practices)  # Save the assigned practices to session state to remove them from the practice dropdown list
        place_key = list(new_place.keys())  # Save place name to a list
        place_name = place_key[0]  # Extract place name from the list
        df_1 = data.query("Practice == @place_practices")  # Queries the original data and only returns the selected practices
        df_1["Place Name"] = place_name  # adds the place name to the dataframe to allow it to be used for aggregation
        df_2 = df_1.groupby('Place Name').agg(
            {'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum',
             'Target_inc_remote_£k': 'sum'})  # aggregates the practices to give the aggregated place values
        df_2 = df_2.apply(round)
        session_state.df = session_state.df.append(df_2)  # Add the aggregated place to session state
        store_data().clear()  # clear the data store so that this process can be repeated for next place
with right:
    if st.button("Reset", help="Reset the place selections and start again. Press a second time to restore Practice dropdown list"):
        session_state.df.drop(session_state.df.index[:], inplace=True)
        session_state.list.clear()
        session_state.places.clear()

# Write out dataframe
st.write(session_state.df)


# Download functionality
@st.cache
def convert_df(df):
    return df.to_csv().encode("utf-8")


csv = convert_df(session_state.df)
st.download_button(label="Download Output", data=csv, file_name="{ics} place based allocations.csv".format(ics=ics_choice), mime="text/csv")

# Temporary prototype notice
st.markdown("PROTOTYPE UNDER DEVELOPMENT")
