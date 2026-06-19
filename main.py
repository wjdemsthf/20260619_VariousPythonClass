import streamlit as st

# 1. 페이지 설정 및 진한 톤(Dark Theme) 스타일
st.set_page_config(page_title="포켓몬 스플렌더 프리미엄", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #111216; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #1A1D24; border: 1px solid #2D3748; padding: 12px; border-radius: 10px; }
    .stButton>button { background-color: #2D3748; color: white; border: 1px solid #4A5568; width: 100%; }
    .stButton>button:hover { background-color: #4A5568; color: #F7FAFC; }
    .highlight-box { background-color: #1E222B; border-left: 5px solid #E53E3E; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ 포켓몬 스플렌더: 에볼루션 (Pokémon Splendor: Evolution)")
st.caption("볼 수집, 포획, 그리고 '진화' 시스템이 탑재된 2~4인용 정통 스플렌더 웹앱입니다.")

# 2. 게임 상수 및 데이터 정의
BALL_TYPES = ["몬스터볼", "수퍼볼", "하이퍼볼", "사파리볼", "다이브볼", "마스터볼"]

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.game_started = False
    st.session_state.num_players = 2
    st.session_state.current_turn = 0
    
    # 턴 내부 단계 관리 (0: 볼 수집 단계, 1: 구매 단계, 2: 진화 단계)
    st.session_state.turn_phase = 0 
    st.session_state.selected_balls = []  # 이번 턴에 고른 볼 임시 저장
    
    # 공용 필드 볼 공급처
    st.session_state.market_balls = {b: 7 for b in BALL_TYPES if b != "마스터볼"}
    st.session
