import streamlit as st
import random

# 1. 게임 페이지 설정
st.set_page_config(page_title="포켓몬 스플렌더", layout="wide")
st.title("⚽ 포켓몬 스플렌더 (Pokémon Splendor)")
st.caption("몬스터볼을 모아 포켓몬을 포획하고, 최고의 포켓몬 마스터가 되세요!")

# 2. 게임 데이터 초기화 (포켓몬 카드 & 진화체)
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    
    # 플레이어 자원 및 점수
    st.session_state.player_balls = {"일반볼": 0, "수퍼볼": 0, "하이퍼볼": 0, "마스터볼": 0}
    st.session_state.player_score = 0
    st.session_state.captured_pokemon = []
    
    # 시장에 남아있는 몬스터볼 공급처
    st.session_state.market_balls = {"일반볼": 7, "수퍼볼": 7, "하이퍼볼": 7, "마스터볼": 5}
    
    # 포켓몬 카드 풀 (비용, 제공하는 보너스, 승점)
    st.session_state.pokemon_market = [
        {"name": "피카츄", "cost": {"일반볼": 2, "수퍼볼": 1}, "bonus": "수퍼볼", "points": 1, "tier": 1},
        {"name": "파이리", "cost": {"일반볼": 3}, "bonus": "하이퍼볼", "points": 1, "tier": 1},
        {"name": "꼬부기", "cost": {"수퍼볼": 3}, "bonus": "일반볼", "points": 1, "tier": 1},
        {"name": "이상해씨", "cost": {"하이퍼볼": 2}, "bonus": "하이퍼볼", "points": 1, "tier": 1},
        {"name": "리자몽", "cost": {"일반볼": 3, "하이퍼볼": 3}, "bonus": "마스터볼", "points": 3, "tier": 2},
        {"name": "거북왕", "cost": {"수퍼볼": 4, "하이퍼볼": 2}, "bonus": "마스터볼", "points": 4, "tier": 2},
        {"name": "뮤츠", "cost": {"일반볼": 4, "수퍼볼": 4, "하이퍼볼": 4}, "bonus": "마스터볼", "points": 5, "tier": 3},
    ]
    st.session_state.log = ["게임을 시작합니다! 코인을 모아 포켓몬을 잡으세요."]

# 로그 기록 함수
def log_message(msg):
    st.session_state.log.insert(0, msg)

# --- UI 레이아웃 분할 ---
col1, col2 = st.columns([1, 2])

# 왼쪽 사이드바 역할: 내 정보 및 보유 자원
with col1:
    st.header("👤 트레이너 정보")
    st.metric(label="🏆 현재 승점", value=f"{st.session_state.player_score} 점 / 15점 만점")
    
    st.subheader("🎒 내 가방 (몬스터볼)")
    b_cols = st.columns(4)
    for i, (ball, count) in enumerate(st.session_state.player_balls.items()):
        b_cols[i].metric(label=ball, value=count)
        
    st.subheader("포획한 포켓몬 목록")
    if st.session_state.captured_pokemon:
        st.write(", ".join(st.session_state.captured_pokemon))
    else:
        st.caption("아직 포획한 포켓몬이 없습니다.")

# 오른쪽 메인 화면: 몬스터볼 획득 및 포켓몬 상점
with col2:
    st.header("🛒 필드 (시장)")
    
    # 1. 몬스터볼 가져오기 세션
    st.subheader("🔴 몬스터볼 수집 (종류별로 1개씩 선택 가능)")
    ball_choices = []
    take_cols = st.columns(4)
    for i, (ball, stock) in enumerate(st.session_state.market_balls.items()):
        with take_cols[i]:
            st.text(f"{ball} (남은 개수: {stock})")
            if stock > 0:
                if st.button(f"{ball} 받기", key=f"take_{ball}"):
                    if len(ball_choices) < 3: # 간단한 규칙 처리
                        st.session_state.market_balls[ball] -= 1
                        st.session_state.player_balls[ball] += 1
                        log_message(f"필드에서 {ball} 1개를 가져왔습니다.")
                        st.rerun()

    st.write("---")

    # 2. 포켓몬 포획하기 세션
    st.subheader("✨ 야생 포켓몬 나타남 (포획하기)")
    
    grid_cols = st.columns(3)
    for idx, poke in enumerate(st.session_state.pokemon_market):
        with grid_cols[idx % 3]:
            st.markdown(f"### **{poke['name']}**")
            st.caption(f"티어: {poke['tier']} | 보너스: {poke['bonus']}")
            st.markdown(f"**승점: {poke['points']}점**")
            
            # 비용 표시
            cost_text = " 필요: " + ", ".join([f"{k} {v}개" for k, v in poke['cost'].items()])
            st.text(cost_text)
            
            # 구매 가능 여부 체크
            can_buy = True
            for ball_type, cost_amount in poke['cost'].items():
                if st.session_state.player_balls.get(ball_type, 0) < cost_amount:
                    can_buy = False
                    
            if st.button(f"{poke['name']} 포획", key=f"buy_{idx}", disabled=not can_buy):
                # 비용 지불 및 획득 처리
                for ball_type, cost_amount in poke['cost'].items():
                    st.session_state.player_balls[ball_type] -= cost_amount
                    st.session_state.market_balls[ball_type] += cost_amount # 코인 반납
                
                st.session_state.player_score += poke['points']
                st.session_state.captured_pokemon.append(poke['name'])
                log_message(f"🎉 {poke['name']}(을)를 포획했습니다! (+{poke['points']}점)")
                
                # 상점에서 제외 (프로토타입이므로 단순 삭제 또는 재생성 가능)
                st.session_state.pokemon_market.pop(idx)
                st.rerun()

# --- 하단 게임 로그 및 리셋 ---
st.write("---")
st.subheader("📜 행동 기록 (Log)")
for l in st.session_state.log[:5]: # 최근 5개 로그만 출력
    st.text(l)

if st.button("게임 초기화 🔄"):
    st.session_state.clear()
    st.rerun()
