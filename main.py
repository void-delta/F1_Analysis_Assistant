import streamlit as st
import fastf1 as ff1
from fastf1 import plotting as fplt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import seaborn as sns

st.title("Formula 1 Race Analysis Assistant")

selected_year = st.selectbox("Select Year", list(range(2000, 2025)), index=len(list(range(2000, 2025))) - 1)

grands_prix = ff1.get_event_schedule(selected_year, include_testing=False, backend=None, force_ergast=False)
gp_name = grands_prix.EventName 
selected_grand_prix = st.selectbox("Select Grand Prix", gp_name)

session_name = ["FP1", "FP2", "FP3", "Q", "R", "SS", "S"]
selected_session = st.selectbox("Select Session", session_name)
session = ff1.get_session(selected_year, selected_grand_prix, selected_session)
session.load()

st.header("Fastest Laptime Comparison")

selected_driver1 = st.text_input("Select Driver 1")
selected_driver2 = st.text_input("Select Driver 2")

st.write(f"Selected Year: {selected_year}")
st.write(f"Selected Grand Prix: {selected_grand_prix}")
st.write(f"Selected Session: {selected_session}")
st.write(f"Selected Driver 1: {selected_driver1}")
st.write(f"Selected Driver 2: {selected_driver2}")

if selected_driver1 and selected_driver2:
    fast_d1 = session.laps.pick_driver(selected_driver1).pick_fastest()
    fast_d2 = session.laps.pick_driver(selected_driver2).pick_fastest()

    d1_car_data = fast_d1.get_car_data()
    t1 = pd.to_numeric(d1_car_data['Time'].dt.total_seconds())
    vCar_1 = d1_car_data['Speed']

    d2_car_data = fast_d2.get_car_data()
    t2 = pd.to_numeric(d2_car_data['Time'].dt.total_seconds())
    vCar_2 = d2_car_data['Speed']

    fig, ax = plt.subplots()
    ax.plot(t1, vCar_1, label=selected_driver1)
    ax.plot(t2, vCar_2, label=selected_driver2)
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Speed [Km/h]')
    ax.set_title(selected_driver1 + " vs " + selected_driver2)
    ax.legend()
    st.pyplot(fig)

st.header("Tyre Strategy Visualisation")

selected_driver_tyre = st.text_input("Select Driver for Tyre Strategy")

st.write(f"Selected Year: {selected_year}")
st.write(f"Selected Grand Prix: {selected_grand_prix}")
st.write(f"Selected Session: {selected_session}")
st.write(f"Selected Driver for Tyre Strategy: {selected_driver_tyre}")

if selected_driver_tyre:
    driver_laps = session.laps.pick_driver(selected_driver_tyre).pick_quicklaps().reset_index()

    # Convert timedelta to seconds for plotting
    driver_laps['LapTime_seconds'] = pd.to_numeric(driver_laps['LapTime'].dt.total_seconds())

    fig, ax = plt.subplots(figsize=(8, 8))
    sns.scatterplot(data=driver_laps,
                    x="LapNumber",
                    y="LapTime_seconds",
                    ax=ax,
                    hue="Compound",
                    palette={'HARD': '#000000', 'INTERMEDIATE': '#43b02a', 'MEDIUM': '#ffd12e', 'SOFT': '#da291c', 'TEST-UNKNOWN': '#434649', 'UNKNOWN': '#00ffff', 'WET': '#0067ad'},
                    s=80,
                    linewidth=0,
                    legend='auto')
    ax.set_ylabel('Lap Time (seconds)')
    ax.set_title(f"Lap Times for {selected_driver_tyre} by Tyre Compound")
    st.pyplot(fig)

# gearshift map
st.header("Gearshift Map")
selected_driver_map = st.text_input("Select Driver for Map Gearshift")

lap = session.laps.pick_driver(selected_driver_map).pick_fastest()
tel = lap.get_telemetry()

x = np.array(tel['X'].values)
y = np.array(tel['Y'].values)

points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
gear = tel['nGear'].to_numpy().astype(float)

cmap = plt.get_cmap('Paired')
lc_comp = LineCollection(segments, norm=plt.Normalize(1, cmap.N+1), cmap=cmap)
lc_comp.set_array(gear)
lc_comp.set_linewidth(4)

plt.gca().add_collection(lc_comp)
plt.axis('equal')
plt.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

title = plt.suptitle(
    f"Fastest Lap Gear Shift Visualization\n"
    f"{lap['Driver']} - {session.event['EventName']} {session.event.year}"
)

cbar = plt.colorbar(mappable=lc_comp, label="Gear",
                    boundaries=np.arange(1, 10))
cbar.set_ticks(np.arange(1.5, 9.5))
cbar.set_ticklabels(np.arange(1, 9))

# Save the entire plot, including the color bar
st.pyplot(plt.gcf())
