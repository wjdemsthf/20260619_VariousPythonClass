import streamlit as st
import random

# 1. 페이지 설정 및 네온 스타일 커스텀 CSS (화려함 및 자원 가독성 극대화)
st.set_page_config(page_title="포켓몬 스플렌더: 프리미엄 마스터즈", layout="wide")
st.markdown("""
    <style>
    /* 기본 테마 및 배경 */
    .stApp { background-color: #0B0C10; color: #C5C6C7; font-family: 'Helvetica Neue', Arial, sans-serif; }
    
    /* 대시보드 및 메트릭 기본 레이아웃 개조 */
    div[data-testid="stMetric"] { background: linear-gradient(145deg, #151B24, #0F131A); padding: 10px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.4); }
    
    /* 자원별 가독성 전용 네온 스킨 매핑 */
    .ball-일반 { border: 2px solid #FF4B4B !important; color: #FF6B6B !important; }
    .ball-수퍼 { border: 2px solid #1C7ED6 !important; color: #339AF0 !important; }
    .ball-하이퍼 { border: 2px solid #FCC419 !important; color: #FFD43B !important; }
    .ball-사파리 { border: 2px solid #37B24D !important; color: #51CF66 !important; }
    .ball-다이브 { border: 2px solid #1098AD !important; color: #22B8CF !important; }
    .ball-마스터 { border: 2px solid #9C36B5 !important; color: #CC5DE8 !important; }
    
    /* 자원 스탯 보드 내 내부 텍스트 정렬 */
    .resource-card { padding: 8px; border-radius: 8px; text-align: center; margin-bottom: 5px; background: #1A1F26; }
    .resource-title { font-size: 13px; font-weight: bold; margin-bottom: 2px; }
    .resource-value { font-size: 18px; font-weight: 800; }
    
    /* 범용 버튼 스타일 */
    .stButton>button { background: linear-gradient(135deg, #1F2833, #2C3E50); color: #66FCF1; border: 1px solid #45A29E; border-radius: 8px; font-weight: bold; transition: all 0.3s ease; }
    .stButton>button:hover { background: linear-gradient(135deg, #45A29E, #66FCF1); color: #0B0C10; box-shadow: 0 0 12px #66FCF1; transform: translateY(-2px); }
    
    /* 알림창 스킨 */
    .highlight-box { background: linear-gradient(90deg, #1F2833, #0B0C10); border-left: 6px solid #66FCF1; padding: 18px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.5); }
    
    /* 단계별 카드 그래디언트 외곽선 */
    .tier-1 { background-color: #111A1E; border: 2px solid #2ECC71; padding: 15px; border-radius: 12px; box-shadow: 0 0 8px rgba(46, 204, 113, 0.3); margin-bottom: 12px; }
    .tier-2 { background-color: #121622; border: 2px solid #3498DB; padding: 15px; border-radius: 12px; box-shadow: 0 0 8px rgba(52, 152, 219, 0.3); margin-bottom: 12px; }
    .tier-3 { background-color: #1C121E; border: 2px solid #9B59B6; padding: 15px; border-radius: 12px; box-shadow: 0 0 12px rgba(155, 89, 182, 0.5); margin-bottom: 12px; }
    
    .player-badge { font-size: 22px; font-weight: bold; color: #66FCF1; text-shadow: 0 0 10px rgba(102, 252, 241, 0.6); animation: pulse 2s infinite; }
    @keyframes pulse { 0% { opacity: 0.8; } 50% { opacity: 1; text-shadow: 0 0 18px rgba(102, 252, 241, 0.9); } 100% { opacity: 0.8; } }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ 포켓몬 스플렌더: 프리미엄 마스터즈")

BALL_TYPES = ["몬스터볼", "수퍼볼", "하이퍼볼", "사파리볼", "다이브볼", "마스터볼"]
BALL_STYLES = {
    "몬스터볼": {"class": "ball-일반", "prefix": "🔴"},
    "수퍼볼": {"class": "ball-수퍼", "prefix": "🔵"},
    "하이퍼볼": {"class": "ball-하이퍼", "prefix": "🟡"},
    "사파리볼": {"class": "ball-사파리", "prefix": "🟢"},
    "다이브볼": {"class": "ball-다이브", "prefix": "🌊"},
    "마스터볼": {"class": "ball-마스터", "prefix": "🟣"}
}

# 2. 3단계 대진화 트랙 고화력 덱 구성
TOTAL_POKEMON_DECK = {
    1: [
        {"id": 1, "name": "파이리", "cost": {"몬스터볼": 3}, "bonus": "몬스터볼", "points": 0, "stage": 1},
        {"id": 2, "name": "꼬부기", "cost": {"수퍼볼": 3}, "bonus": "다이브볼", "points": 0, "stage": 1},
        {"id": 3, "name": "이상해씨", "cost": {"하이퍼볼": 3}, "bonus": "사파리볼", "points": 0, "stage": 1},
        {"id": 4, "name": "피츄", "cost": {"사파리볼": 4}, "bonus": "수퍼볼", "points": 1, "stage": 1},
        {"id": 5, "name": "미뇽", "cost": {"다이브볼": 4}, "bonus": "하이퍼볼", "points": 1, "stage": 1},
    ],
    2: [
        {"id": 11, "name": "리자드", "from": "파이리", "cost": {"몬스터볼": 3, "하이퍼볼": 2}, "bonus": "몬스터볼", "points": 2, "stage": 2},
        {"id": 12, "name": "어니부기", "from": "꼬부기", "cost": {"수퍼볼": 3, "다이브볼": 2}, "bonus": "다이브볼", "points": 2, "stage": 2},
        {"id": 13, "name": "이상해풀", "from": "이상해씨", "cost": {"하이퍼볼": 3, "사파리볼": 3}, "bonus": "사파리볼", "points": 3, "stage": 2},
        {"id": 14, "name": "피카츄", "from": "피츄", "cost": {"사파리볼": 2, "수퍼볼": 3}, "bonus": "수퍼볼", "points": 2, "stage": 2},
        {"id": 15, "name": "신뇽", "from": "미뇽", "cost": {"다이브볼": 3, "하이퍼볼": 3}, "bonus": "하이퍼볼", "points": 3, "stage": 2},
    ],
    3: [
        {"id": 21, "name": "리자몽", "from": "리자드", "cost": {"몬스터볼": 4, "수퍼볼": 2, "하이퍼볼": 3}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 22, "name": "거북왕", "from": "어니부기", "cost": {"수퍼볼": 4, "다이브볼": 4}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 23, "name": "이상해꽃", "from": "이상해풀", "cost": {"하이퍼볼": 5, "사파리볼": 3}, "bonus": "마스터볼", "points": 6, "stage": 3},
        {"id": 24, "name": "라이츄", "from": "피카츄", "cost": {"수퍼볼": 4, "사파리볼": 4}, "bonus": "마스터볼", "points": 5, "stage": 3},
        {"id": 25, "name": "망나뇽", "from": "신뇽", "cost": {"하이퍼볼": 3, "사파리볼": 3, "다이브볼": 3}, "bonus": "마스터볼", "points": 6, "stage": 3},
    ]
}

if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.game_started = False
    st.session_state.current_turn = 0
    st.session_state.turn_phase = 0
    st.session_state.selected_balls = []
    
    st.session_state.market_balls = {b: 7 for b in BALL_TYPES if b != "마스터볼"}
    st.session_state.market_balls["마스터볼"] = 5
    
    st.session_state.decks = {
        1: list(TOTAL_POKEMON_DECK[1]), 2: list(TOTAL_POKEMON_DECK[2]), 3: list(TOTAL_POKEMON_DECK[3])
    }
    for s in [1, 2, 3]: random.shuffle(st.session_state.decks[s])
        
    st.session_state.field_market = {
        1: [st.session_state.decks[1].pop() for _ in range(3) if st.session_state.decks[1]],
        2: [st.session_state.decks[2].pop() for _ in range(3) if st.session_state.decks[2]],
        3: [st.session_state.decks[3].pop() for _ in range(3) if st.session_state.decks[3]],
    }
    st.session_state.players = {}
    st.session_state.log = []

if "turn_phase" not in st.session_state: st.session_state.turn_phase = 0
if "selected_balls" not in st.session_state: st.session_state.selected_balls = []

def finish_turn():
    curr_p = f"Player {st.session_state.current_turn + 1}"
    total_balls = sum(st.session_state.players[curr_p]["balls"].values())
    if total_balls > 8:
        over_count = total_balls - 8
        for b in BALL_TYPES:
            while st.session_state.players[curr_p]["balls"][b] > 0 and over_count > 0:
                st.session_state.players[curr_p]["balls"][b] -= 1
                st.session_state.market_balls[b] += 1
                over_count -= 1
        st.session_state.log.insert(0, f"⚠️ {curr_p}님의 가방이 가득 차 초과 자원이 필드로 자동 반납되었습니다.")
        
    st.session_state.turn_phase = 0
    st.session_state.selected_balls = []
    st.session_state.current_turn = (st.session_state.current_turn + 1) % st.session_state.num_players
    st.rerun()

def refill_market(stage, index):
    if st.session_state.decks[stage]:
        st.session_state.field_market[stage][index] = st.session_state.decks[stage].pop()
    else:
        st.session_state.field_market[stage].pop(index)

# --- 트레이너 등록 대기실 ---
if not st.session_state.get("game_started", False):
    st.subheader("👥 리그 참전 트레이너 인원 선택")
    p_count = st.radio("플레이어 인원수", [2, 3, 4], index=0, horizontal=True)
    if st.button("🎮 프리미엄 리그 매치 스타트"):
        st.session_state.num_players = p_count
        st.session_state.players = {
            f"Player {i+1}": {
                "balls": {b: 0 for b in BALL_TYPES},
                "bonuses": {b: 0 for b in BALL_TYPES},
                "score": 0,
                "captured": []
            } for i in range(p_count)
        }
        st.session_state.game_started = True
        st.session_state.log = ["✨ 최고의 그래픽 테마 스플렌더 매치 개막! 1P 행동을 대기합니다."]
        st.rerun()
    st.stop()

current_player_id = f"Player {st.session_state.current_turn + 1}"
p_data = st.session_state.players[current_player_id]
phases = ["🟢 PHASE 1: 자원 보급 스테이션", "🔵 PHASE 2: 통합 진화 포획 마켓플레이스 (1~3단계 전체 거래 가능)"]

col_left, col_right = st.columns([1, 2])

# [가독성 패치 반영] 왼쪽 상황판 대시보드 리팩토링
with col_left:
    st.markdown("### 🏆 실시간 트레이너 랭킹")
    for p_id, data in st.session_state.players.items():
        is_curr = "▶️ " if p_id == current_player_id else ""
        badge_class = "class='player-badge'" if p_id == current_player_id else ""
        
        with st.expander(f"{is_curr}{p_id} (⭐ {data['score']} 점)", expanded=(p_id == current_player_id)):
            if p_id == current_player_id:
                st.markdown(f"<div {badge_class}>🌟 당신의 차례입니다!</div>", unsafe_allow_html=True)
            
            # 가방 용량 시각화 게이지 바 패치
            total_b = sum(data["balls"].values())
            st.markdown(f"**🎒 가방 보관 점유율** ({total_b} / 8 개)")
            st.progress(min(1.0, total_b / 8.0))
            
            # [핵심] 자원 상태 카드로 가독성 높인 파트 (HTML 커스텀 바인딩)
            st.markdown("<div style='margin-top:10px;'><b>🎒 소지품 정보 (보유량 + 영구할인 패시브)</b></div>", unsafe_allow_html=True)
            
            res_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                style_info = BALL_STYLES[b_name]
                ball_count = data["balls"][b_name]
                bonus_count = data["bonuses"][b_name]
                
                # 가방 수량과 무한 할인 패시브를 다채롭고 큰 폰트로 통합 명시
                res_cols[idx % 3].markdown(f"""
                <div class="resource-card {style_info['class']}">
                    <div class="resource-title">{style_info['prefix']} {b_name}</div>
                    <div class="resource-value">{ball_count} <span style="font-size:12px; opacity:0.8;">(+{bonus_count}💎)</span></div>
                </div>
                """, unsafe_allow_html=True)
                
            st.markdown(f"<div style='margin-top:10px;'><b>🐾 도감 획득 내역:</b> {', '.join(data['captured']) if data['captured'] else '비어 있음'}</div>", unsafe_allow_html=True)

# 오른쪽 컨트롤 타워
with col_right:
    current_phase_idx = st.session_state.get("turn_phase", 0)
    st.markdown(f"<div class='highlight-box'><h2>{phases[current_phase_idx]}</h2>"
                f"현재 액션 진행 중인 마스터: <b>{current_player_id}</b></div>", unsafe_allow_html=True)
    
    # ----------------------------------------
    # [PHASE 0] 자원 보급 스테이션
    # ----------------------------------------
    if current_phase_idx == 0:
        st.subheader("🔴 보급소 필드 현황 및 장바구니")
        selected = st.session_state.selected_balls
        
        if selected:
            st.write("**현재 바구니 내역 (클릭 시 가방에서 취소 반납):**")
            basket_cols = st.columns(len(selected))
            for s_idx, b_item in enumerate(selected):
                if basket_cols[s_idx].button(f"❌ {b_item}", key=f"cancel_{b_item}_{s_idx}"):
                    st.session_state.selected_balls.pop(s_idx)
                    st.rerun()
        else:
            st.info("💡 보급소에서 가져갈 볼을 하단에서 골라 담아주세요.")
            
        has_two_same = len(selected) == 2 and selected[0] == selected[1]
        has_master = p_data["balls"]["마스터볼"] > 0
        
        grid_b = st.columns(3)
        for idx, b_name in enumerate(BALL_TYPES):
            stock = st.session_state.market_balls[b_name]
            style_info = BALL_STYLES[b_name]
            with grid_b[idx % 3]:
                st.markdown(f"### {style_info['prefix']} **{b_name}**")
                st.markdown(f"🏟️ 필드 매장 잔량: **{stock}**개")
                
                btn_disabled = False
                if stock <= 0: btn_disabled = True
                if has_two_same: btn_disabled = True
                if b_name == "마스터볼" and (has_master or len(selected) > 0): btn_disabled = True
                if len(selected) >= 3: btn_disabled = True
                if b_name in selected and len(selected) == 1 and stock < 4: btn_disabled = True
                if b_name in selected and len(selected) >= 2: btn_disabled = True
                
                if st.button(f"➕ 선택하기", key=f"pick_{b_name}_{idx}", disabled=btn_disabled):
                    st.session_state.selected_balls.append(b_name)
                    st.rerun()
                    
        st.write("---")
        b_actions = st.columns(3)
        if b_actions[0].button("✔️ 서로 다른 3종 확정 수령", disabled=not (len(set(selected)) == 3 and "마스터볼" not in selected)):
            for b in selected: st.session_state.market_balls[b] -= 1; p_data["balls"][b] += 1
            st.session_state.log.insert(0, f"🔹 {current_player_id}님이 다른 볼 3종을 수령했습니다.")
            st.session_state.turn_phase = 1
            st.rerun()
            
        if len(selected) == 1 and "마스터볼" not in selected:
            t_ball = selected[0]
            if b_actions[1].button(f"✔️ {t_ball} 2개 묶음 확정 수령", disabled=(st.session_state.market_balls[t_ball] < 4)):
                st.session_state.market_balls[t_ball] -= 2; p_data["balls"][t_ball] += 2
                st.session_state.log.insert(0, f"🔹 {current_player_id}님이 동일 볼 2개를 대량 수령했습니다.")
                st.session_state.turn_phase = 1
                st.rerun()
                
        if b_actions[2].button("👑 조커 마스터볼 수령", disabled=not (len(selected) == 1 and selected[0] == "마스터볼")):
            st.session_state.market_balls["마스터볼"] -= 1; p_data["balls"]["마스터볼"] += 1
            st.session_state.log.insert(0, f"👑 {current_player_id}님이 마스터 조커볼을 독점 수령했습니다.")
            st.session_state.turn_phase = 1
            st.rerun()
            
        if st.button("보급 패스하고 바로 포획/진화 장터로 건너뛰기 ➡️"):
            st.session_state.turn_phase = 1
            st.rerun()

    # ----------------------------------------
    # [PHASE 1] 통합 진화 포획 마켓플레이스
    # ----------------------------------------
    elif current_phase_idx == 1:
        st.subheader("🪐 전 등급 올인원 프리미엄 조달 시장")
        
        # --- [1단계 시장 섹션 배치] ---
        st.markdown(f"##### 🟢 야생 개체 [1단계 코어] (더미 잔여: {len(st.session_state.decks[1])}장)")
        g1 = st.columns(3)
        for idx, p1 in enumerate(st.session_state.field_market[1]):
            with g1[idx]:
                st.markdown(f"<div class='tier-1'><b>🌳 {p1['name']}</b> (승점: {p1['points']}점)<br>⚡ 무한패시브 보상: +1 {p1['bonus']}</div>", unsafe_allow_html=True)
                shortage = 0
                cost_info = []
                for b_t, req in p1['cost'].items():
                    disc = p_data["bonuses"].get(b_t, 0)
                    need = max(0, req - disc)
                    hold = p_data["balls"].get(b_t, 0)
                    if hold < need: shortage += (need - hold)
                    cost_info.append(f"▫️ {b_t}: {req}개 (보유:{hold}/할인:{disc})")
                st.markdown("\n".join(cost_info))
                can_p1 = p_data["balls"]["마스터볼"] >= shortage
                
                if st.button(f"⚽ {p1['name']} 포획", key=f"buy_m1_{p1['id']}", disabled=not can_p1):
                    p_data["balls"]["마스터볼"] -= shortage; st.session_state.market_balls["마스터볼"] += shortage
                    for b_t, req in p1['cost'].items():
                        disc = p_data["bonuses"].get(b_t, 0)
                        need = max(0, req - disc)
                        hold = p_data["balls"].get(b_t, 0)
                        if hold >= need: p_data["balls"][b_t] -= need; st.session_state.market_balls[b_t] += need
                        else: p_data["balls"][b_t] = 0; st.session_state.market_balls[b_t] += hold
                    p_data["score"] += p1["points"]; p_data["captured"].append(p1["name"]); p_data["bonuses"][p1["bonus"]] += 1
                    st.session_state.log.insert(0, f"🎉 {current_player_id}님이 {p1['name']}(을)를 포획 도감 등록했습니다.")
                    refill_market(1, idx)
                    finish_turn()

        # --- [2단계 시장 섹션 배치] ---
        st.markdown(f"##### 🔵 중간 진화체 [2단계 엘리트] (더미 잔여: {len(st.session_state.decks[2])}장)")
        g2 = st.columns(3)
        for idx, p2 in enumerate(st.session_state.field_market[2]):
            with g2[idx]:
                st.markdown(f"<div class='tier-2'><b>🔥 {p2['from']} ➔ {p2['name']}</b><br>⭐ 승점: {p2['points']}점 | 보상: +1 {p2['bonus']}</div>", unsafe_allow_html=True)
                shortage = 0
                cost_info = []
                for b_t, req in p2['cost'].items():
                    disc = p_data["bonuses"].get(b_t, 0)
                    need = max(0, req - disc)
                    hold = p_data["balls"].get(b_t, 0)
                    if hold < need: shortage += (need - hold)
                    cost_info.append(f"▫️ {b_t}: {req}개 (보유:{hold})")
                st.markdown("\n".join(cost_info))
                
                has_o2 = p2["from"] in p_data["captured"]
                can_p2 = has_o2 and (p_data["balls"]["마스터볼"] >= shortage)
                
                if st.button(f"⚡ {p2['name']} 진화구입", key=f"buy_m2_{p2['id']}", disabled=not can_p2):
                    p_data["balls"]["마스터볼"] -= shortage; st.session_state.market_balls["마스터볼"] += shortage
                    for b_t, req in p2['cost'].items():
                        disc = p_data["bonuses"].get(b_t, 0)
                        need = max(0, req - disc)
                        hold = p_data["balls"].get(b_t, 0)
                        if hold >= need: p_data["balls"][b_t] -= need; st.session_state.market_balls[b_t] += need
                        else: p_data["balls"][b_t] = 0; st.session_state.market_balls[b_t] += hold
                    p_data["captured"].remove(p2["from"]); p_data["captured"].append(p2["name"])
                    p_data["score"] += p2["points"]; p_data["bonuses"][p2["bonus"]] += 1
                    st.session_state.log.insert(0, f"🔥 {current_player_id}님의 {p2['from']}가 {p2['name']}(으)로 대진화!")
                    refill_market(2, idx)
                    finish_turn()

        # --- [3단계 시장 섹션 배치] ---
        st.markdown(f"##### 🍇 최종 하이엔드 [3단계 레전더리] (더미 잔여: {len(st.session_state.decks[3])}장)")
        g3 = st.columns(3)
        for idx, p3 in enumerate(st.session_state.field_market[3]):
            with g3[idx]:
                st.markdown(f"<div class='tier-3'><b>👑 {p3['from']} ➔ {p3['name']}</b><br>⭐ 승점: {p3['points']}점 | 보상: +1 {p3['bonus']}</div>", unsafe_allow_html=True)
                shortage = 0
                cost_info = []
                for b_t, req in p3['cost'].items():
                    disc = p_data["bonuses"].get(b_t, 0)
                    need = max(0, req - disc)
                    hold = p_data["balls"].get(b_t, 0)
                    if hold < need: shortage += (need - hold)
                    cost_info.append(f"▫️ {b_t}: {req}개 (보유:{hold})")
                st.markdown("\n".join(cost_info))
                
                has_o3 = p3["from"] in p_data["captured"]
                can_p3 = has_o3 and (p_data["balls"]["마스터볼"] >= shortage)
                
                if st.button(f"👑 {p3['name']} 최종결제", key=f"buy_m3_{p3['id']}", disabled=not can_p3):
                    p_data["balls"]["마스터볼"] -= shortage; st.session_state.market_balls["마스터볼"] += shortage
                    for b_t, req in p3['cost'].items():
                        disc = p_data["bonuses"].get(b_t, 0)
                        need = max(0, req - disc)
                        hold = p_data["balls"].get(b_t, 0)
                        if hold >= need: p_data["balls"][b_t] -= need; st.session_state.market_balls[b_t] += need
                        else: p_data["balls"][b_t] = 0; st.session_state.market_balls[b_t] += hold
                    p_data["captured"].remove(p3["from"]); p_data["captured"].append(p3["name"])
                    p_data["score"] += p3["points"]; p_data["bonuses"][p3["bonus"]] += 1
                    st.session_state.log.insert(0, f"✨ {current_player_id}님이 최종 전설개체 {p3['name']}(으)로의 정점 도달!")
                    refill_market(3, idx)
                    finish_turn()
                    
        st.write("---")
        if st.button("🏁 상점 행동 없음 (이대로 턴 완전히 종료)"):
            finish_turn()

# --- 하단 배틀 로그 브리핑 ---
st.write("---")
st.subheader("📜 마스터즈 배틀 실시간 브리핑 로그")
for l in st.session_state.log[:5]: st.text(l)

if st.button("🔄 토너먼트 시스템 완전 완전 초기화"):
    st.session_state.clear()
    st.rerun()
