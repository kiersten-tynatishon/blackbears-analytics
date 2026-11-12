import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Black Bears Analytics", layout="wide")
st.title("Binghamton Black Bears - Shot Analytics Dashboard")

# Load & Clean Data
def load_data():
    df = pd.read_csv('shots_data.csv')
    
    # Numeric coordinates
    df['x_coord'] = pd.to_numeric(df['x_coord'], errors='coerce')
    df['y_coord'] = pd.to_numeric(df['y_coord'], errors='coerce')
    
    # Handle period column
    if 'period' in df.columns:
        df['period'] = pd.to_numeric(df['period'], errors='coerce').fillna(1).astype(int)
    else:
        df['period'] = 1

    # Handle game_date column
    if 'game_date' in df.columns:
        df['game_date'] = df['game_date'].astype(str).str.strip().replace({'': 'Unknown Date', 'nan': 'Unknown Date'})
    else:
        df['game_date'] = 'All Games'
        
    str_cols = ['opponent', 'team_shooting', 'shooter', 'f1', 'f2', 'f3', 'd1', 'd2', 'shot_type']
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().replace({'': 'None', 'nan': 'None'})
            
    return df.dropna(subset=['x_coord', 'y_coord'])

df = load_data()

# Sidebar Filters
st.sidebar.header("Filter Options")

# 1. Select Opponent
opponents_list = df['opponent'].unique() if len(df) > 0 else []
selected_opponent = st.sidebar.selectbox("Select Opponent:", options=opponents_list)

# 2. Select View Mode
view_mode = st.sidebar.radio(
    "View Mode:",
    ["Goals/Shots WE Scored", "Goals/Shots WE Allowed"]
)

# Filter by Shooting Team and Opponent
if selected_opponent:
    if view_mode == "Goals/Shots WE Scored":
        # Black Bears offensive shots taken against the selected opponent
        opponent_filtered_df = df[(df['opponent'] == selected_opponent) & (df['team_shooting'] == 'Binghamton Black Bears')]
        chart_title = f"Offensive Shots vs. {selected_opponent}"
    else:
        # Shots taken BY the opponent against Black Bears (anything where team_shooting != 'Binghamton Black Bears')
        opponent_filtered_df = df[(df['opponent'] == selected_opponent) & (df['team_shooting'] != 'Binghamton Black Bears')]
        chart_title = f"Defensive Shots Allowed vs. {selected_opponent}"
else:
    opponent_filtered_df = pd.DataFrame()
    chart_title = "Shot Analytics Dashboard"

# 3. Game Date Filter
available_dates = opponent_filtered_df['game_date'].unique() if len(opponent_filtered_df) > 0 else []
selected_dates = st.sidebar.multiselect(
    "Select Game Date(s):",
    options=available_dates,
    default=available_dates
)

date_filtered_df = opponent_filtered_df[opponent_filtered_df['game_date'].isin(selected_dates)]

# 4. Period Filter
period_options = ["All Periods", "1st Period", "2nd Period", "3rd Period", "Overtime"]
selected_period_label = st.sidebar.selectbox("Select Period:", period_options)

period_filtered_df = date_filtered_df.copy()
if selected_period_label == "1st Period":
    period_filtered_df = period_filtered_df[period_filtered_df['period'] == 1]
elif selected_period_label == "2nd Period":
    period_filtered_df = period_filtered_df[period_filtered_df['period'] == 2]
elif selected_period_label == "3rd Period":
    period_filtered_df = period_filtered_df[period_filtered_df['period'] == 3]
elif selected_period_label == "Overtime":
    period_filtered_df = period_filtered_df[period_filtered_df['period'] >= 4]

# 5. Player Filter
available_players = period_filtered_df['shooter'].unique() if len(period_filtered_df) > 0 else []
selected_player = st.sidebar.multiselect(
    "Select Player(s):",
    options=available_players,
    default=available_players
)

filtered_df = period_filtered_df[period_filtered_df['shooter'].isin(selected_player)]

# Key Performance Indicators
total_shots = len(filtered_df)
total_goals = filtered_df['is_goal'].sum() if total_shots > 0 else 0
shooting_pct = (total_goals / total_shots * 100) if total_shots > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Shots", total_shots)
col2.metric("Total Goals", total_goals)
col3.metric("Shooting %", f"{shooting_pct:.1f}%")

# Plotting Rink Canvas
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(-100, 100)
ax.set_ylim(-42.5, 42.5)
ax.set_facecolor('#f8f9fa')

# Outer Boards & Lines
ax.add_patch(patches.Rectangle((-100, -42.5), 200, 85, linewidth=2, edgecolor='black', facecolor='none'))
ax.plot([0, 0], [-42.5, 42.5], color='red', linewidth=3)      # Red Center Line
ax.plot([-25, -25], [-42.5, 42.5], color='blue', linewidth=3) # Defensive Blue Line
ax.plot([25, 25], [-42.5, 42.5], color='blue', linewidth=3)   # Offensive Blue Line
ax.plot([-89, -89], [-42.5, 42.5], color='red', linewidth=1.5) # Goal Lines
ax.plot([89, 89], [-42.5, 42.5], color='red', linewidth=1.5)

# Creases & Center Circle
ax.add_patch(patches.Arc((-89, 0), width=12, height=12, angle=0, theta1=-90, theta2=90, color='blue', fill=False))
ax.add_patch(patches.Arc((89, 0), width=12, height=12, angle=0, theta1=90, theta2=270, color='blue', fill=False))
ax.add_patch(patches.Circle((0, 0), radius=15, color='blue', fill=False, linewidth=1.5))
ax.add_patch(patches.Circle((0, 0), radius=1, color='blue', fill=True))

# End-Zone Faceoff Circles & Faceoff Dots
faceoff_coords = [(69, 22), (69, -22), (-69, 22), (-69, -22)]
for x, y in faceoff_coords:
    ax.add_patch(patches.Circle((x, y), radius=15, color='red', fill=False, linewidth=1.5))
    ax.add_patch(patches.Circle((x, y), radius=1, color='red', fill=True))

# Neutral Zone Dots
for x, y in [(20, 22), (20, -22), (-20, 22), (-20, -22)]:
    ax.add_patch(patches.Circle((x, y), radius=1, color='red', fill=True))

# NHL "Home Plate" Slot Area Diamonds
ax.plot([89, 89, 54, 54, 89], [-4, 4, 22, -22, -4], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
ax.plot([-89, -89, -54, -54, -89], [-4, 4, 22, -22, -4], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)

# Scatter Shot Plotting
if total_shots > 0:
    saves = filtered_df[filtered_df['is_goal'] == 0]
    goals = filtered_df[filtered_df['is_goal'] == 1]

    save_color, goal_color = ('gray', 'darkgreen') if view_mode == "Goals/Shots WE Scored" else ('grey', 'darkgreen')

    ax.scatter(saves['x_coord'], saves['y_coord'], c=save_color, alpha=0.6, label='Saved Shot', s=50)
    ax.scatter(goals['x_coord'], goals['y_coord'], c=goal_color, alpha=0.9, label='Goal', s=130, marker='*')

date_str = ", ".join(selected_dates) if len(selected_dates) > 0 else "No Date Selected"
ax.set_title(f"{chart_title} | Date(s): {date_str} ({selected_period_label})", fontsize=13, fontweight='bold')
ax.legend(loc='upper left')
ax.axis('off')

st.pyplot(fig)
