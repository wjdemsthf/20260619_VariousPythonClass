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
    st.session_state.market_balls["마스터볼"] = 5
    
    # 야생 포켓몬 상점 (기본 포켓몬)
    st.session_state.pokemon_market = [
        {"id": 1, "name": "파이리", "cost": {"몬스터볼": 3}, "bonus": "몬스터볼", "points": 0, "stage": 1},
        {"id": 2, "name": "꼬부기", "cost": {"수퍼볼": 3}, "bonus": "다이브볼", "points": 1, "stage": 1},
        {"id": 3, "name": "이상해씨", "cost": {"하이퍼볼": 2, "몬스터볼": 1}, "bonus": "사파리볼", "points": 1, "stage": 1},
        {"id": 4, "name": "피카츄", "cost": {"사파리볼": 3}, "bonus": "수퍼볼", "points": 1, "stage": 1},
        {"id": 5, "name": "미뇽", "cost": {"다이브볼": 4}, "bonus": "하이퍼볼", "points": 2, "stage": 1},
    ]
    
    # 진화 가능 포켓몬 필드 (진화 대상이 내 필드에 있어야 함)
    st.session_state.evolution_market = [
        {"id": 101, "name": "리자몽", "from": "파이리", "cost": {"몬스터볼": 2, "하이퍼볼": 3}, "bonus": "마스터볼", "points": 4},
        {"id": 102, "name": "거북왕", "from": "꼬부기", "cost": {"수퍼볼": 2, "다이브볼": 3}, "bonus": "마스터볼", "points": 4},
        {"id": 103, "name": "이상해꽃", "from": "이상해씨", "cost": {"하이퍼볼": 4}, "bonus": "마스터볼", "points": 3},
        {"id": 104, "name": "라이츄", "from": "피카츄", "cost": {"수퍼볼": 4}, "bonus": "수퍼볼", "points": 3},
        {"id": 105, "name": "망나뇽", "from": "미뇽", "cost": {"하이퍼볼": 3, "사파리볼": 3}, "bonus": "마스터볼", "points": 5},
    ]
    
    st.session_state.players = {}
    st.session_state.log = []

# --- 헬퍼 함수: 다음 단계 및 턴 전환 ---
def next_phase():
    st.session_state.turn_phase += 1
    # 진화 단계(2)까지 모두 끝나면 다음 플레이어 턴으로
    if st.session_state.turn_phase > 2:
        # 턴 종료 시 볼 보유 제한(8개) 체크 및 초과분 폐기 규칙
        curr_p = f"Player {st.session_state.current_turn + 1}"
        total_balls = sum(st.session_state.players[curr_p]["balls"].values())
        if total_balls > 8:
            over_count = total_balls - 8
            # 무작위 혹은 단순 차감으로 8개 맞춤
            for b in BALL_TYPES:
                while st.session_state.players[curr_p]["balls"][b] > 0 and over_count > 0:
                    st.session_state.players[curr_p]["balls"][b] -= 1
                    st.session_state.market_balls[b] += 1
                    over_count -= 1
            st.session_state.log.insert(0, f"⚠️ {curr_p}님의 볼이 8개를 초과하여 보유량이 8개로 강제 조정되었습니다.")
            
        st.session_state.turn_phase = 0
        st.session_state.selected_balls = []
        st.session_state.current_turn = (st.session_state.current_turn + 1) % st.session_state.num_players
    st.rerun()

# --- 게임 시작 전 인원 설정 ---
if not st.session_state.get("game_started", False):
    st.subheader("👥 트레이너 대결 인원 선택")
    player_count = st.radio("플레이어 수", [2, 3, 4], index=0, horizontal=True)
    if st.button("🎮 리그 시작"):
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
        st.session_state.log = ["🔴 스플렌더 리그가 시작되었습니다! 1P의 차례입니다."]
        st.rerun()
    st.stop()

# --- 메인 게임 플레이 정보 설정 ---
current_player_id = f"Player {st.session_state.current_turn + 1}"
p_data = st.session_state.players[current_player_id]
phases = ["🟢 1단계: 볼 수집 하기", "🔵 2단계: 포켓몬 구매(포획) 하기", "🟣 3단계: 포켓몬 진화 시키기"]

