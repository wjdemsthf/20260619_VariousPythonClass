import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="월드컵 시대 탐험", page_icon="⏳", layout="wide")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "clean_fifa_worldcup_historical_data.csv")
    df = pd.read_csv(file_path)
    df = df.dropna(subset=['home_goals', 'away_goals', 'total_goals'])
    df['year'] = df['year'].astype(int)
    return df

df = load_data()

st.header("⏳ 월드컵 시대별 통계 분석")
st.markdown("축구 전술의 변화와 시대의 흐름에 따라 경기당 평균 골 수가 어떻게 변화했는지 확인하세요.")

yearly_stats = df.groupby('year').agg(
    avg_goals=('total_goals', 'mean'),
    total_matches=('total_goals', 'count')
).reset_index()

st.subheader("📈 연도별 경기당 평균 득점 추이")
st.line_chart(data=yearly_stats, x='year', y='avg_goals', use_container_width=True)

st.subheader("🏅 역사상 가장 많은 골이 터진 매치 TOP 5")
top_scoring = df.sort_values(by='total_goals', ascending=False).head(5)
st.dataframe(top_scoring[['year', 'home', 'away', 'home_goals', 'away_goals', 'total_goals']], use_container_width=True, hide_index=True)
