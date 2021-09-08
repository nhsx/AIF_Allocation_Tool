import pandas as pd

# Load data, to future proof the data loading, potentially have this loaded from a URL where the file is kept online
practice_data = pd.read_excel("~/PycharmProjects/pythonProject3/gp_practice_weighted_population_by_ics v2.xlsx", 1, 0,
                              usecols="F,H,J,L,M:AC")
practice_data = practice_data.rename(columns={"STP21_42": "ICS", "GP practice name": "practice_name"})

print(practice_data.head())

# To ensure that all practices are unique, join the practice name and practice code columns then drop the practice name column
practice_data["Practice"] = practice_data["Practice"] + " " + ":" + " " + practice_data["practice_name"]
practice_data = practice_data.drop(["practice_name"], axis=1)

# Allow user to select the ICS of their choice
ics = "Cumbria and North East"
ics_data = practice_data[practice_data['ICS'] == ics]
practices = list(ics_data["Practice"])

print(ics_data.head())
print(len(practices))

chunks = [practices[x:x + 50] for x in range(0, len(practices), 50)]
places = {}
for idx, chunk in enumerate(chunks):
    places["place_%s" % idx] = ics_data[ics_data["Practice"].isin(chunk)]

for key, value in places.items():
    value2 = value.assign(Place=key)
    places[key] = value2

aggregated_places = {}


for key, value in places.items():
    value2 = value.groupby('Place').agg({'GP_pop': 'sum', 'WP_G&A': 'sum', 'WP_CS': 'sum', 'WP_MH': 'sum', 'WP_Mat': 'sum', 'WP_HCHS': 'sum', 'Target_inc_remote_£k': 'sum'})
    aggregated_places[key] = value2

ics_output = pd.concat(aggregated_places.values(), ignore_index=True)
ics_output = ics_output.apply(round)
ics_output = ics_output.append(ics_output.sum().rename('Total'))

ics_output["G&A_Index"] = (ics_output["WP_G&A"]/ics_output["GP_pop"])/((ics_output.iloc[8, 1])/(ics_output.iloc[8, 0]))
ics_output["CS_Index"] = (ics_output["WP_CS"]/ics_output["GP_pop"])/((ics_output.iloc[8, 2])/(ics_output.iloc[8, 0]))
ics_output["MH_Index"] = (ics_output["WP_MH"]/ics_output["GP_pop"])/((ics_output.iloc[8, 3])/(ics_output.iloc[8, 0]))
ics_output["Mat_Index"] = (ics_output["WP_Mat"]/ics_output["GP_pop"])/((ics_output.iloc[8, 4])/(ics_output.iloc[8, 0]))
ics_output["HCHS_Index"] = (ics_output["WP_HCHS"]/ics_output["GP_pop"])/((ics_output.iloc[8, 5])/(ics_output.iloc[8, 0]))

print(ics_output.info())

print("hi")
