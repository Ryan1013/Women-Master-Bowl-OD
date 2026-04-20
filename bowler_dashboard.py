import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PIL import Image

def detect_mobile():
    try:
        user_agent = st.context.headers["user-agent"]
        mobile_keywords = ["Mobile", "Android", "iPhone", "iPad"]
        return any(keyword in user_agent for keyword in mobile_keywords)
    except:
        return False

is_mobile = detect_mobile()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

if is_mobile:
    st.markdown("""
    <style>
    .mobile-filters-label {
        margin-top: -50px;   /* pulls it up under header */
        margin-left: 0px;   /* aligns after chevron */
        font-weight: 600;
        font-size: 16px;
    }
    </style>

    <div class="mobile-filters-label">
        Filters
    </div>
    """, unsafe_allow_html=True)

def apply_responsive_legend(fig):
    if is_mobile:
        fig.update_layout(
            legend=dict(
                orientation="h",
                y=-0.20,
                x=0.5,
                xanchor="center"
            ),
            margin=dict(l=0, r=0, t=10, b=80)
        )
    else:
        fig.update_layout(
            legend=dict(
                orientation="h",
                y=1.05,
                x=0.5,
                xanchor="center"
            ),
            margin=dict(l=0, r=0, t=40, b=20)
        )

st.title("One-Day Bowling Dashboard")

