import streamlit as st
import fastf1 as ff1
from matplotlib import pyplot as plt

# Set up FastF1 with your API key
# fastf1 = ff1(api_key='your_api_key_here')

# Sidebar for user input
st.sidebar.title("Formula 1 Race Report Generator")

# Choose the year
selected_year = st.sidebar.selectbox("Select Year", list(range(2000, 2025)), index=len(list(range(2000, 2025))) - 1)

# Fetch the Grand Prix for the selected year
grands_prix = ff1.get_event_schedule(selected_year, include_testing=False, backend=None, force_ergast=False)
gp_name = grands_prix.EventName 
selected_grand_prix = st.sidebar.selectbox("Select Grand Prix", gp_name)

# Fetch the sessions for the selected Grand Prix
session_name = ["FP1", "FP2", "FP3", "Q", "R", "SS", "S"]
selected_session = st.sidebar.selectbox("Select Session", session_name)
session = ff1.get_session(selected_year, selected_grand_prix, selected_session)



# Fetch the drivers for the selected session
selected_driver1 = st.sidebar.text_input("Select Driver 1")
selected_driver2 = st.sidebar.text_input("Select Driver 2")

# Display selected options
st.write(f"Selected Year: {selected_year}")
st.write(f"Selected Grand Prix: {selected_grand_prix}")
st.write(f"Selected Session: {selected_session}")
st.write(f"Selected Driver 1: {selected_driver1}")
st.write(f"Selected Driver 2: {selected_driver2}")

session.load()
fast_d1 = session.laps.pick_driver(selected_driver1).pick_fastest()
fast_d2 = session.laps.pick_driver(selected_driver2).pick_fastest()

d1_car_data = fast_d1.get_car_data()
t1 = d1_car_data['Time']
vCar_1 = d1_car_data['Speed']

d2_car_data = fast_d2.get_car_data()
t2 = d2_car_data['Time']
vCar_2 = d2_car_data['Speed']

# The rest is just plotting
fig, ax = plt.subplots()
ax.plot(t1, vCar_1, label=selected_driver1)
ax.plot(t2, vCar_2, label=selected_driver2)
ax.set_xlabel('Time')
ax.set_ylabel('Speed [Km/h]')
ax.set_title(selected_driver1 + " vs " + selected_driver2)
ax.legend()
st.pyplot(fig)