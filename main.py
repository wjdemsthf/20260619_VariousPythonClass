import streamlit as st

# 1. 페이지 설정 및 진한 톤(Dark Theme) 배경 스타일 커스텀
st.set_page_config(page_title="포켓몬 스플렌더", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #121214;
        color: #E2E8F0;
    }
    div[data-testid="stMetric"] {
        background-color: #1A1D24;
        border: 1px solid #2D3748;
        padding: 10px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #2D3748;
        color: white;
        border: 1px solid #4A5568;
    }
    .stButton>button:hover {
        background-color: #4A5568;
        color: #F7FAFC;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔴 포켓몬 스플렌더 (Pokémon Splendor)")
st.caption("공식 몬스터볼을 모으고 포켓몬의 진화 보너스를 얻어 최고의 마스터가 되세요!")

# 2. 게임 데이터 및 세션 상태 초기화
BALL_TYPES = ["몬스터볼", "수퍼볼", "하이퍼볼", "사파리볼", "다이브볼", "마스터볼"]

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.num_players = 2
    st.session_state.current_turn = 0
    st.session_state.game_started = False
    
    # 공용 시장 공급처 (사파리/다이브 포함 6종)
    st.session_state.market_balls = {
        "몬스터볼": 7, "수퍼볼": 7, "하이퍼볼": 7, "사파리볼": 7, "다이브볼": 7, "마스터볼": 5
    }
    
    # 포켓몬 카드 데이터 (비용, 잡았을 때 주는 무한 보너스 볼, 승점)
    st.session_state.pokemon_market = [
        {"name": "구구", "cost": {"몬스터볼": 2, "수퍼볼": 1}, "bonus": "몬스터볼", "points": 0},
        {"name": "꼬부기", "cost": {"수퍼볼": 3}, "bonus": "다이브볼", "points": 1},
        {"name": "피카츄", "cost": {"몬스터볼": 1, "하이퍼볼": 2}, "bonus": "수퍼볼", "points": 1},
        {"name": "리자드", "cost": {"몬스터볼": 3, "사파리볼": 2}, "bonus": "하이퍼볼", "points": 2},
        {"name": "스라크", "cost": {"사파리볼": 4}, "bonus": "사파리볼", "points": 2},
        {"name": "라프라스", "cost": {"다이브볼": 4, "하이퍼볼": 1}, "bonus": "다이브볼", "points": 3},
        {"name": "망나뇽", "cost": {"하이퍼볼": 3, "사파리볼": 3, "다이브볼": 2}, "bonus": "마스터볼", "points": 4},
        {"name": "뮤츠", "cost": {"몬스터볼": 4, "수퍼볼": 4, "하이퍼볼": 4}, "bonus": "마스터볼", "points": 5},
    ]
    st.session_state.players = {}
    st.session_state.log = ["인원수를 선택하고 게임을 시작해주세요!"]

# --- 게임 시작 전 설정 화면 ---
if not st.session_state.game_started:
    st.subheader("👥 대결 설정")
    player_count = st.radio("플레이어 수를 선택하세요", [2, 3, 4], index=0, horizontal=True)
    
    if st.button("🎮 게임 시작"):
        st.session_state.num_players = player_count
        st.session_state.players = {
            f"Player {i+1}": {
                "balls": {b: 0 for b in BALL_TYPES},
                "bonuses": {b: 0 for b in BALL_TYPES},  # 내가 보유한 보너스 개수
                "score": 0,
                "captured": []
            } for i in range(player_count)
        }
        st.session_state.game_started = True
        st.session_state.log = ["게임을 시작했습니다! 1P의 차례입니다."]
        st.rerun()
    st.stop()

# --- 게임 플레이 화면 ---
current_player_id = f"Player {st.session_state.current_turn + 1}"
p_data = st.session_state.players[current_player_id]

# 상단: 턴 표시 및 로그
st.subheader(f"⚡ 현재 차례: ⭐ {current_player_id} ⭐")

col_left, col_right = st.columns([1, 2])

# 왼쪽: 플레이어 현황 대시보드
with col_left:
    st.header("📋 트레이너 상황판")
    
    for p_id, data in st.session_state.players.items():
        is_current = "▶️ " if p_id == current_player_id else ""
        with st.expander(f"{is_current}{p_id} (승점: {data['score']}점)", expanded=(p_id == current_player_id)):
            st.markdown("**보유한 몬스터볼 (일회성 소비용)**")
            b_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                b_cols[idx % 3].metric(b_name, f"{data['balls'][b_name]}개")
                
            st.markdown("**✨ 획득한 보너스 (영구 할인 아이콘)**")
            bonus_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                bonus_cols[idx % 3].metric(f"💎 {b_name}", f"+{data['bonuses'][b_name]}")
                
            st.caption(f"포획한 포켓몬: {', '.join(data['captured']) if data['captured'] else '없음'}")

# 오른쪽: 필드 및 액션 (시장)
with col_right:
    st.header("🌐 중앙 필드")
    
    # Action 1: 볼 수집하기
    st.subheader("🔴 몬스터볼 보급소 (종류별로 1개씩 최대 2종류까지 수집 가능)")
    st.caption("※ 간단한 규칙 적용: 클릭 시 필드에서 내 가방으로 1개 즉시 이동합니다.")
    
    take_cols = st.columns(3)
    for idx, (b_name, stock) in enumerate(st.session_state.market_balls.items()):
        with take_cols[idx % 3]:
            st.markdown(f"**{b_name}** (필드 남음: `{stock}`개)")
            if stock > 0:
                if st.button(f"{b_name} 1개 가져오기", key=f"take_{b_name}"):
                    st.session_state.market_balls[b_name] -= 1
                    p_data["balls"][b_name] += 1
                    st.session_state.log.insert(0, f"💬 {current_player_id}님이 {b_name}을(를) 1개 가져갔습니다.")
                    
                    # 턴 넘기기
                    st.session_state.current_turn = (st.session_state.current_turn + 1) % st.session_state.num_players
                    st.rerun()

    st.write("---")
    
    # Action 2: 포켓몬 포획하기
    st.subheader("🐉 야생 포켓몬 등장 (보너스 할인 자동 계산)")
    
    grid_cols = st.columns(2)
    for idx, poke in enumerate(st.session_state.pokemon_market):
        with grid_cols[idx % 2]:
            st.markdown(f"### **{poke['name']}**")
            st.markdown(f"🏆 승점: **{poke['points']}점** | ✨ 잡을 시 영구 보너스: `{poke['bonus']}`")
            
            # 비용 및 할인액 계산 표시
            cost_details = []
            can_afford = True
            
            for b_type, req_amount in poke['cost'].items():
                my_bonus = p_data["bonuses"].get(b_type, 0)
                actual_cost = max(0, req_amount - my_bonus)  # 보너스로 할인된 실제 가격
                my_ball = p_data["balls"].get(b_type, 0)
                
                cost_details.append(f"- {b_type}: 필요 {req_amount} (할인되어 실요구: **{actual_cost}**, 내 보유: {my_ball})")
                
                if my_ball < actual_cost:
                    can_afford = False
            
            st.markdown("\n".join(cost_details))
            
            # 포획 버튼 활성화 조건
            if st.button(f"⚽ {poke['name']} 포획하기", key=f"buy_{poke['name']}_{idx}", disabled=not can_afford):
                # 자원 지불 처리 (보너스 적용 후 차액만 차감)
                for b_type, req_amount in poke['cost'].items():
                    my_bonus = p_data["bonuses"].get(b_type, 0)
                    actual_cost = max(0, req_amount - my_bonus)
                    p_data["balls"][b_type] -= actual_cost
                    st.session_state.market_balls[b_type] += actual_cost  # 공용 시장으로 반납
                
                # 보상 지급
                p_data["score"] += poke['points']
                p_data["captured"].append(poke['name'])
                p_data["bonuses"][poke['bonus']] += 1  # 보너스 볼 누적 증가!
                
                st.session_state.log.insert(0, f"🎉 {current_player_id}님이 {poke['name']}를 포획했습니다! {poke['bonus']} 보너스 획득!")
                
                # 상점에서 잡힌 포켓몬 제거
                st.session_state.pokemon_market.pop(idx)
                
                # 턴 넘기기
                st.session_state.current_turn = (st.session_state.current_turn + 1) % st.session_state.num_players
                st.rerun()

# 하단: 로그 관리 및 시스템 리셋
st.write("---")
st.subheader("📜 배틀 로그 (최근 행동 5개)")
for l in st.session_state.log[:5]:
    st.text(l)

if st.button("🔄 게임 완전히 초기화"):
    st.session_state.clear()
    st.rerun()