st.markdown("""
<div style="
    position: absolute;
    top: 0px;
    right: 0px;
    font-size: 8px;
    color: grey;
    text-align: right;
">
<b>Bowler Type Key:</b><br>
ROB = Right-arm Off Break<br>
RLB = Right-arm Leg Break<br>
RF = Right-arm Fast<br>
RFM = Right-arm Fast Medium<br>
RM = Right-arm Medium<br>
LOB = Left-arm Orthodox<br>
LLB = Left-arm Leg Break<br>
LF = Left-arm Fast<br>
LFM = Left-arm Fast Medium<br>
LM = Left-arm Medium<br>
WK = Wicketkeeper<br>
NA = Not Available
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("Master.csv", low_memory=False)

    # Date parsing
    df['Date'] = pd.to_datetime(
        df['Date'],
        format='%d/%m/%Y',
        errors='coerce'
    )

    df['Year'] = df['Date'].dt.year

    # Ensure Bowler Extra Runs exists
    if 'Bowler Extra Runs' not in df.columns:
        df['Bowler Extra Runs'] = 0

    # Total Runs Conceded
    df['Total Runs'] = (
        df['Runs'].fillna(0) +
        df['Bowler Extra Runs'].fillna(0)
    )

    # Clean Legal Ball
    df['Legal Ball'] = df['Legal Ball'].astype(str).str.lower()

    # Bowler Wicket flag
    non_bowler_dismissals = [
        'Run Out', 'Obstruction', 'Retired Hurt',
        'Retired - Not Out', 'Handled Ball', 'Absent'
    ]

    df['Bowler Wicket'] = (
        df['Wicket'].notna() &
        ~df['Wicket'].isin(non_bowler_dismissals)
    ).astype(int)

    # Phase
    def categorize_over(over):
        if 1 <= over <= 10:
            return 'Powerplay (1-10)'
        elif 11 <= over <= 25:
            return 'Upper Middle (11-25)'
        elif 26 <= over <= 40:
            return 'Lower Middle (26-40)'
        elif 41 <= over <= 50:
            return 'Death (41-50)'
        else:
            return None

    df['Phase'] = df['Over'].apply(categorize_over)

    # Bowling Type
    bowling_type_mapping = {
        'LLB': 'Spin', 'LOB': 'Spin', 'RLB': 'Spin', 'ROB': 'Spin',
        'LF': 'Pace', 'LFM': 'Pace', 'LM': 'Pace',
        'RF': 'Pace', 'RFM': 'Pace', 'RM': 'Pace'
    }

    df['Bowling Type'] = df['Bowler Type'].map(bowling_type_mapping)

    return df


data = load_data()

# ---------------- VIDEO LINKS ---------------- #

video_links = {
    "RN Cambampaty": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260226_PLAYLIST_1080.mp4",
        "Stock": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/yorkshire-women-v-middlesex-women---2-aug-2025/VPM_260304_YORW_MIDW_PLAYLIST_1080.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/glamorgan-women-v-middlesex-women---27-apr-2025/VPM_260304_GLAMW_MIDW_PLAYLIST_1080.mp4"
        },
    "HR Davis": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1.mp4",
        "Googly": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2.mp4"
        },
    "AK Dissanayake": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5.mp4",
        },
    "AE Downer": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/middlesex-women-v-worcestershire-rapids-women---30-aug-2025/VPM_260304_MIDW_WORCW_PLAYLIST_1080.mp4"
        },
    "HC Francis": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/leicestershire-women-v-middlesex-women---16-aug-2025/VPM_260304_LEIW_MIDW_PLAYLIST_1080.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/leicestershire-women-v-middlesex-women---16-aug-2025/VPM_260304_LEIW_MIDW_PLAYLIST_1080_1.mp4"
        },
    "GKS Gole": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7.mp4",
        "Slower": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11.mp4"
        },
    "SM Horley": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8.mp4",
        "Turn In": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9.mp4"
    },
    "GV Irving": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/middlesex-women-v-worcestershire-rapids-women---30-aug-2025/VPM_260304_MIDW_WORCW_PLAYLIST_1080_1.mp4"
    },
    "LE Judge": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14.mp4"
    },
    "NT Miles": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/middlesex-women-v-derbyshire-falcons-women---9-aug-2025/VPM_260304_MIDW_FALCW_PLAYLIST_1080.mp4"
    },
    "A Patel": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15.mp4"
    },
    "S Patel": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260304_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18.mp4"
    },
    "S Pearson": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080.mp4",
        "Slower": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11.mp4"
    },
    "IFK Routledge": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1.mp4",
        "Turn In": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2.mp4"
    },
    "L Turner": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10.mp4"
    },
    "REA Tyson": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/middlesex-women-v-gloucestershire-women---15-may-2025/VPM_260310_MIDW_GLOSW_PLAYLIST_1080.mp4"
    },
    "KJ Wolfe": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5_6.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_720.mp4",
        "Slower": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5_6_7_8.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260310_PLAYLIST_1080_1_2_3_4_5_6_7_8_9.mp4"
    },
    "LA Bailey": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3.mp4"
    },
    "OJ Barnes": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/worcestershire-rapids-women-v-kent-women---3-aug-2025/VPM_260404_WORCW_KENTW_PLAYLIST_1080.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/worcestershire-rapids-women-v-kent-women---3-aug-2025/VPM_260404_WORCW_KENTW_PLAYLIST_1080_1.mp4"
    },
    "EG Barnfather": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5.mp4"
    },
    "MS Belt": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6.mp4",
        "Turn In": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7.mp4"
    },
    "Z Bilal": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12.mp4"
    },
    "MC Callaghan": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13.mp4"
    },
    "EL Darlington": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18.mp4"
    },
    "AG Gordon": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19.mp4",
        "Turn In": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20.mp4"
    },
    "SR Gorham": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22.mp4"
    },
    "AF Grant": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23.mp4",
        "Yorker": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24.mp4"
    },
    "IG James": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26.mp4"
    },
    "GRK Jeer": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27.mp4",
        "Seam In/Inswinger": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/worcestershire-rapids-women-v-kent-women---3-aug-2025/VPM_260404_WORCW_KENTW_PLAYLIST_1080_1_2.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27_28.mp4"
    },
    "GA Poole": {
        "No Movement": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27_28_29.mp4",
        "Seam Away/Outswinger": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27_28_29_30.mp4"
    },
    "SA Singer": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2026/VPM_260404_PLAYLIST_1080_1_2_3_4_5_6_7_8_9_10_11_12_13_14_15_16_17_18_19_20_21_22_23_24_25_26_27_28_29_30_31.mp4",
        "Turn Away": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/worcestershire-rapids-women-v-kent-women---3-aug-2025/VPM_260404_WORCW_KENTW_PLAYLIST_1080_1_2_3.mp4"
    },
    "ML Sturge": {
        "No Turn": "https://vid.ecb.nvplay.net/video-highlights/2025/metro-bank-one-day-cup---women-league-2/sussex-sharks-women-v-kent-women---15-may-2025/VPM_260404_SUSW_KENTW_PLAYLIST_1080.mp4"
    }
}

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

st.sidebar.header("Filters")

# ---------------- COMPETITION FILTER ---------------- #

levels = sorted(data['Competition'].dropna().unique())

selected_levels = st.sidebar.multiselect(
    "Competition",
    levels,
    default=levels
)

# Bowling Team
teams = sorted(data['Bowling Team'].dropna().unique())

selected_teams = st.sidebar.multiselect(
    "Bowling Team",
    teams,
    default=["Glamorgan Women"] if "Glamorgan Women" in teams else teams[:1]
)

# Bowler (dependent)
if selected_teams:
    team_filtered = data[data['Bowling Team'].isin(selected_teams)]
else:
    team_filtered = data.copy()

# ------------------------------------------
# Create Bowler + Most Frequent Type label
# ------------------------------------------

bowler_type_mode = (
    team_filtered
    .dropna(subset=["Bowler"])
    .groupby("Bowler")["Bowler Type"]
    .agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    .reset_index()
)

bowler_type_mode["Display Name"] = (
    bowler_type_mode["Bowler"] + " (" +
    bowler_type_mode["Bowler Type"].fillna("NA") + ")"
)

# Create mapping
display_to_bowler = dict(
    zip(bowler_type_mode["Display Name"], bowler_type_mode["Bowler"])
)

display_options = sorted(display_to_bowler.keys())

selected_display = st.sidebar.multiselect(
    "Bowler",
    display_options,
    default=display_options[:1] if len(display_options) > 0 else []
)

# Convert back to actual bowler names
selected_bowlers = [display_to_bowler[d] for d in selected_display]

# Year
years = sorted(data['Year'].dropna().unique())

selected_years = st.sidebar.multiselect(
    "Year",
    years,
    default=years
)

# ---------------------------------------------------
# PHASE FILTER
# ---------------------------------------------------

phases = [
    "Powerplay (1-10)",
    "Upper Middle (11-25)",
    "Lower Middle (26-40)",
    "Death (41-50)"
]

selected_phases = st.sidebar.multiselect(
    "Phase",
    phases,
    default=phases
)

# ---------------------------------------------------
# PITCH MAP FILTER
# ---------------------------------------------------

st.sidebar.subheader("Pitch Map & Beehive")

pitch_options = [0, 1, 2, 3, 4, 6, "Wide", "Dismissal"]

selected_pitch_options = st.sidebar.multiselect(
    "Select Outcome",
    options=pitch_options,
    default=pitch_options
)

# Venue
venues = sorted(data['Venue'].dropna().unique())

selected_venues = st.sidebar.multiselect(
    "Venue",
    venues,
    default=venues
)

# ---------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------

filtered = data.copy()

# Filter by selected teams
if selected_levels:
    filtered = filtered[filtered['Competition'].isin(selected_levels)]

if selected_teams:
    filtered = filtered[filtered['Bowling Team'].isin(selected_teams)]

if selected_bowlers:
    filtered = filtered[filtered['Bowler'].isin(selected_bowlers)]

if selected_years:
    filtered = filtered[filtered['Year'].isin(selected_years)]

if selected_phases:
    filtered = filtered[filtered["Phase"].isin(selected_phases)]

if selected_venues:
    filtered = filtered[filtered['Venue'].isin(selected_venues)]

# ---------------------------------------------------
# GLOBAL OUTCOME FILTER
# ---------------------------------------------------

outcome_filtered = pd.DataFrame()

is_wide = filtered["Extra"].astype(str).str.contains("Wide", case=False, na=False)
is_dismissal = filtered["Bowler Wicket"] == 1

# Separate selected numeric run values
selected_runs = [x for x in selected_pitch_options if isinstance(x, int)]

# Build mask for each condition
run_mask = filtered["Runs"].isin(selected_runs)

wide_mask = is_wide if "Wide" in selected_pitch_options else False
dismissal_mask = is_dismissal if "Dismissal" in selected_pitch_options else False

# Combine everything
mask = run_mask | wide_mask | dismissal_mask

outcome_filtered = filtered[mask]

# ---------------------------------------------------
# BOWLER STATS KPI SECTION
# ---------------------------------------------------

st.subheader("Bowler Stats")

bowler_innings_count = filtered[
    filtered['Bowler'].isin(selected_bowlers)
].groupby(['Match', 'Date', 'Innings']).ngroups

st.caption(f"Sample Size: {bowler_innings_count} innings")

bowler_df = filtered.copy()

runs_conceded = bowler_df['Total Runs'].sum()

legal_balls = bowler_df[
    bowler_df['Legal Ball'] == "yes"
].shape[0]

dismissals = bowler_df[
    bowler_df['Bowler Wicket'] == 1
].shape[0]

bowling_average = round(runs_conceded / dismissals, 1) if dismissals > 0 else "—"
strike_rate = round(legal_balls / dismissals, 1) if dismissals > 0 else "—"

runs_conceded = bowler_df['Total Runs'].sum()

legal_balls = bowler_df[
    bowler_df['Legal Ball'] == "yes"
].shape[0]

economy_rate = (
    round((runs_conceded / legal_balls) * 6, 1)
    if legal_balls > 0 else "—"
)

dot_balls = bowler_df[
    (bowler_df['Legal Ball'] == "yes") &
    (bowler_df['Runs'] == 0)
].shape[0]

dot_ball_percentage = round(
    (dot_balls / legal_balls) * 100, 1
) if legal_balls > 0 else 0

col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

col1.metric("Runs Conceded", runs_conceded)
col2.metric("Balls Bowled", legal_balls)
col3.metric("Dismissals", dismissals)
col4.metric("Average", bowling_average)
col5.metric("Strike Rate", strike_rate)
col6.metric("Economy", economy_rate)
col7.metric("Dot %", f"{dot_ball_percentage}")

# ---------------------------------------------------
# PITCH MAP
# ---------------------------------------------------

st.subheader("Pitch Map")

pitch_data = outcome_filtered[
    outcome_filtered['PitchX'].notna() &
    outcome_filtered['PitchY'].notna()
].copy()

# -------------------------------------------
# IDENTIFY WIDES & DISMISSALS
# -------------------------------------------
pitch_data["IsWide"] = pitch_data["Extra"].astype(str).str.contains("Wide", case=False, na=False)
pitch_data["IsDismissal"] = pitch_data["Bowler Wicket"] == 1

# -------------------------------------------
# APPLY FILTER
# -------------------------------------------

if len(pitch_data) > 0:

    fig = go.Figure()

    # -------------------------------------------
    # SCALE SETTINGS
    # -------------------------------------------
    width_scale = 2
    height_scale = 0.5
    original_width_half = 1.3
    original_height = 20

    x_min = -original_width_half * width_scale
    x_max =  original_width_half * width_scale

    y_min = -0.12 * height_scale
    y_max =  original_height * height_scale

    pitch_data["PlotX"] = pitch_data["PitchY"] * width_scale
    pitch_data["PlotY"] = (original_height - pitch_data["PitchX"]) * height_scale

    # -------------------------------------------
    # BACKGROUND IMAGE
    # -------------------------------------------
    from PIL import Image
    img = Image.open("cp.jpg")

    fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=x_min,
            y=y_max,
            sizex=(x_max - x_min),
            sizey=(y_max - y_min),
            sizing="stretch",
            layer="below",
            xanchor="left",
            yanchor="top"
        )
    )

    # ---------------------------------------------------
    # LENGTH TICK MARKS (2m intervals, 2–18m)
    # ---------------------------------------------------

    for length in range(2, 20, 2):
        y_position = (original_height - length) * height_scale

        fig.add_shape(
            type="line",
            x0=1.2 * width_scale,
            x1=1.3 * width_scale,
            y0=y_position,
            y1=y_position,
            line=dict(color="black", width=2)
        )

        fig.add_annotation(
            x=1.35 * width_scale,
            y=y_position,
            text=f"<b>{length}m</b>",
            showarrow=False,
            xanchor="left",
            yanchor="middle",
            font=dict(size=12)
        )

    # -------------------------------------------
    # UPDATED COLOUR MAP (CLEAR DIFFERENCE)
    # -------------------------------------------
    colour_map = {
    0: "#808080",      # Grey
    1: "#FFFFFF",      # White
    2: "#1f77b4",      # Existing blue
    3: "#8B4513",      # Brown
    4: "#B8860B",      # Dark yellow (GoldenRod)
    6: "#000000"       # Black
}

    # -------------------------------------------
    # PLOT RUNS
    # -------------------------------------------
    for run, colour in colour_map.items():

        if run in selected_pitch_options:

            subset = pitch_data[
                (pitch_data["Runs"] == run) &
                (pitch_data["IsWide"] == False)
            ]

            if len(subset) > 0:
                fig.add_trace(go.Scatter(
                    x=subset["PlotX"],
                    y=subset["PlotY"],
                    mode="markers",
                    marker=dict(
                        size=8,
                        color=colour,
                        line=dict(width=1, color="black")
                        ),
                    name=f"<b>{run} Runs</b>"
                    ))

    # -------------------------------------------
    # PLOT WIDES
    # -------------------------------------------
    if "Wide" in selected_pitch_options:

        wides = pitch_data[pitch_data["IsWide"] == True]

        if len(wides) > 0:
            fig.add_trace(go.Scatter(
                x=wides["PlotX"],
                y=wides["PlotY"],
                mode="markers",
                marker=dict(
                    size=8,
                    color="#8A2BE2",
                    line=dict(width=1, color="black")
                    ),
                name="<b>Wide</b>"
            ))

    # -------------------------------------------
    # PLOT DISMISSALS
    # -------------------------------------------
    if "Dismissal" in selected_pitch_options:

        dismissals = pitch_data[pitch_data["IsDismissal"] == True]

        if len(dismissals) > 0:
            fig.add_trace(go.Scatter(
                x=dismissals["PlotX"],
                y=dismissals["PlotY"],
                mode="markers",
                marker=dict(
                    size=12,
                    color="red",
                    symbol="x",
                    line=dict(width=2, color="black")
                    ),
                name="<b>Dismissal</b>"
            ))

    # -------------------------------------------
    # LAYOUT
    # -------------------------------------------
    fig.update_layout(
        height=500,
        xaxis=dict(range=[x_min, x_max], visible=False, fixedrange=True),
        yaxis=dict(range=[y_min, y_max], visible=False, fixedrange=True),
        margin=dict(l=0, r=0, t=20, b=20),
        dragmode=False,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            bordercolor="black",
            borderwidth=1,
            bgcolor="#E8F5E9",   # Light green
            font=dict(color="black")
            )
        )

    fig.update_yaxes(scaleanchor="x", scaleratio=1)

    st.plotly_chart(fig, use_container_width=True)

else:
    st.write("No pitch data available for selected options.")

# ---------------------------------------------------
# CENTERED LENGTH EVALUATION (Below Pitch Map)
# ---------------------------------------------------

if "Analyst Pitch Length" in filtered.columns:

    length_series = filtered["Analyst Pitch Length"].dropna()

    if len(length_series) > 0:

        avg_length = round(length_series.mean(), 2)

        def categorize_length_raw(length):
            if length <= 1:
                return "Full Toss"
            elif 1 < length <= 1.5:
                return "Yorker"
            elif 1.5 < length <= 5:
                return "Full"
            elif 5 < length <= 7:
                return "Good Length"
            elif 7 < length <= 8:
                return "Back of Length"
            elif 8 < length <= 11:
                return "Short"
            else:
                return "Bouncer"

        length_category = categorize_length_raw(avg_length)

        left, center, right = st.columns([1, 2, 1])

        with center:
            st.markdown(
                f"""
                <div style="text-align:center; margin-top:-15px;">
                    <div style="font-size:32px; font-weight:600; margin-bottom:2px;">
                        Average Length
                    </div>
                    <div style="font-size:48px; font-weight:700; line-height:1;">
                        {avg_length} m
                    </div>
                    <div style="font-size:32px; color:#555; margin-top:2px;">
                        {length_category}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        st.info("No Analyst Pitch Length data available.")

else:
    st.warning("'Analyst Pitch Length' column not found in dataset.")

# ---------------- BEEHIVE ---------------- #

st.subheader("Beehive")

beehive_data = outcome_filtered[
    outcome_filtered['Analyst Arrival Line'].notna() &
    outcome_filtered['Analyst Arrival Height'].notna()
].copy()

if len(beehive_data) > 0:

    fig = go.Figure()
    img = Image.open("BA Beehive.png")

    x_min_m = -1.83
    x_max_m =  1.83
    y_min_m =  0
    y_max_m =  2.0

    fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=x_min_m,
            y=y_max_m,
            sizex=(x_max_m - x_min_m),
            sizey=(y_max_m - y_min_m),
            sizing="stretch",
            layer="below"
        )
    )

    # ---------------- RUN COLOURS ---------------- #

    colour_map = {
        0: "#B0B0B0",
        1: "#ADD8E6",
        2: "#FFD700",
        3: "#FF69B4",
        4: "green",
        6: "red"
    }

    # ---------------- RUN TRACES ---------------- #

    for run_value, colour in colour_map.items():

        subset = beehive_data[
            beehive_data['Runs'] == run_value
        ]

        if len(subset) > 0:
            fig.add_trace(go.Scatter(
                x=subset['Analyst Arrival Line'],
                y=subset['Analyst Arrival Height'],
                mode="markers",
                marker=dict(
                    size=12 if run_value == 6
                         else 10 if run_value == 4
                         else 8,
                    color=colour,
                    line=dict(width=1, color="black")
                ),
                name=f"{run_value} Runs"
            ))

    # ---------------- WIDES ---------------- #

    if "Wide" in selected_pitch_options:

        wides = beehive_data[
            beehive_data["Extra"].astype(str).str.contains("Wide", case=False, na=False)
        ]

        if len(wides) > 0:
            fig.add_trace(go.Scatter(
                x=wides['Analyst Arrival Line'],
                y=wides['Analyst Arrival Height'],
                mode="markers",
                marker=dict(
                    size=8,
                    color="#8A2BE2",
                    line=dict(width=1, color="black")
                ),
                name="Wide"
            ))

    # ---------------- DISMISSALS ---------------- #

    if "Dismissal" in selected_pitch_options:

        dismissals = beehive_data[
            beehive_data['Bowler Wicket'] == 1
        ]

        if len(dismissals) > 0:
            fig.add_trace(go.Scatter(
                x=dismissals['Analyst Arrival Line'],
                y=dismissals['Analyst Arrival Height'],
                mode="markers",
                marker=dict(
                    symbol="x",
                    size=14,
                    color="black",
                    line=dict(width=2)
                ),
                name="Dismissal"
            ))

    # ---------------- LAYOUT ---------------- #

    fig.update_layout(
        height=750,
        xaxis=dict(range=[x_min_m, x_max_m], visible=False),
        yaxis=dict(range=[y_min_m, y_max_m], visible=False),
        margin=dict(l=0, r=0, t=20, b=20),
        dragmode=False
    )

    fig.update_yaxes(scaleanchor="x")

    apply_responsive_legend(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "scrollZoom": False,
            "displaylogo": False,
            "modeBarButtonsToRemove": [
                "zoom2d",
                "select2d",
                "lasso2d"
            ]
        }
    )

