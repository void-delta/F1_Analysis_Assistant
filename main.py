import streamlit as st
import fastf1 as ff1
from fastf1 import plotting as fplt
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import seaborn as sns
fplt.setup_mpl(misc_mpl_mods=False)

st.title("Formula 1 Race Analysis Assistant")
link_style = """
    text-decoration: none;
    padding: 8px 12px;
    background-color: #007bff;
    color: #ffffff;
    border-radius: 5px;
    font-weight: bold;
    display: inline-block;
    margin-bottom: 10px;
"""

# Display the link button styled as a traditional app button
st.markdown('<a href="https://void-delta.github.io/F1_Analysis_Assistant/" style="{}">Documentation</a>'.format(link_style), unsafe_allow_html=True)
st.markdown('''*Welcome to the Formula 1 Race Analysis Assistant!*

This application provides an interactive platform for analyzing Formula 1 race data. Whether you're a seasoned F1 enthusiast or a newcomer eager to delve into the world of motorsports analytics, this tool offers insights into race positions, fastest lap comparisons, tyre strategies, gearshift maps, driver performance, team pace comparisons, and more.

Select your preferred year, Grand Prix event, and session type to dive into the fascinating world of Formula 1 racing. Explore visualizations, compare driver performances, and uncover strategic insights to enhance your understanding of this exhilarating sport.

Let's embark on a thrilling journey through the data-rich universe of Formula 1 racing together!''')

selected_year = st.selectbox("Select Year", list(range(2018, 2025)), index=len(list(range(2018, 2025))) - 1)

grands_prix = ff1.get_event_schedule(selected_year, include_testing=False, backend=None, force_ergast=False)
gp_name = grands_prix.EventName 
selected_grand_prix = st.selectbox("Select Grand Prix", gp_name)

session_name = ["FP1", "FP2", "FP3", "Q", "R", "SS", "S"]
selected_session = st.selectbox("Select Session", session_name)
session = ff1.get_session(selected_year, selected_grand_prix, selected_session)

# Position Changes During Race
st.header("Position Changes During Race")
st.markdown('''
The *"Position Changes During Race"* section visualizes how drivers' positions change over the course of the race. This visualization is useful for:

- **Tracking Race Progress:** It provides a dynamic view of the race, showing which drivers gain or lose positions during each lap.

- **Analyzing Overtaking Opportunities:** Changes in position can indicate where overtaking maneuvers occur, offering insights into drivers' performance and race strategies.

- **Identifying Race Highlights:** Dramatic shifts in position can highlight key moments in the race, such as accidents, safety car periods, or strategic pit stops.

''')

session.load(telemetry=False, weather=False)
fig, ax = plt.subplots(figsize=(8.0, 4.9))
for drv in session.drivers:
    drv_laps = session.laps.pick_driver(drv)

    abb = drv_laps['Driver'].iloc[0]
    color = ff1.plotting.driver_color(abb)

    ax.plot(drv_laps['LapNumber'], drv_laps['Position'],
            label=abb, color=color)
ax.set_ylim([20.5, 0.5])
ax.set_yticks([1, 5, 10, 15, 20])
ax.set_xlabel('Lap')
ax.set_ylabel('Position')
ax.legend(bbox_to_anchor=(1.0, 1.02))
plt.tight_layout()

st.pyplot(fig)

# Fastest Laptime Comparison
session = ff1.get_session(selected_year, selected_grand_prix, selected_session)
session.load()
fig, ax = plt.subplots(figsize=(8.0, 4.9))

st.header("Fastest Laptime Comparison")
st.markdown('''The "Fastest Laptime Comparison" section allows you to compare the fastest laps of two selected drivers from a given session. This visualization is useful for:

- **Performance Analysis:** It shows differences in speed and performance, highlighting where one driver might be quicker than the other.

- **Driving Style Insights:** Comparing speed across time can reveal variations in driving style, indicating how aggressively or conservatively a driver handles certain sections of the track.

- **Strategy Indications:** Differences in speed and consistency can point to strategic choices, such as tyre compound, fuel load, or car setup.''')

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

# Tyre strategy visualisation
st.header("Tyre Strategy Visualisation")
st.markdown('''
The "Tyre Strategy Visualisation" section plots lap times against lap numbers for a selected driver, with points colored based on tyre compounds. This is useful for:

- **Understanding Tyre Strategy:** It provides a visual representation of a driver's tyre choices throughout a session, showing the impact of different compounds on performance and lap times.

- **Assessing Pit Stop Decisions:** By examining when and why tyre changes occur, you can infer pit stop strategies and their effects on race outcomes.

- **Performance Trends:** This visualization can highlight trends in lap times, helping to identify whether a driver maintained pace, experienced tyre degradation, or improved performance after a tyre change.
''')

selected_driver_tyre = st.text_input("Select Driver for Tyre Strategy")

