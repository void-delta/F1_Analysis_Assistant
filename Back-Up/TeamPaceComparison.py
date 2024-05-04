import streamlit as st
import fastf1 as ff1
import seaborn as sns
import matplotlib.pyplot as plt

# Function to load session data
@st.cache
def load_session(year, grand_prix, session_type):
    session = ff1.get_session(year, grand_prix, session_type)
    session.load()
    return session

# Main code
st.title("Formula 1 Race Analysis Assistant")

selected_year = st.selectbox("Select Year", list(range(2000, 2025)), index=len(list(range(2000, 2025))) - 1)
grands_prix = ff1.get_event_schedule(selected_year, include_testing=False, backend=None, force_ergast=False)
gp_name = grands_prix.EventName 
selected_grand_prix = st.selectbox("Select Grand Prix", gp_name)
session_name = ["FP1", "FP2", "FP3", "Q", "R", "SS", "S"]
selected_session = st.selectbox("Select Session", session_name)
session = load_session(selected_year, selected_grand_prix, selected_session)

# Team pace comparison
st.header("Team Pace Comparison Analysis")
laps = session.laps.pick_quicklaps()

# Convert timedelta to seconds for plotting
laps['LapTime_seconds'] = laps['LapTime'].dt.total_seconds()

fig, ax = plt.subplots(figsize=(15, 10))
sns.boxplot(
    data=laps,
    x="Team",
    y="LapTime_seconds",  # Updated column name for seconds
    hue="Team",
    order=laps["Team"].unique(),  # Use unique teams for order
    palette="Set3",  # Example palette
    linewidth=1.5,  # Increase linewidth for better visibility
)

plt.title(session.event['EventName'])
plt.grid(visible=False)
ax.set(xlabel=None)
plt.tight_layout()
st.pyplot(fig)
