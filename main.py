import streamlit as st
import random

# 1. 페이지 설정 및 진한 톤(Dark Theme) 스타일
st.set_page_config(page_title="포켓몬 스플렌더: 에볼루션 삼단계", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #111216; color: #E2E8F0; }
    div[data-testid="stMetric"] { background-color: #1A1D24; border: 1px solid #2D3748; padding: 12px; border-radius: 10px; }
    .stButton>button { background-color: #2D3748; color: white; border: 1px solid #4A5568; width: 100%; }
    .stButton>button:hover { background-color: #4A5568; color: #F7FAFC; }
    .highlight-box { background-color: #1E222B; border-left: 5px solid #E53E3E; padding: 15px; border-radius: 5px; margin-bottom: 15px; }
    .evo-box { background-color: #1A1C23; border: 1px dashed #4A5568; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚽ 포켓몬 스플렌더: 3단 대진화 (Pokémon Splendor: 3-Stage Evolution)")

BALL_TYPES = ["몬스터볼", "수퍼볼", "하이퍼볼", "사파리볼", "다이브볼", "마스터볼"]

# 2. 단계별로 가격 격차를 둔 포켓몬 덱 구성
TOTAL_POKEMON_DECK = {
    # 1단계: 기본형 (총 비용 볼 3~4개 수준 / 승점 0~1점)
    1: [
        {"id": 1, "name": "파이리", "cost": {"몬스터볼": 3}, "bonus": "몬스터볼", "points": 0, "stage": 1},
        {"id": 2, "name": "꼬부기", "cost": {"수퍼볼": 3}, "bonus": "다이브볼", "points": 0, "stage": 1},
        {"id": 3, "name": "이상해씨", "cost": {"하이퍼볼": 3}, "bonus": "사파리볼", "points": 0, "stage": 1},
        {"id": 4, "name": "피츄", "cost": {"사파리볼": 4}, "bonus": "수퍼볼", "points": 1, "stage": 1},
        {"id": 5, "name": "미뇽", "cost": {"다이브볼": 4}, "bonus": "하이퍼볼", "points": 1, "stage": 1},
    ],
    # 2단계: 1차 진화형 (총 비용 볼 5~6개 수준 / 승점 2~3점)
    2: [
        {"id": 11, "name": "리자드", "from": "파이리", "cost": {"몬스터볼": 3, "하이퍼볼": 2}, "bonus": "몬스터볼", "points": 2, "stage": 2},
        {"id": 12, "name": "어니부기", "from": "꼬부기", "cost": {"수퍼볼": 3, "다이브볼": 2}, "bonus": "다이브볼", "points": 2, "stage": 2},
        {"id": 13, "name": "이상해풀", "from": "이상해씨", "cost": {"하이퍼볼": 3, "사파리볼": 3}, "bonus": "사파리볼", "points": 3, "stage": 2},
        {"id": 14, "name": "피카츄", "from": "피츄", "cost": {"사파리볼": 2, "수퍼볼": 3}, "bonus": "수퍼볼", "points": 2, "stage": 2},
        {"id": 15, "name": "신뇽", "from": "미뇽", "cost": {"다이브볼": 3, "하이퍼볼": 3}, "bonus": "하이퍼볼", "points": 3, "stage": 2},
    ],
    # 3단계: 최종 진화형 (총 비용 볼 7~9개 수준의 고가 / 승점 5~6점 배치)
    3: [
        {"id": 21, "name": "리자몽", "from": "리자드", "cost": {"몬스터볼": 4, "수퍼볼": 2, "하이퍼볼": 3}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 22, "name": "거북왕", "from": "어니부기", "cost": {"수퍼볼": 4, "다이브볼": 4}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 23, "name": "이상해꽃", "from": "이상해풀", "cost": {"하이퍼볼": 5, "사파리볼": 3}, "bonus": "마스터볼", "points": 6, "stage": 3},
        {"id": 24, "name": "라이츄", "from": "피카츄", "cost": {"수퍼볼": 4, "사파리볼": 4}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 25, "name": "망나뇽", "from": "신뇽", "cost": {"하이퍼볼": 3, "사파리볼": 3, "다이브볼": 3}, "bonus": "마스터볼", "points": 6, "stage": 3},
    ]
}

# 세션 상태 초기화
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.game_started = False
    st.session_state.current_turn = 0
    st.session_state.turn_phase = 0
    st.session_state.selected_balls = []
    
    # 공용 시장 풀 자원 공급 (고가 카드 거래 활성화를 위해 마스터볼 공급 증가)
    st.session_state.market_balls = {b: 7 for b in BALL_TYPES if b != "마스터볼"}
    st.session_state.market_balls["마스터볼"] = 5
    
    st.session_state.decks = {
        1: list(TOTAL_POKEMON_DECK[1]),
        2: list(TOTAL_POKEMON_DECK[2]),
        3: list(TOTAL_POKEMON_DECK[3])
    }
    for stage in [1, 2, 3]:
        random.shuffle(st.session_state.decks[stage])
        
    # 각 슬롯당 3개씩 선배치
    st.session_state.field_market = {
        1: [st.session_state.decks[1].pop() for _ in range(3) if st.session_state.decks[1]],
        2: [st.session_state.decks[2].pop() for _ in range(3) if st.session_state.decks[2]],
        3: [st.session_state.decks[3].pop() for _ in range(3) if st.session_state.decks[3]],
    }
    
    st.session_state.players = {}
    st.session_state.log = []

if "turn_phase" not in st.session_state: st.session_state.turn_phase = 0
if "selected_balls" not in st.session_state: st.session_state.selected_balls = []

def next_phase():
    st.session_state.turn_phase += 1
    if st.session_state.turn_phase > 2:
        curr_p = f"Player {st.session_state.current_turn + 1}"
        total_balls = sum(st.session_state.players[curr_p]["balls"].values())
        if total_balls > 8:
            over_count = total_balls - 8
            for b in BALL_TYPES:
                while st.session_state.players[curr_p]["balls"][b] > 0 and over_count > 0:
                    st.session_state.players[curr_p]["balls"][b] -= 1
                    st.session_state.market_balls[b] += 1
                    over_count -= 1
            st.session_state.log.insert(0, f"⚠️ {curr_p}님의 볼 보유량이 8개를 초과하여 자동 반납되었습니다.")
            
        st.session_state.turn_phase = 0
        st.session_state.selected_balls = []
        st.session_state.current_turn = (st.session_state.current_turn + 1) % st.session_state.num_players
    st.rerun()

def refill_market(stage, index):
    if st.session_state.decks[stage]:
        new_card = st.session_state.decks[stage].pop()
        st.session_state.field_market[stage][index] = new_card
    else:
        st.session_state.field_market[stage].pop(index)

# --- 방 입장 설정 ---
if not st.session_state.get("game_started", False):
    st.subheader("👥 트레이너 대결 인원 선택")
    player_count = st.radio("플레이어 수", [2, 3, 4], index=0, horizontal=True)
    if st.button("🎮 대진 시작"):
        st.session_state.num_players = player_count
        st.session_state.players = {
            f"Player {i+1}": {
                "balls": {b: 0 for b in BALL_TYPES},
                "bonuses": {b: 0 for b in BALL_TYPES},
                "score": 0,
                "captured": []
            } for i in range(player_count)
        }
        st.session_state.game_started = True
        st.session_state.log = ["🔴 3단계 밸런스 매치 리그가 구동되었습니다! 1P 차례입니다."]
        st.rerun()
    st.stop()

current_player_id = f"Player {st.session_state.current_turn + 1}"
p_data = st.session_state.players[current_player_id]
phases = ["🟢 1단계: 볼 수집 하기", "🔵 2단계: 야생 포켓몬 포획 (1단계 포켓몬)", "🟣 3단계: 포켓몬 진화 연구 (2단계 & 3단계 진화)"]

col_left, col_right = st.columns([1, 2])

# 상황판 대시보드
with col_left:
    st.header("📋 트레이너 상황판")
    for p_id, data in st.session_state.players.items():
        is_curr = "▶️ " if p_id == current_player_id else ""
        with st.expander(f"{is_curr}{p_id} ({data['score']} 점)", expanded=(p_id == current_player_id)):
            st.caption(f"🎒 가방 자원량: {sum(data['balls'].values())} / 8 개")
            b_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                b_cols[idx % 3].metric(b_name, f"{data['balls'][b_name]}개")
            st.markdown("**💎 획득한 영구 할인 보너스**")
            bonus_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                bonus_cols[idx % 3].metric(b_name[:3], f"+{data['bonuses'][b_name]}")
            st.markdown(f"**🐾 소유 포켓몬:** {', '.join(data['captured']) if data['captured'] else '없음'}")

# 메인 시스템 조작 구역
with col_right:
    current_phase_idx = st.session_state.get("turn_phase", 0)
    st.markdown(f"<div class='highlight-box'><h3>{phases[current_phase_idx]}</h3>"
                f"현재 차례 트레이너: <b>{current_player_id}</b></div>", unsafe_allow_html=True)
    
    # ----------------------------------------
    # [PHASE 0] 자원 보급 단계
    # ----------------------------------------
    if current_phase_idx == 0:
        st.subheader("🔴 볼 선택지 및 필드 현황")
        selected = st.session_state.selected_balls
        st.info(f"선택 바구니 상황: {', '.join(selected) if selected else '비어 있음'}")
        
        has_two_same = len(selected) == 2 and selected[0] == selected[1]
        has_master = p_data["balls"]["마스터볼"] > 0
        
        grid_b = st.columns(3)
        for idx, b_name in enumerate(BALL_TYPES):
            stock = st.session_state.market_balls[b_name]
            with grid_b[idx % 3]:
                st.markdown(f"**{b_name}** (필드 남음: {stock}개)")
                
                btn_disabled = False
                if stock <= 0: btn_disabled = True
                if has_two_same: btn_disabled = True
                if b_name == "마스터볼" and (has_master or len(selected) > 0): btn_disabled = True
                if len(selected) >= 3: btn_disabled = True
                if b_name in selected and len(selected) == 1 and stock < 4: btn_disabled = True
                if b_name in selected and len(selected) >= 2: btn_disabled = True
                
                if st.button("선택", key=f"sel_{b_name}_{idx}", disabled=btn_disabled):
                    st.session_state.selected_balls.append(b_name)
                    st.rerun()
                    
        st.write("---")
        b_actions = st.columns(3)
        if b_actions[0].button("✔️ 다른 종류 3개 수령", disabled=not (len(set(selected)) == 3 and "마스터볼" not in selected)):
            for b in selected: st.session_state.market_balls[b] -= 1; p_data["balls"][b] += 1
            st.session_state.log.insert(0, f"🔹 {current_player_id}님이 서로 다른 볼 3개를 공급받았습니다.")
            next_phase()
            
        if len(selected) == 1 and "마스터볼" not in selected:
            t_ball = selected[0]
            if b_actions[1].button(f"✔️ {t_ball} 2개 묶음 수령", disabled=(st.session_state.market_balls[t_ball] < 4)):
                st.session_state.market_balls[t_ball] -= 2; p_data["balls"][t_ball] += 2
                st.session_state.log.insert(0, f"🔹 {current_player_id}님이 {t_ball} 2개를 가져왔습니다.")
                next_phase()
                
        if b_actions[2].button("👑 마스터볼 독점 수령", disabled=not (len(selected) == 1 and selected[0] == "마스터볼")):
            st.session_state.market_balls["마스터볼"] -= 1; p_data["balls"]["마스터볼"] += 1
            st.session_state.log.insert(0, f"👑 {current_player_id}님이 마스터볼 1개를 확보했습니다.")
            next_phase()
            
        if st.button("볼 보급 스킵하기 ➡️"): next_phase()

    # ----------------------------------------
    # [PHASE 1] 야생 포켓몬 포획 (저가 단계)
    # ----------------------------------------
    elif current_phase_idx == 1:
        st.subheader(f"🛒 야생 필드 포켓몬 [1단계] (남은 더미: {len(st.session_state.decks[1])}장)")
        
        grid_p = st.columns(3)
        for idx, poke in enumerate(st.session_state.field_market[1]):
            with grid_p[idx]:
                st.markdown(f"### **{poke['name']}**")
                st.markdown(f"🏆 승점: **{poke['points']}점** | 💎 할인: `{poke['bonus']}`")
                
                shortage = 0
                cost_text = []
                for b_type, req in poke['cost'].items():
                    discount = p_data["bonuses"].get(b_type, 0)
                    needed = max(0, req - discount)
                    holding = p_data["balls"].get(b_type, 0)
                    if holding < needed: shortage += (needed - holding)
                    cost_text.append(f"- {b_type}: 필요 {req} (실제 {needed}/보유 {holding})")
                
                st.markdown("\n".join(cost_text))
                can_buy = p_data["balls"]["마스터볼"] >= shortage
                
                if st.button(f"⚽ {poke['name']} 포획", key=f"buy_p1_{poke['id']}", disabled=not can_buy):
                    p_data["balls"]["마스터볼"] -= shortage
                    st.session_state.market_balls["마스터볼"] += shortage
                    for b_type, req in poke['cost'].items():
                        discount = p_data["bonuses"].get(b_type, 0)
                        needed = max(0, req - discount)
                        holding = p_data["balls"].get(b_type, 0)
                        if holding >= needed:
                            p_data["balls"][b_type] -= needed; st.session_state.market_balls[b_type] += needed
                        else:
                            p_data["balls"][b_type] = 0; st.session_state.market_balls[b_type] += holding
                            
                    p_data["score"] += poke["points"]
                    p_data["captured"].append(poke["name"])
                    p_data["bonuses"][poke["bonus"]] += 1
                    st.session_state.log.insert(0, f"🎉 {current_player_id}님이 야생의 {poke['name']}를 포획했습니다.")
                    
                    refill_market(1, idx)
                    next_phase()
                    
        st.write("---")
        if st.button("포획 단계 스킵하기 ➡️"): next_phase()

    # ----------------------------------------
    # [PHASE 2] 진화 설계 연구소 (중~고가형 단계 통합 배치)
    # ----------------------------------------
    elif current_phase_idx == 2:
        st.subheader("🧬 포켓몬 대진화 센터 (단계별 비용 격차 패치 완료)")
        
        # [2단계 필드 시각화]
        st.markdown(f"#### 🔼 2단계 진화 리스트 (중간 가격대 | 더미 잔여: {len(st.session_state.decks[2])}장)")
        grid_e2 = st.columns(3)
        for idx, evo2 in enumerate(st.session_state.field_market[2]):
            with grid_e2[idx]:
                st.markdown(f"<div class='evo-box'>🧪 <b>{evo2['from']}</b> ➔ <span style='color:#4299E1; font-weight:bold;'>{evo2['name']}</span><br>⭐ 승점: {evo2['points']}점 | 할인: {evo2['bonus']}</div>", unsafe_allow_html=True)
                
                shortage = 0
                cost_text = []
                for b_type, req in evo2['cost'].items():
                    discount = p_data["bonuses"].get(b_type, 0)
                    needed = max(0, req - discount)
                    holding = p_data["balls"].get(b_type, 0)
                    if holding < needed: shortage += (needed - holding)
                    cost_text.append(f"• {b_type}: {req}개 필요 (내 보유: {holding}개)")
                st.markdown("\n".join(cost_text))
                
                has_origin = evo2["from"] in p_data["captured"]
                can_evo = has_origin and (p_data["balls"]["마스터볼"] >= shortage)
                
                if st.button(f"⚡ {evo2['name']} 진화시행", key=f"evo2_{evo2['id']}", disabled=not can_evo):
                    p_data["balls"]["마스터볼"] -= shortage; st.session_state.market_balls["마스터볼"] += shortage
                    for b_type, req in evo2['cost'].items():
                        discount = p_data["bonuses"].get(b_type, 0)
                        needed = max(0, req - discount)
                        holding = p_data["balls"].get(b_type, 0)
                        if holding >= needed: p_data["balls"][b_type] -= needed; st.session_state.market_balls[b_type] += needed
                        else: p_data["balls"][b_type] = 0; st.session_state.market_balls[b_type] += holding
                    
                    p_data["captured"].remove(evo2["from"])
                    p_data["captured"].append(evo2["name"])
                    p_data["score"] += evo2["points"]
                    p_data["bonuses"][evo2["bonus"]] += 1
                    st.session_state.log.insert(0, f"🔥 {current_player_id}님이 {evo2['from']}를 {evo2['name']}(으)로 진화시켰습니다.")
                    refill_market(2, idx)
                    next_phase()
                    
        st.write("---")
        
        # [3단계 필드 시각화]
        st.markdown(f"#### 👑 3단계 최종 진화 리스트 (최고 최고가형 | 더미 잔여: {len(st.session_state.decks[3])}장)")
        grid_e3 = st.columns(3)
        for idx, evo3 in enumerate(st.session_state.field_market[3]):
            with grid_e3[idx]:
                st.markdown(f"<div class='evo-box'>🌟 <b>{evo3['from']}</b> ➔ <span style='color:#ED64A6; font-weight:bold;'>{evo3['name']}</span><br>⭐ 승점: {evo3['points']}점 | 보너스: {evo3['bonus']}</div>", unsafe_allow_html=True)
                
                shortage = 0
                cost_text = []
                for b_type, req in evo3['cost'].items():
                    discount = p_data["bonuses"].get(b_type, 0)
                    needed = max(0, req - discount)
                    holding = p_data["balls"].get(b_type, 0)
                    if holding < needed: shortage += (needed - holding)
                    cost_text.append(f"• {b_type}: {req}개 필요 (내 보유: {holding}개)")
                st.markdown("\n".join(cost_text))
                
                has_origin = evo3["from"] in p_data["captured"]
                can_evo3 = has_origin and (p_data["balls"]["마스터볼"] >= shortage)
                
                if st.button(f"👑 {evo3['name']} 최종대진화", key=f"evo3_{evo3['id']}", disabled=not can_evo3):
                    p_data["balls"]["마스터볼"] -= shortage; st.session_state.market_balls["마스터볼"] += shortage
                    for b_type, req in evo3['cost'].items():
                        discount = p_data["bonuses"].get(b_type, 0)
                        needed = max(0, req - discount)
                        holding = p_data["balls"].get(b_type, 0)
                        if holding >= needed: p_data["balls"][b_type] -= needed; st.session_state.market_balls[b_type] += needed
                        else: p_data["balls"][b_type] = 0; st.session_state.market_balls[b_type] += holding
                    
                    p_data["captured"].remove(evo3["from"])
                    p_data["captured"].append(evo3["name"])
                    p_data["score"] += evo3["points"]
                    p_data["bonuses"][evo3["bonus"]] += 1
                    st.session_state.log.insert(0, f"✨ {current_player_id}님이 최종 하이엔드형 {evo3['name']}(으)로의 3단 진화를 이룩했습니다!")
                    refill_market(3, idx)
                    next_phase()
                    
        st.write("---")
        if st.button("🏁 진화 단계 종료 및 차례 넘기기"): next_phase()

# --- 하단 배틀 로그 브리핑 ---
st.write("---")
st.subheader("📜 배틀 로그 브리핑 (최근 5개)")
for l in st.session_state.log[:5]: st.text(l)

if st.button("🔄 게임 시스템 완전 완전 초기화"):
    st.session_state.clear()
    st.rerun()
