import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="역사적 라이벌 분석기", page_icon="⚔️", layout="wide")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "clean_fifa_worldcup_historical_data.csv")
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['home_goals', 'away_goals', 'total_goals'])
    df['year'] = df['year'].astype(int)
    return df

df = load_data()
all_teams = sorted(list(set(df['home'].unique()) | set(df['away'].unique())))

st.header("⚔️ 헤드 투 헤드(H2H) 역사적 라이벌 분석기")

col1, col2 = st.columns(2)
with col1:
    rival_a = st.selectbox("국가 1 선택", all_teams, index=all_teams.index("Argentina") if "Argentina" in all_teams else 0)
with col2:
    rival_b = st.selectbox("국가 2 선택", all_teams, index=all_teams.index("Germany") if "Germany" in all_teams else 1)

h2h_df = df[((df['home'] == rival_a) & (df['away'] == rival_b)) | 
            ((df['home'] == rival_b) & (df['away'] == rival_a))].copy()

if len(h2h_df) == 0:
    st.info(f"ℹ️ **{rival_a}**와 **{rival_b}**는 역대 월드컵 본선 무대에서 맞붙은 적이 없습니다.")
else:
    st.subheader(f"📊 총 {len(h2h_df)}번의 역사적 맞대결 기록")
    
    a_wins = len(h2h_df[(h2h_df['home'] == rival_a) & (h2h_df['home_goals'] > h2h_df['away_goals'])]) + \
             len(h2h_df[(h2h_df['away'] == rival_a) & (h2h_df['away_goals'] > h2h_df['home_goals'])])
    b_wins = len(h2h_df[(h2h_df['home'] == rival_b) & (h2h_df['home_goals'] > h2h_df['away_goals'])]) + \
             len(h2h_df[(h2h_df['away'] == rival_b) & (h2h_df['away_goals'] > h2h_df['home_goals'])])
    draws = len(h2h_df[h2h_df['home_goals'] == h2h_df['away_goals']])
    
    rc1, rc2, rc3 = st.columns(3)
    rc1.metric(f"🏆 {rival_a} 승리", f"{a_wins}회")
    rc2.metric("🤝 무승부", f"{draws}회")
    rc3.metric(f"🏆 {rival_b} 승리", f"{b_wins}회")
    
    st.markdown("### 📋 역대 매치 로그")
    st.dataframe(h2h_df[['year', 'home', 'away', 'home_goals', 'away_goals', 'total_goals']].sort_values(by='year'), use_container_width=True, hide_index=True)
