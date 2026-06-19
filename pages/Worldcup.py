import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson

# Set page configurations
st.set_page_config(
    page_title="FIFA World Cup Time-Machine & Simulator",
    page_icon="⚽",
    layout="wide"
)

# Title and introduction
st.title("⚽ FIFA World Cup Time-Machine & Dream Match Simulator")
st.markdown("""
Welcome to the ultimate World Cup simulation engine. This application leverages historical match data from 1930 onwards 
to build a statistical prediction engine and interactive history tracker.
""")

# Load and clean data
@st.cache_data
def load_data():
    df = pd.read_csv("clean_fifa_worldcup_historical_data.csv")
    # Drop rows with missing match statistics (e.g., Sweden vs Austria 1938 walkover)
    df = df.dropna(subset=['home_goals', 'away_goals', 'total_goals'])
    df['year'] = df['year'].astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Could not find 'clean_fifa_worldcup_historical_data.csv'. Please make sure it's in the same directory.")
    st.stop()

# Get unique sorted team list
all_teams = sorted(list(set(df['home'].unique()) | set(df['away'].unique())))

# Global Tournament Baselines for smoothing
global_home_avg = df['home_goals'].mean()
global_away_avg = df['away_goals'].mean()

# --- Tabs setup ---
tab1, tab2, tab3 = st.tabs(["🔮 Dream Match Simulator", "⚔️ Historical Rivalry Tracker", "⏳ World Cup Era Explorer"])

# ==========================================
# TAB 1: DREAM MATCH SIMULATOR
# ==========================================
with tab1:
    st.header("🔮 Historical Dream Match Engine")
    st.markdown("What happens if two footballing giants go head-to-head? This engine uses a **Poisson Distribution** model built entirely on historical tournament scoring rates.")
    
    col1, col2 = st.columns(2)
    with col1:
        team_a = st.selectbox("Select Team A (Designated Home)", all_teams, index=all_teams.index("Brazil") if "Brazil" in all_teams else 0)
    with col2:
        team_b = st.selectbox("Select Team B (Designated Away)", all_teams, index=all_teams.index("Italy") if "Italy" in all_teams else 1)
        
    if team_a == team_b:
        st.warning("Please select two different countries to simulate a match.")
    else:
        # Calculate team stats for the simulation
        def get_team_stats(team):
            home_m = df[df['home'] == team]
            away_m = df[df['away'] == team]
            
            h_scored = home_m['home_goals'].mean() if len(home_m) > 0 else global_home_avg
            h_conceded = home_m['away_goals'].mean() if len(home_m) > 0 else global_away_avg
            a_scored = away_m['away_goals'].mean() if len(away_m) > 0 else global_away_avg
            a_conceded = away_m['home_goals'].mean() if len(away_m) > 0 else global_home_avg
            
            return h_scored, h_conceded, a_scored, a_conceded

        ta_h_scored, ta_h_conceded, _, _ = get_team_stats(team_a)
        _, _, tb_a_scored, tb_a_conceded = get_team_stats(team_b)
        
        # Expected lambda calculation (Average capability vs Opponent resistance)
        lambda_a = (ta_h_scored + tb_a_conceded) / 2
        lambda_b = (tb_a_scored + ta_h_conceded) / 2
        
        # Generate score probability matrix (up to 6 goals)
        max_goals = 6
        score_matrix = np.zeros((max_goals, max_goals))
        for i in range(max_goals):
            for j in range(max_goals):
                score_matrix[i, j] = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
        
        score_matrix /= score_matrix.sum()  # normalize
        
        # Calculate probabilities
        prob_a_win = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i > j)
        prob_b_win = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i < j)
        prob_draw = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i == j)
        
        # Display Key Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric(f"📈 {team_a} Win Probability", f"{prob_a_win:.1%}")
        m2.metric("🤝 Draw Probability", f"{prob_draw:.1%}")
        m3.metric(f"📉 {team_b} Win Probability", f"{prob_b_win:.1%}")
        
        # Matrix Plot
        st.subheader("📊 Match Scoreline Probability Heatmap")
        fig, ax = plt.subplots(figsize=(7, 5))
        sns.heatmap(score_matrix, annot=True, fmt=".1%", cmap="YlGnBu", 
                    xticklabels=range(max_goals), yticklabels=range(max_goals), ax=ax)
        ax.set_xlabel(f"Goals Scored by {team_b} (Away)")
        ax.set_ylabel(f"Goals Scored by {team_a} (Home)")
        ax.set_title("Most Likely Score Predictions")
        st.pyplot(fig)
        plt.close()
        
        # Live Match Simulation Feature
        st.subheader("🎲 Live Match Simulator Ticker")
        if st.button("🏁 Run Live Match Simulator!"):
            # Sample score based on probabilities
            flat_matrix = score_matrix.flatten()
            sampled_idx = np.random.choice(len(flat_matrix), p=flat_matrix)
            sim_a_goals = sampled_idx // max_goals
            sim_b_goals = sampled_idx % max_goals
            
            st.markdown("### 📻 Matchday Broadcast:")
            st.info(f"✨ **1'** - The referee blows the whistle! {team_a} and {team_b} face off under the stadium lights.")
            
            if sim_a_goals == 0 and sim_b_goals == 0:
                st.write(f"⏱️ **45'** - A tactical chess match. Both defenses are ironclad at halftime.")
                st.write(f"⏱️ **80'** - Desperate attempts from both squads, but accuracy is lacking today.")
            else:
                if sim_a_goals > 0:
                    st.write(f"⚽ **24'** - GOAL! {team_a} executes a flawless counter-attack to rock the stadium!")
                if sim_b_goals > 0:
                    st.write(f"⚽ **61'** - GOAL! {team_b} responds with a stunning long-range strike into the top corner!")
                if sim_a_goals > 1:
                    st.write(f"⚽ **78'** - GOAL! Incredible team play from {team_a} breaks open the defense again.")
                if sim_b_goals > 1:
                    st.write(f"⚽ **85'** - GOAL! {team_b} matches the intensity with a set-piece header!")
            
            st.success(f"🏁 **90' Full Time Summary**: **{team_a} {sim_a_goals} - {sim_b_goals} {team_b}**")