# 레이아웃 분할
col_left, col_right = st.columns([1, 2])

# 왼쪽: 스코어보드 및 대시보드
with col_left:
    st.header("📋 트레이너 상황판")
    for p_id, data in st.session_state.players.items():
        is_curr = "▶️ " if p_id == current_player_id else ""
        with st.expander(f"{is_curr}{p_id} ({data['score']} 점)", expanded=(p_id == current_player_id)):
            st.markdown("**🎒 보유 중인 볼 (최대 8개 제한)**")
            total_b = sum(data["balls"].values())
            st.caption(f"현재 총 합계: {total_b} / 8 개")
            
            b_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                b_cols[idx % 3].metric(b_name, f"{data['balls'][b_name]}개")
                
            st.markdown("**💎 획득한 영구 보너스 볼**")
            bonus_cols = st.columns(3)
            for idx, b_name in enumerate(BALL_TYPES):
                bonus_cols[idx % 3].metric(f"✨ {b_name[:3]}", f"+{data['bonuses'][b_name]}")
                
            st.markdown(f"**🐾 소유한 포켓몬:** {', '.join(data['captured']) if data['captured'] else '없음'}")

# 오른쪽: 단계별 플레이 구역
with col_right:
    st.markdown(f"<div class='highlight-box'><h3>{phases[st.session_state.turn_phase]}</h3>"
                f"현재 순서: <b>{current_player_id}</b>의 차례입니다.</div>", unsafe_allow_html=True)
    
    # ----------------------------------------
    # [PHASE 0] 볼 수집 단계
    # ----------------------------------------
    if st.session_state.turn_phase == 0:
        st.subheader("볼 가져오기 규칙")
        st.caption("1. 서로 다른 종류 3가지 각 1개씩\n2. 동일한 종류 1가지 2개 (필드에 4개 이상 있을 때만)\n3. 마스터볼은 독점(한 번에 딱 1개만 수집 가능, 최대 1개 보유 제한)")
        
        # 마스터볼 보유 예외 체크
        has_master = p_data["balls"]["마스터볼"] > 0
        
        st.write(f"**내가 이번 턴에 고른 볼:** {', '.join(st.session_state.selected_balls) if st.session_state.selected_balls else '없음'}")
        
        grid_b = st.columns(3)
        for idx, b_name in enumerate(BALL_TYPES):
            stock = st.session_state.market_balls[b_name]
            with grid_b[idx % 3]:
                st.markdown(f"**{b_name}** (필드: {stock}개)")
                
                # 버튼 비활성화 로직 설계
                btn_disabled = False
                if stock <= 0: btn_disabled = True
                if b_name == "마스터볼" and (has_master or len(st.session_state.selected_balls) > 0): btn_disabled = True
                if len(st.session_state.selected_balls) >= 3: btn_disabled = True
                if b_name in st.session_state.selected_balls and len(st.session_state.selected_balls) != 1: btn_disabled = True
                if b_name in st.session_state.selected_balls and stock < 3: btn_disabled = True # 스플렌더 원본 규칙 반영 (동일 2개 확보 시 필드 제한)
                
                if st.button(f"➕ {b_name} 선택", key=f"sel_{b_name}", disabled=btn_disabled):
                    st.session_state.selected_balls.append(b_name)
                    st.rerun()
                    
        # 수집 완료 및 확정 처리 버튼들
        b_actions = st.columns(3)
        
        # 1. 다른 종류 3개 확정
        uniq_selected = len(set(st.session_state.selected_balls))
        can_confirm_3 = (uniq_selected == 3 and "마스터볼" not in st.session_state.selected_balls)
        if b_actions[0].button("✔️ 다른 볼 3개 확정", disabled=not can_confirm_3):
            for b in st.session_state.selected_balls:
                st.session_state.market_balls[b] -= 1
                p_data["balls"][b] += 1
            st.session_state.log.insert(0, f"🔹 {current_player_id}님이 각기 다른 볼 3개를 수집했습니다.")
            next_phase()
            
        # 2. 동일 종류 2개 확정
        can_confirm_2 = (len(st.session_state.selected_balls) == 1 and st.session_state.selected_balls.count(st.session_state.selected_balls[0]) == 1)
        # 같은 것을 하나 더 고르는 액션 처리용
        if len(st.session_state.selected_balls) == 1 and "마스터볼" not in st.session_state.selected_balls:
            target_b = st.session_state.selected_balls[0]
            if b_actions[1].button(f"✔️ {target_b} 2개로 확정", disabled=(st.session_state.market_balls[target_b] < 4)):
                st.session_state.market_balls[target_b] -= 2
                p_data["balls"][target_b] += 2
                st.session_state.log.insert(0, f"🔹 {current_player_id}님이 {target_b} 2개를 수집했습니다.")
                next_phase()
                
        # 3. 마스터볼 독점 확정
        can_confirm_m = (len(st.session_state.selected_balls) == 1 and st.session_state.selected_balls[0] == "마스터볼")
        if b_actions[2].button("👑 마스터볼 1개 확정", disabled=not can_confirm_m):
            st.session_state.market_balls["마스터볼"] -= 1
            p_data["balls"]["마스터볼"] += 1
            st.session_state.log.insert(0, f"👑 {current_player_id}님이 마스터볼 1개를 획득했습니다.")
            next_phase()
            
        if st.button("볼 수집 패스하고 다음 단계로 ➡️"):
            st.session_state.selected_balls = []
            next_phase()

    # ----------------------------------------
    # [PHASE 1] 구매 단계
    # ----------------------------------------
    elif st.session_state.turn_phase == 1:
        st.subheader("🛒 야생 포켓몬 포획 상점")
        st.caption("마스터볼은 부족한 자원을 대체할 수 있는 조커로 자동 계산됩니다.")
        
        grid_p = st.columns(2)
        for idx, poke in enumerate(st.session_state.pokemon_market):
            with grid_p[idx % 2]:
                st.markdown(f"### **{poke['name']}** (점수: {poke['points']}점)")
                st.caption(f"보상 보너스: ✨ {poke['bonus']}")
                
                # 마스터볼 조커 계산을 포함한 실구매 연산
                shortage_total = 0
                cost_preview = []
                
                for b_type, req in poke['cost'].items():
                    discount = p_data["bonuses"].get(b_type, 0)
                    actual_needed = max(0, req - discount)
                    my_holding = p_data["balls"].get(b_type, 0)
                    
                    if my_holding < actual_needed:
                        shortage_total += (actual_needed - my_holding)
                    cost_preview.append(f"- {b_type}: 필요 {req}개 (보유 {my_holding}개 / 보너스할인 -{discount})")
                
                st.markdown("\n".join(cost_preview))
                my_master_balls = p_data["balls"]["마스터볼"]
                
                # 구매 가능 여부 판정
                can_buy = (my_master_balls >= shortage_total)
                if shortage_total > 0:
                    st.warning(f"볼 부족분 {shortage_total}개를 마스터볼로 대체 가능 여부: {'가능' if can_buy else '불가'}")
                
                if st.button(f"⚽ {poke['name']} 포획", key=f"buy_poke_{poke['id']}", disabled=not can_buy):
                    # 자원 차감 및 상점 반납 로직 (조커 연산 포함)
                    master_used = shortage_total
                    p_data["balls"]["마스터볼"] -= master_used
                    st.session_state.market_balls["마스터볼"] += master_used
                    
                    for b_type, req in poke['cost'].items():
                        discount = p_data["bonuses"].get(b_type, 0)
                        actual_needed = max(0, req - discount)
                        my_holding = p_data["balls"].get(b_type, 0)
                        
                        if my_holding >= actual_needed:
                            p_data["balls"][b_type] -= actual_needed
                            st.session_state.market_balls[b_type] += actual_needed
                        else:
                            p_data["balls"][b_type] = 0
                            st.session_state.market_balls[b_type] += my_holding
                            
                    # 보상 적용
                    p_data["score"] += poke["points"]
                    p_data["captured"].append(poke["name"])
                    p_data["bonuses"][poke["bonus"]] += 1
                    
                    st.session_state.log.insert(0, f"🎉 {current_player_id}님이 {poke['name']}를 포획했습니다!")
                    st.session_state.pokemon_market.pop(idx)
                    next_phase()
                    
        st.write("---")
        if st.button("포획 패스하고 진화 단계로 ➡️"):
            next_phase()

    # ----------------------------------------
    # [PHASE 2] 진화 단계
    # ----------------------------------------
    elif st.session_state.turn_phase == 2:
        st.subheader("🧬 포켓몬 진화 연구소")
        st.caption("내 필드에 진화 전 단계 포켓몬이 존재하고, 진화 비용(볼 조건)을 만족하면 기존 포켓몬을 파기하고 교체 진화합니다.")
        
        evolved_any = False
        grid_e = st.columns(2)
        
        for idx, evo in enumerate(st.session_state.evolution_market):
            # 1. 내 가방에 진화 대상 원본 포켓몬이 있는지 검증
            if evo["from"] in p_data["captured"]:
                evolved_any = True
                with grid_e[idx % 2]:
                    st.markdown(f"### 🧬 **{evo['name']}** (점수: {evo['points']}점)")
                    st.info(f"진화 루트: `{evo['from']}` ➡️ `{evo['name']}`")
                    
                    # 진화 비용 계산 (마스터볼 대용 가능)
                    shortage_total = 0
                    cost_preview = []
                    for b_type, req in evo['cost'].items():
                        discount = p_data["bonuses"].get(b_type, 0)
                        actual_needed = max(0, req - discount)
                        my_holding = p_data["balls"].get(b_type, 0)
                        if my_holding < actual_needed:
                            shortage_total += (actual_needed - my_holding)
                        cost_preview.append(f"- {b_type}: 필요 {req}개 (보유 {my_holding}개)")
                        
                    st.markdown("\n".join(cost_preview))
                    my_master_balls = p_data["balls"]["마스터볼"]
                    can_evo = (my_master_balls >= shortage_total)
                    
                    if st.button(f"✨ {evo['name']}(으)로 진화시키기", key=f"evo_{evo['id']}", disabled=not can_evo):
                        # 비용 지불
                        master_used = shortage_total
                        p_data["balls"]["마스터볼"] -= master_used
                        st.session_state.market_balls["마스터볼"] += master_used
                        
                        for b_type, req in evo['cost'].items():
                            discount = p_data["bonuses"].get(b_type, 0)
                            actual_needed = max(0, req - discount)
                            my_holding = p_data["balls"].get(b_type, 0)
                            if my_holding >= actual_needed:
                                p_data["balls"][b_type] -= actual_needed
                                st.session_state.market_balls[b_type] += actual_needed
                            else:
                                p_data["balls"][b_type] = 0
                                st.session_state.market_balls[b_type] += my_holding
                                
                        # 핵심: 기존 포켓몬 파기 및 교체
                        p_data["captured"].remove(evo["from"])
                        p_data["captured"].append(evo["name"])
                        p_data["score"] += evo["points"]
                        p_data["bonuses"][evo["bonus"]] += 1
                        
                        st.session_state.log.insert(0, f"🔥 {current_player_id}님의 {evo['from']}(이)가 {evo['name']}(으)로 대진화 성공!")
                        st.session_state.evolution_market.pop(idx)
                        next_phase()
                        
        if not evolved_any:
            st.warning("현재 진화가 가능한 기본 포켓몬을 보유하고 있지 않습니다.")
            
        if st.button("🏁 진화 패스 및 턴 종료 (다음 트레이너에게)"):
            next_phase()

# --- 하단 배틀 로그 및 초기화 리셋 ---
st.write("---")
st.subheader("📜 리그 로그 브리핑 (최근 5개)")
for l in st.session_state.log[:5]:
    st.text(l)

if st.button("🔄 리그 완전 리셋 및 새 게임"):
    st.session_state.clear()
    st.rerun()
