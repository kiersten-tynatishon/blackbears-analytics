import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

st.set_page_config(page_title="Black Bears Analytics", layout="wide")
st.title("Binghamton Black Bears - Full Rink Analytics Dashboard")

# Load data (cache removed so CSV edits update instantly)
def load_data():
    return pd.read_csv('shots_data.csv')

df = load_data()

# Sidebar Filters
st.sidebar.header("Game & Opponent Filters")

# 1. Select Opponent
selected_opponent = st.sidebar.selectbox(
    "Select Opponent:",
    options=df['opponent'].unique()
)

# 2. Select View Perspective
view_mode = st.sidebar.radio(
    "View Mode:",
    ["Goals/Shots WE Scored", "Goals/Shots WE Allowed"]
)

# 3. Filter by Shooting Team and Opponent
if view_mode == "Goals/Shots WE Scored":
    opponent_filtered_df = df[(df['opponent'] == selected_opponent) & (df['team_shooting'] == 'Binghamton Black Bears')]
    chart_title = f"Offensive Shots vs. {selected_opponent} (Scored by Black Bears)"
else:
    opponent_filtered_df = df[(df['opponent'] == selected_opponent) & (df['team_shooting'] == 'Opponent')]
    chart_title = f"Defensive Shots Allowed vs. {selected_opponent} (Scored on Black Bears)"

# 4. Player Filter (Applies when viewing Black Bears shots)
available_players = opponent_filtered_df['shooter'].unique()
selected_player = st.sidebar.multiselect(
    "Select Player(s):",
    options=available_players,
    default=available_players
)

filtered_df = opponent_filtered_df[opponent_filtered_df['shooter'].isin(selected_player)]

# Calculate Key Stats
total_shots = len(filtered_df)
total_goals = filtered_df['is_goal'].sum()
shooting_pct = (total_goals / total_shots * 100) if total_shots > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Shots", total_shots)
col2.metric("Total Goals", total_goals)
col3.metric("Shooting %", f"{shooting_pct:.1f}%")

# Create Full Rink Figure (200ft x 85ft, centered at 0,0)
fig, ax = plt.subplots(figsize=(12, 6))
ax.set_xlim(-100, 100)
ax.set_ylim(-42.5, 42.5)
ax.set_facecolor('#f4f4f4')

# 1. Rink Outer Border & Center Line
rink_border = patches.Rectangle((-100, -42.5), 200, 85, linewidth=2, edgecolor='black', facecolor='none')
ax.add_patch(rink_border)
ax.plot([0, 0], [-42.5, 42.5], color='red', linewidth=3) # Center Line

# 2. Blue Lines (-25 and +25)
ax.plot([-25, -25], [-42.5, 42.5], color='blue', linewidth=3)
ax.plot([25, 25], [-42.5, 42.5], color='blue', linewidth=3)

# 3. Goal Lines (-89 and +89)
ax.plot([-89, -89], [-42.5, 42.5], color='red', linewidth=1.5)
ax.plot([89, 89], [-42.5, 42.5], color='red', linewidth=1.5)

# 4. Goal Creases
crease_left = patches.Arc((-89, 0), width=12, height=12, angle=0, theta1=-90, theta2=90, color='blue', fill=False)
crease_right = patches.Arc((89, 0), width=12, height=12, angle=0, theta1=90, theta2=270, color='blue', fill=False)
ax.add_patch(crease_left)
ax.add_patch(crease_right)

# 5. Center Circle
center_circle = patches.Circle((0, 0), radius=15, color='blue', fill=False, linewidth=1.5)
ax.add_patch(center_circle)



# Plot Shots
saves = filtered_df[filtered_df['is_goal'] == 0]
goals = filtered_df[filtered_df['is_goal'] == 1]

# Set dot colors dynamically depending on mode
if view_mode == "Goals/Shots WE Scored":
    save_color, goal_color = 'gray', 'red'
else:
    save_color, goal_color = 'lightblue', 'darkred'

ax.scatter(saves['x_coord'], saves['y_coord'], c=save_color, alpha=0.6, label='Saved Shot', s=50)
ax.scatter(goals['x_coord'], goals['y_coord'], c=goal_color, alpha=0.9, label='Goal', s=120, marker='*')

ax.set_title(chart_title, fontsize=14, fontweight='bold')
ax.legend(loc='upper left')
ax.axis('off')

st.pyplot(fig)