else:
    st.write("No delivery data available.")

# ---------------------------------------------------
# BUSINESS AREA LOGIC
# ---------------------------------------------------

def in_business_area(line, height, hand):
    if pd.isna(line) or pd.isna(height) or pd.isna(hand):
        return False
    if hand == "RHB":
        return (height <= 1.0) and (-0.35 <= line <= 0.15)
    elif hand == "LHB":
        return (height <= 1.0) and (-0.10 <= line <= 0.40)
    return False

filtered["In Business Area"] = filtered.apply(
    lambda r: in_business_area(
        r.get("Analyst Arrival Line"),
        r.get("Analyst Arrival Height"),
        r.get("Batting Hand")
    ),
    axis=1
)

filtered["Bowler Wicket in BA"] = (
    filtered["In Business Area"] & (filtered["Bowler Wicket"] == 1)
)

# ---------------------------------------------------
# BOWLER BUSINESS AREA SUMMARY
# ---------------------------------------------------

bowler_ba_stats = (
    filtered.groupby("Bowler")
    .agg(
        Total_Deliveries=("Ball", "count"),
        BA_Deliveries=("In Business Area", "sum"),
        Total_Wickets=("Bowler Wicket", "sum"),
        BA_Wickets=("Bowler Wicket in BA", "sum")
    )
    .reset_index()
)

