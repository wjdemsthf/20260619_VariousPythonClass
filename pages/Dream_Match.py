import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import poisson
import os

st.set_page_config(page_title="드림 매치 시뮬레이터", page_icon="🔮", layout="wide")

# 안전한 상위 디렉토리 데이터 로드 방식
@st.cache_data
def load_data():
    # 현재 파일(pages/...)의 절대 경로 기준 상위 디렉토리 파일 지정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "clean_fifa_worldcup_historical_data.csv")
    
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['home_goals', 'away_goals', 'total_goals'])
    df['year'] = df['year'].astype(int)
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("상위 디렉토리에서 'clean_fifa_worldcup_historical_data.csv' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
    st.stop()

all_teams = sorted(list(set(df['home'].unique()) | set(df['away'].unique())))
global_home_avg = df['home_goals'].mean()
global_away_avg = df['away_goals'].mean()

st.header("🔮 역사적 드림 매치 엔진")
st.markdown("과거 득점 데이터를 기반으로 한 **포아송 분포** 모델이 두 팀의 예상 스코어를 계산합니다.")

col1, col2 = st.columns(2)
with col1:
    team_a = st.selectbox("홈 팀 선택", all_teams, index=all_teams.index("Brazil") if "Brazil" in all_teams else 0)
with col2:
    team_b = st.selectbox("어웨이 팀 선택", all_teams, index=all_teams.index("Italy") if "Italy" in all_teams else 1)
    
if team_a == team_b:
    st.warning("서로 다른 두 국가를 선택해주세요.")
else:
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
    
    lambda_a = (ta_h_scored + tb_a_conceded) / 2
    lambda_b = (tb_a_scored + ta_h_conceded) / 2
    
    max_goals = 6
    score_matrix = np.zeros((max_goals, max_goals))
    for i in range(max_goals):
        for j in range(max_goals):
            score_matrix[i, j] = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
    score_matrix /= score_matrix.sum()
    
    prob_a_win = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i > j)
    prob_b_win = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i < j)
    prob_draw = sum(score_matrix[i, j] for i in range(max_goals) for j in range(max_goals) if i == j)
    
    m1, m2, m3 = st.columns(3)
    m1.metric(f"📈 {team_a} 승리 확률", f"{prob_a_win:.1%}")
    m2.metric("🤝 무승부 확률", f"{prob_draw:.1%}")
    m3.metric(f"📉 {team_b} 승리 확률", f"{prob_b_win:.1%}")
    
    st.subheader("📊 스코어 확률 히트맵")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(score_matrix, annot=True, fmt=".1%", cmap="YlGnBu", xticklabels=range(max_goals), yticklabels=range(max_goals), ax=ax)
    ax.set_xlabel(f"{team_b} 득점 수")
    ax.set_ylabel(f"{team_a} 득점 수")
    st.pyplot(fig)
    plt.close()
    
    st.subheader("🎲 실시간 매치 시뮬레이터")
    if st.button("🏁 시뮬레이션 시작!"):
        flat_matrix = score_matrix.flatten()
        sampled_idx = np.random.choice(len(flat_matrix), p=flat_matrix)
        sim_a_goals = sampled_idx // max_goals
        sim_b_goals = sampled_idx % max_goals
        
        st.markdown("### 📻 중계 방송:")
        st.info(f"✨ **1'** - 경기 시작! {team_a}와 {team_b}의 맞대결이 시작됩니다.")
        
        if sim_a_goals > 0:
            st.write(f"⚽ **{np.random.randint(10, 45)}'** - GOAL! {team_a}의 환상적인 선제골이 터집니다!")
        if sim_b_goals > 0:
            st.write(f"⚽ **{np.random.randint(46, 85)}'** - GOAL! {team_b}가 날카로운 추격골을 성공시킵니다!")
        if sim_a_goals > 1:
            st.write(f"⚽ **88'** - GOAL! {team_a}가 쐐기골을 기록하며 승기를 굳힙니다!")
            
        st.success(f"🏁 **경기 종료**: **{team_a} {sim_a_goals} - {sim_b_goals} {team_b}**")
