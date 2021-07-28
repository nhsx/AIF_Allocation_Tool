import streamlit as st
import pandas as pd

# App appearance
st.title("ICS Place Based Allocation Tool")


# Load data and cache
@st.cache
def get_data():
    path = "~/PycharmProjects/pythonProject3/gp_practice_weighted_population_by_ics v2.xlsx"
    return pd.read_excel(path, 1, 0, usecols="F,H,J,L,M,O:AC")


data = get_data()
data = data.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})
data["Practice"] = data["Practice"] + " " + ":" + " " + data["practice_name"]
data = data.drop(["practice_name"], axis=1)
ics = data['ICS'].drop_duplicates()
ics_choice = st.sidebar.selectbox("Select your ICS:", ics)
ccgs = list(data['CCG19'].loc[data['ICS'] == ics_choice])
pcns = list(data['PCN_name'].loc[data['ICS'] == ics_choice])
practices = list(data["Practice"].loc[data["ICS"] == ics_choice])
practice_choice = st.sidebar.multiselect("Select practices", practices)
place_name = st.text_input("Place Name/Number", "group 1")
save_place = st.button("Save Place", help="Click here to save selected practices to defined place")


def new_df(df, column, values):
    """"
    Output a new dataframe based on the rows in the original dataframe passed to the function

    Args:
        df (pandas Dataframe): The dataframe containing the original values
        column (str): The column name in the dataframe from which the values are derived
        values (list): A list of column values that are contained in the dataframe whose rows will make up the new dataframe

    Returns:
        pandas Dataframe: The new dataframe that can be manipulated and aggregated

    """
    # Subset the dataframe
    new_data: object = df[df[column].isin(values)]
    return new_data


# Assign select practices to a dataframe
result1 = new_df(data, 'Practice', practice_choice)

# Add column that allows users to name the place they have defined, this column will be used for aggregation
result1 = result1.assign(Place=place_name)

# Aggregate selected GP practices into a single row for the defined place
result2 = result1.groupby('Place').agg({'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum'})

place_aggregation = pd.DataFrame()
place_aggregation.append(result2[0])

st.write(place_aggregation)