bowler_ba_stats["BA %"] = round(
    (bowler_ba_stats["BA_Deliveries"] / bowler_ba_stats["Total_Deliveries"]) * 100,
    2
)

# ---------------- BUSINESS AREA SUMMARY ---------------- #

if len(bowler_ba_stats) > 0:

    total_deliveries = bowler_ba_stats["Total_Deliveries"].sum()
    total_ba = bowler_ba_stats["BA_Deliveries"].sum()
    total_wickets = bowler_ba_stats["Total_Wickets"].sum()
    total_ba_wickets = bowler_ba_stats["BA_Wickets"].sum()

    ba_percent = round((total_ba / total_deliveries) * 100, 2) if total_deliveries > 0 else 0

    left, center, right = st.columns([1, 2, 1])

    with center:
        st.markdown(
            f"""
            <div style="text-align:center; margin-top:-15px;">
                <div style="font-size:20px; font-weight:600; margin-bottom:2px;">
                    % of Deliveries in Business Area (BA) / Around Stumps
                </div>
                <div style="font-size:48px; font-weight:700; line-height:1;">
                    {ba_percent}
                </div>
                <div style="font-size:28px; color:#555; margin-top:4px;">
                    {total_ba_wickets}/{total_wickets} Wickets in BA / Around Stumps
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

else:
    st.info("No Business Area data available.")

# ---------------- VIDEO SECTION ---------------- #

st.subheader("Videos (Filters not applicable to this section)")

if len(selected_bowlers) == 1:

    bowler_name = selected_bowlers[0]

    if bowler_name in video_links:

        bowler_videos = video_links[bowler_name]

        # Only show categories that exist
        for category, link in bowler_videos.items():

            st.markdown(f"**{category}**")
            st.video(link)

    else:
        st.write("No video links available for selected bowler.")

else:
    st.write("Select a single bowler to view video highlights.")