st.write(f"Selected Year: {selected_year}")
st.write(f"Selected Grand Prix: {selected_grand_prix}")
st.write(f"Selected Session: {selected_session}")
st.write(f"Selected Driver for Tyre Strategy: {selected_driver_tyre}")

if selected_driver_tyre:
    driver_laps = session.laps.pick_driver(selected_driver_tyre).pick_quicklaps().reset_index()

    # Convert timedelta to seconds for plotting
    driver_laps['LapTime_seconds'] = pd.to_numeric(driver_laps['LapTime'].dt.total_seconds())

    fig_tyre, ax_tyre = plt.subplots(figsize=(8, 8))
    sns.scatterplot(data=driver_laps,
                    x="LapNumber",
                    y="LapTime_seconds",
                    ax=ax_tyre,
                    hue="Compound",
                    palette={'HARD': '#ffffff', 'INTERMEDIATE': '#43b02a', 'MEDIUM': '#ffd12e', 'SOFT': '#da291c', 'TEST-UNKNOWN': '#434649', 'UNKNOWN': '#00ffff', 'WET': '#0067ad'},
                    s=80,
                    linewidth=0,
                    legend='auto')
    ax_tyre.set_ylabel('Lap Time (seconds)')
    ax_tyre.set_title(f"Lap Times for {selected_driver_tyre} by Tyre Compound")
    st.pyplot(fig_tyre)

# Gearshift Map
st.header("Gearshift Map")
st.markdown('''
The "Gearshift Map" section visualizes the fastest lap of a selected driver, with color-coded lines representing gear shifts. 

This section is useful for:

- **Track Analysis:** It provides a visual representation of the track, showing where gear shifts occur and how frequently they happen.

- **Driving Style Assessment:** This visualization can reveal a driver's approach to corners and straight sections, offering insights into their driving style.

- **Vehicle Performance:** By examining gear shifts, you can understand how drivers utilize their car's power and torque across different sections of the track.
''')
selected_driver_map = st.text_input("Select Driver for Map Gearshift")

if selected_driver_map:
    lap_map = session.laps.pick_driver(selected_driver_map).pick_fastest()
    tel_map = lap_map.get_telemetry()

    x_map = np.array(tel_map['X'].values)
    y_map = np.array(tel_map['Y'].values)

    points_map = np.array([x_map, y_map]).T.reshape(-1, 1, 2)
    segments_map = np.concatenate([points_map[:-1], points_map[1:]], axis=1)
    gear_map = tel_map['nGear'].to_numpy().astype(float)

    cmap_map = plt.get_cmap('Paired')
    lc_comp_map = LineCollection(segments_map, norm=plt.Normalize(1, cmap_map.N+1), cmap=cmap_map)
    lc_comp_map.set_array(gear_map)
    lc_comp_map.set_linewidth(4)

    fig_map, ax_map = plt.subplots()
    ax_map.add_collection(lc_comp_map)
    ax_map.axis('equal')
    ax_map.tick_params(labelleft=False, left=False, labelbottom=False, bottom=False)

    title_map = ax_map.set_title(
        f"Fastest Lap Gear Shift Visualization\n"
        f"{selected_driver_map} - {session.event['EventName']} {session.event.year}"
    )

    cbar_map = plt.colorbar(mappable=lc_comp_map, label="Gear",
                            boundaries=np.arange(1, 10))
    cbar_map.set_ticks(np.arange(1.5, 9.5))
    cbar_map.set_ticklabels(np.arange(1, 9))

    # Save the entire plot, including the color bar
    st.pyplot(fig_map)


# Tyre Strategies during the race
st.header("Tyre Strategy During the Race")
st.markdown('''**Tyre Race Strategy** in Formula 1 is about smart choices in tyre compounds, pit stops, and managing tyre wear to optimize performance and race outcomes. It's a critical factor in the dynamic world of motorsports.
            ''')
laps = session.laps
drivers = session.drivers
drivers = [session.get_driver(driver)["Abbreviation"] for driver in drivers]
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = stints.groupby(["Driver", "Stint", "Compound"])
stints = stints.count().reset_index()
stints = stints.rename(columns={"LapNumber": "StintLength"})
fig, ax = plt.subplots(figsize=(3, 4))

for driver in drivers:
    driver_stints = stints.loc[stints["Driver"] == driver]

    previous_stint_end = 0
    for idx, row in driver_stints.iterrows():
        # each row contains the compound name and stint length
        # we can use these information to draw horizontal bars
        plt.barh(
            y=driver,
            width=row["StintLength"],
            left=previous_stint_end,
            color=fplt.COMPOUND_COLORS[row["Compound"]],
            edgecolor="black",
            fill=True
        )

        previous_stint_end += row["StintLength"]
plt.title(session.event['EventName'])
plt.xlabel("Lap Number")
plt.grid(False)
# invert the y-axis so drivers that finish higher are closer to the top
ax.invert_yaxis()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
st.pyplot(fig)