# ==========================================
# TAB 2: HISTORICAL RIVALRY TRACKER
# ==========================================
with tab2:
    st.header("⚔️ Head-to-Head Historical Rivalry Analyzer")
    st.markdown("Discover the authentic records of previous World Cup encounters between any two footballing countries.")
    
    col1_r, col2_r = st.columns(2)
    with col1_r:
        rival_a = st.selectbox("Select Country 1", all_teams, index=all_teams.index("Argentina") if "Argentina" in all_teams else 0)
    with col2_r:
        rival_b = st.selectbox("Select Country 2", all_teams, index=all_teams.index("Germany") if "Germany" in all_teams else 2)
        
    # Query direct encounters (either team can be home or away)
    h2h_df = df[((df['home'] == rival_a) & (df['away'] == rival_b)) | 
                ((df['home'] == rival_b) & (df['away'] == rival_a))].copy()
    
    if len(h2h_df) == 0:
        st.info(f"**{rival_a}** and **{rival_b}** have never met in an official FIFA World Cup match according to this dataset!")
    else:
        st.subheader(f"📊 Historical Summary ({len(h2h_df)} Meetings)")
        
        # Calculate records
        a_wins = len(h2h_df[(h2h_df['home'] == rival_a) & (h2h_df['home_goals'] > h2h_df['away_goals'])]) + \
                 len(h2h_df[(h2h_df['away'] == rival_a) & (h2h_df['away_goals'] > h2h_df['home_goals'])])
                 
        b_wins = len(h2h_df[(h2h_df['home'] == rival_b) & (h2h_df['home_goals'] > h2h_df['away_goals'])]) + \
                 len(h2h_df[(h2h_df['away'] == rival_b) & (h2h_df['away_goals'] > h2h_df['home_goals'])])
                 
        draws = len(h2h_df[h2h_df['home_goals'] == h2h_df['away_goals']])
        
        rc1, rc2, rc3 = st.columns(3)
        rc1.metric(f"🏆 {rival_a} Wins", a_wins)
        rc2.metric("🤝 Draws", draws)
        rc3.metric(f"🏆 {rival_b} Wins", b_wins)
        
        # Detailed game history table
        st.markdown("### 📋 Historic Match Log")
        display_h2h = h2h_df[['year', 'home', 'away', 'home_goals', 'away_goals', 'total_goals']].sort_values(by='year')
        st.dataframe(display_h2h.style.format({'home_goals': '{:.0f}', 'away_goals': '{:.0f}', 'total_goals': '{:.0f}'}), use_container_width=True)
        
        # Rivalry Timeline visualization
        fig2, ax2 = plt.subplots(figsize=(8, 3))
        colors = ['green' if row['home_goals'] == row['away_goals'] else ('blue' if row['home'] == rival_a and row['home_goals'] > row['away_goals'] else 'orange') for _, row in h2h_df.iterrows()]
        
        # Quick representation plot
        h2h_df = h2h_df.sort_values(by='year')
        ax2.scatter(h2h_df['year'], [1]*len(h2h_df), s=300, c='purple', alpha=0.6, edgecolors='black')
        for idx, row in h2h_df.iterrows():
            ax2.text(row['year'], 1.05, f"{int(row['home_goals'])} - {int(row['away_goals'])}", ha='center', fontweight='bold')
            ax2.text(row['year'], 0.93, f"{row['home']}\nvs\n{row['away']}", ha='center', fontsize=8)
            
        ax2.set_xlim(df['year'].min() - 4, df['year'].max() + 4)
        ax2.get_yaxis().set_visible(False)
        ax2.set_title("Timeline of World Cup Collisions")
        st.pyplot(fig2)
        plt.close()


# ==========================================
# TAB 3: WORLD CUP ERA EXPLORER
# ==========================================
with tab3:
    st.header("⏳ Historical World Cup Era Dashboard")
    st.markdown("See how tournament rules, playstyles, and goal scoring changed over nearly a century of football history.")
    
    # Calculate trends per year
    yearly_stats = df.groupby('year').agg(
        total_matches=('total_goals', 'count'),
        avg_goals=('total_goals', 'mean'),
        avg_home_goals=('home_goals', 'mean'),
        avg_away_goals=('away_goals', 'mean')
    ).reset_index()
    
    # Plot 1: Goal Trends Over Time
    st.subheader("📈 Trend of Average Goals Scored Per Match By Era")
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    ax3.plot(yearly_stats['year'], yearly_stats['avg_goals'], marker='o', color='crimson', linewidth=2.5, label='Total Expected Goals')
    ax3.bar(yearly_stats['year'], yearly_stats['avg_home_goals'], alpha=0.4, label='Home Team Goals', color='blue
