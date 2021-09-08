# import packages
import pandas as pd
import streamlit as st
from PIL import Image
import requests
from io import BytesIO


# Download NHS Logo from an online source and place on frontend
url = "https://www.digitalartsonline.co.uk/cmsdata/features/3655443/nhs-logo-opener.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content))
if img.mode != 'RGB':
    img = img.convert('RGB')

st.image(img, width=100)
st.title("ICS Place Based Allocation Tool")
st.markdown(
    "This tool is designed to allow place, for allocation purposes, to be defined by aggregating GP Practices within an ICS. Please refer to the User Guide for instructions.")
st.markdown("The Relative Need Index for ICS (i) and Defined Place (p) is given by the formula:")
st.latex(r''' (WP_p/GP_p)\over (WP_i/GP_i)''')


# create Practice class
class Practice:
    def __init__(self, practice_name, ics, ccg, pcn, gp_pop, wp_ga, wp_cs, wp_mh, wp_mat, wp_hchs, target_exc_remote,
                 target_inc_remote):
        self._practice_name = practice_name
        self._ccg = ccg
        self._pcn = pcn
        self._ics = ics
        self._gp_pop = gp_pop
        self._wp_ga = wp_ga
        self._wp_cs = wp_cs
        self._wp_mh = wp_mh
        self._wp_mat = wp_mat
        self._wp_hchs = wp_hchs
        self._target_exc_remote = target_exc_remote
        self._target_inc_remote = target_inc_remote

    def __str__(self):
        practice_str = """ 
        {name}
        """.format(name=self._practice_name)
        return practice_str

    def __repr__(self):
        return "Practice( '{name}', '{ccg}', '{pcn}', '{ics}, {gp_pop}, {wp_ga}, {wp_cs}, {wp_mh}, {wp_mat}, {wp_hchs}, {exc}, {inc}'".format(name=self._practice_name, ccg=self._ccg, pcn=self._pcn, ics=self._ics, gp_pop=self._gp_pop, wp_ga=self._wp_ga, wp_cs=self._wp_cs, wp_mh=self._wp_mh, wp_mat=self._wp_mat, wp_hchs=self._wp_hchs, exc=self._target_exc_remote, inc=self._target_inc_remote)

    @property
    def practice_name(self):
        return self._practice_name

    @property
    def ccg(self):
        return self._ccg

    @property
    def pcn(self):
        return self._pcn

    @property
    def ics(self):
        return self._ics

    @property
    def gp_pop(self):
        return self._gp_pop

    @property
    def wp_ga(self):
        return self._wp_ga

    @property
    def wp_cs(self):
        return self._wp_cs

    @property
    def wp_mh(self):
        return self._wp_mh

    @property
    def wp_mat(self):
        return self._wp_mat

    @property
    def wp_hchs(self):
        return self.wp_hchs

    @property
    def target_exc_remote(self):
        return self._target_exc_remote

    @property
    def target_inc_remote(self):
        return self._target_inc_remote


# Load and manipulate data from spreadsheet to assign to Practice objects and cache
@st.cache
def get_data():
    path = "~/PycharmProjects/pythonProject3/gp_practice_weighted_population_by_ics v2.xlsx"
    return pd.read_excel(path, 1, 0, usecols="F, H, I, J, L:S, Z, AA")


# Store defined places in a list to access them later for place based calculations
@st.cache(allow_output_mutation=True)
def store_data():
    return []


practice_data = get_data()  # Run cached function to load data from spreadsheet
practice_data = practice_data.rename(columns={"STP21_42": "ICS", "CCG19": "CCG", "GP practice name": "practice_name"})  # Give some columns more sensible names
practice_data["Practice"] = practice_data["Practice"] + " " + ":" + " " + practice_data["practice_name"]  # Concatenate practice name with practice number to ensure that each practice name is unique
practice_data = practice_data.drop(["practice_name"], axis=1)  # Drop column after concatenation
practice_data["PCN"] = practice_data["PCN"] + " " + ":" + " " + practice_data["PCN_name"]  # Concatenate PCN columns in similar way to practice columns
practice_data = practice_data.drop(["PCN_name"], axis=1)  # Drop column after concatenation
# Re-order columns to match positional arguments to create Practice class instances
practice_data = practice_data[['Practice', 'ICS', 'CCG', 'PCN', 'GP_pop', 'WP_G&A', 'WP_CS', 'WP_MH', 'WP_Mat', 'WP_HCHS', 'Target_exc_remote_£k', 'Target_inc_remote_£k']]

# Create practice objects
practices = practice_data.values.tolist()
practice_instances = []  # Initialise empty list to hold Practice object instances
# Run for loop that creates a practice instance for each of the practices in the dataframe
for p in practices:
    practice_instances.append(Practice(*p))

# Group practice objects into sub lists based on ICS attribute
ics_groups = {}  # Initialise an empty dictionary
# Group practices by their ICS attribute
for e in practice_instances:
    ics_groups.setdefault(e.ics, []).append(e)

data = pd.DataFrame.from_records(vars(o) for o in practice_instances)

ics_list = list(ics_groups.keys())

# Dropdown lists
ics_choice = st.sidebar.selectbox("Select your ICS:", ics_list, help="Select an ICS")
practices = list(ics_groups[ics_choice])
practice_choice = st.sidebar.multiselect("Select practices", practices,
                                         help="Select GP Practices to aggregate into a single defined 'place'")
place_name = st.text_input("Place Name", "Group 1", help="Give your defined place a name to identify it")

# Buttons
left, right = st.beta_columns(2)
with left:
    if st.button("Save Place", help="Save the selected practices to the named place"):
        pass
with right:
    if st.button("Reset", help="Reset the place selections and start again"):
        store_data().clear()

st.write(store_data())
print("hello world")