# Driver Laptimes Scatter Plot
st.header("Top 10 Driver Laptimes Scatter Plot")
st.markdown('''
The "Top 10 Driver Laptimes Scatter Plot" section compares the lap times of the top 10 finishers in a race. 

This visualization is useful for:

- **Performance Comparison:** It allows you to compare lap times across multiple drivers, highlighting differences in speed and consistency.

- **Tyre Strategy Analysis:** Variations in lap times can indicate differences in tyre degradation and pit stop strategies among drivers.

- **Race Recap:** By analyzing lap times, you can gain insights into the factors that influenced the outcome of the race, such as weather conditions, track evolution, and driver performance.
''')
fplt.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
race = ff1.get_session(selected_year, selected_grand_prix, selected_session)
race.load()
point_finishers = race.drivers[:10]
print(point_finishers)
driver_laps = race.laps.pick_drivers(point_finishers).pick_quicklaps()
driver_laps = driver_laps.reset_index()
finishing_order = [race.get_driver(i)["Abbreviation"] for i in point_finishers]
driver_colors = {abv: fplt.DRIVER_COLORS[driver] for abv,
                 driver in fplt.DRIVER_TRANSLATE.items()}
fig, ax = plt.subplots(figsize=(15, 10))

# Seaborn doesn't have proper timedelta support
# so we have to convert timedelta to float (in seconds)
driver_laps["LapTime(s)"] = driver_laps["LapTime"].dt.total_seconds()

sns.violinplot(data=driver_laps,
               x="Driver",
               y="LapTime(s)",
               hue="Driver",
               inner=None,
               density_norm="area",
               order=finishing_order,
               palette=driver_colors
               )

sns.swarmplot(data=driver_laps,
              x="Driver",
              y="LapTime(s)",
              order=finishing_order,
              hue="Compound",
              palette=fplt.COMPOUND_COLORS,
              hue_order=["SOFT", "MEDIUM", "HARD"],
              linewidth=0,
              size=4,
              )
ax.set_xlabel("Driver")
ax.set_ylabel("Lap Time (s)")
plt.suptitle(session.event['EventName'])
sns.despine(left=True, bottom=True)

plt.tight_layout()
st.pyplot(fig)

# team pace comparison
st.header("Team Pace Comparison Analysis")
st.markdown('''The **Team Pace Comparison Analysis** section compares the lap times of different Formula 1 teams. This visualization is useful for:

- Team Performance Assessment: It provides a comprehensive view of each team's pace throughout the race, highlighting strengths and weaknesses.
- Strategy Evaluation: Variations in lap times can reveal differences in race strategies among teams, such as tyre management, fuel strategy, and pit stop timing.
- Competitive Analysis: By comparing lap times across teams, you can assess the overall competitiveness of the field and identify potential areas for improvement.
''')
# Function to load session data
session = ff1.get_session(selected_year, selected_grand_prix, selected_session)
# Team pace comparison
team_session = ff1.get_session(selected_year, selected_grand_prix, selected_session)  # Rename session to team_session
team_session.load()  # Load team session data

# Team pace comparison
team_laps = team_session.laps.pick_quicklaps()  # Pick quicklaps for team comparison

# Convert timedelta to seconds for plotting
team_laps['LapTime_seconds'] = team_laps['LapTime'].dt.total_seconds()

fig_team, ax_team = plt.subplots(figsize=(15, 10))
sns.boxplot(
    data=team_laps,
    x="Team",
    y="LapTime_seconds",  # Updated column name for seconds
    hue="Team",
    order=team_laps["Team"].unique(),  # Use unique teams for order
    palette="Set3",  # Example palette
    linewidth=1.5,  # Increase linewidth for better visibility
)

plt.title(team_session.event['EventName'])  # Use team_session for event name
plt.grid(visible=False)
ax_team.set(xlabel=None)
plt.tight_layout()
st.pyplot(fig_team)

plt.close("all")

st.markdown("""---
The Formula 1 Race Analysis Assistant provides a powerful platform for exploring and analyzing Formula 1 race data. From tracking race progress to comparing lap times and understanding strategic decisions, this application offers a comprehensive toolkit for both seasoned enthusiasts and newcomers to dive deep into the world of motorsports analytics.

By leveraging interactive visualizations, performance comparisons, and strategic insights, users can gain a deeper understanding of Formula 1 races, drivers' performances, and team strategies. Whether you're interested in position changes, fastest lap comparisons, tyre strategies, or team pace analysis, this application caters to a wide range of analytical needs.

With its intuitive interface and rich data visualization capabilities, the Formula 1 Race Analysis Assistant empowers users to uncover valuable insights, enhance their race analysis skills, and enjoy a more immersive experience in the thrilling universe of Formula 1 racing.
""")


st.markdown('''
---
*Project created for course Software Engineering CS301*

*Undertaken by:*
*   Digant Singh
*   Eati Nikhilesh
*   Emani Srikar
*   Shri Harsha
''')
