import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 주식 대시보드 (나스닥 100 & 시총 탑티어)",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 글로벌 주식 인터랙티브 대시보드")
st.markdown("최근 1년 데이터 기준 주가와 시가총액 변화를 추적합니다. (데이터 출처: Yahoo Finance)")

# 2. 기본 제공 기업 리스트 (시총 상위 및 나스닥 100 주요 기업)
@st.cache_data
def get_default_companies():
    return {
        "MSFT": "마이크로소프트 (Microsoft)",
        "AAPL": "애플 (Apple)",
        "NVDA": "엔비디아 (NVIDIA)",
        "GOOGL": "알파벳 A (Alphabet)",
        "AMZN": "아마존 (Amazon)",
        "META": "메타 (Meta)",
        "BRK-B": "버크셔 해서웨이 (Berkshire Hathaway)",
        "LLY": "일라이 릴리 (Eli Lilly)",
        "AVGO": "브로드컴 (Broadcom)",
        "TSLA": "테슬라 (Tesla)",
        "TSM": "TSMC",
        "V": "비자 (Visa)",
        "WMT": "월마트 (Walmart)",
        "UNH": "유나이티드헬스 (UnitedHealth)",
        "XOM": "엑슨모빌 (Exxon Mobil)",
        "MA": "마스터카드 (Mastercard)",
        "JPM": "JP모건 체이스 (JPMorgan Chase)",
        "NVO": "노보 노디스크 (Novo Nordisk)",
        "PG": "프록터 앤 갬블 (P&G)",
        "ASML": "ASML",
        "ORCL": "오라클 (Oracle)",
        "COST": "코스트코 (Costco)",
        "HD": "홈디포 (Home Depot)",
        "BAC": "뱅크 오브 아메리카 (Bank of America)",
        "NFLX": "넷플릭스 (Netflix)",
        "AMD": "AMD",
        "QCOM": "퀄컴 (Qualcomm)",
        "TM": "토요타 (Toyota)",
        "ADBE": "어도비 (Adobe)",
        "SNDK": "샌디스크 (SanDisk)",
        "INTC": "인텔 (Intel)",
        "CSCO": "시스코 (Cisco)",
        "AMGN": "암젠 (Amgen)",
        "PEP": "펩시코 (PepsiCo)",
        "KO": "코카콜라 (Coca-Cola)"
    }

ticker_dict = get_default_companies()

# 3. 사이드바 구성
st.sidebar.header("⚙️ 대시보드 설정")

# [기능 1] 종목 검색 및 추가 기능
st.sidebar.subheader("🔍 종목 추가하기")
search_ticker = st.sidebar.text_input("야후 파이낸스 티커 입력 (예: NFLX, 기호 분리):").upper().strip()

# 세션 상태를 활용해 사용자가 추가한 커스텀 티커 관리
if 'custom_tickers' not in st.session_state:
    st.session_state.custom_tickers = {}

if st.sidebar.button("종목 추가"):
    if search_ticker:
        if search_ticker in ticker_dict or search_ticker in st.session_state.custom_tickers:
            st.sidebar.info(f"💡 {search_ticker}는 이미 리스트에 존재합니다.")
        else:
            with st.spinner(f"{search_ticker} 정보를 확인하는 중..."):
                try:
                    ticker_obj = yf.Ticker(search_ticker)
                    info = ticker_obj.info
                    # 회사 이름 가져오기 시도
                    comp_name = info.get('longName', search_ticker)
                    st.session_state.custom_tickers[search_ticker] = f"{comp_name} ({search_ticker}) *"
                    st.sidebar.success(f"✅ {search_ticker} 추가 완료!")
                except Exception:
                    st.sidebar.error("❌ 유효하지 않은 티커이거나 데이터를 가져올 수 없습니다.")

# 전체 선택 옵션 결합 (기본 목록 + 사용자 추가 목록)
full_options = {**ticker_dict, **st.session_state.custom_tickers}

# 멀티 셀렉트 박스
selected_names = st.sidebar.multiselect(
    "시각화할 기업 선택:",
    options=list(full_options.values()),
    default=list(ticker_dict.values())[:5] # 초기값은 상위 5개
)

selected_tickers = [ticker for ticker, name in full_options.items() if name in selected_names]

# [기능 2] 주가 vs 시가총액 토글 기능 (라디오 버튼 형태)
st.sidebar.subheader("📊 데이터 표시 형태")
view_mode = st.sidebar.radio(
    "지표를 선택하세요:",
    ("주가 (Price, USD)", "시가총액 (Market Cap, USD)")
)

# 4. 데이터 로드 및 처리
if not selected_tickers:
    st.warning("⚠️ 최소 한 개 이상의 기업을 선택해 주세요.")
else:
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    with st.spinner('데이터를 불러오는 중입니다...'):
        try:
            # yfinance 데이터 다운로드
            data_download = yf.download(selected_tickers, start=start_date, end=end_date, group_by='ticker')
            
            df_price = pd.DataFrame(index=data_download.index)
            df_cap = pd.DataFrame(index=data_download.index)
            
            for ticker in selected_tickers:
                # 1개 기업만 선택했을 때와 여러 개 선택했을 때의 데이터 구조 처리
                if len(selected_tickers) == 1:
                    close_data = data_download['Close']
                    # 시가총액 변동 추이를 계산하기 위해 현재 총 발행주식수 대입 (근사치 구동)
                    shares_out = yf.Ticker(ticker).info.get('sharesOutstanding', 1)
                else:
                    close_data = data_download[ticker]['Close'] if ticker in data_download.columns.levels[0] else None
                    shares_out = yf.Ticker(ticker).info.get('sharesOutstanding', 1)

                if close_data is not None:
                    df_price[ticker] = close_data
                    # 일별 시가총액 = 일별 종가 * 발행주식수
                    df_cap[ticker] = close_data * shares_out
                    
        except Exception as e:
            st.error(f"데이터 로드 오류: {e}")
            df_price, df_cap = None, None

    # 데이터 시각화 렌더링
    active_df = df_price if "주가" in view_mode else df_cap
    
    if active_df is not None and not active_df.empty:
        fig = go.Figure()
        
        for ticker in active_df.columns:
            display_name = full_options.get(ticker, ticker)
            valid_data = active_df[ticker].dropna()
            
            if not valid_data.empty:
                if "주가" in view_mode:
                    hover_format = f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>주가: $%{{y:.2f}}<extra></extra>"
                    yaxis_label = "주가 ($)"
                else:
                    # 시가총액의 경우 가독성을 위해 빌리언($B, 10억 달러) 단위 툴팁 고려 가능하나 기본 값 표기
                    hover_format = f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>시총: $%{{y:,.0f}}<extra></extra>"
                    yaxis_label = "시가총액 ($)"

                fig.add_trace(go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    mode='lines',
                    name=display_name,
                    hovertemplate=hover_format
                ))
            
        fig.update_layout(
            title=f"최근 1년 {view_mode} 변화 추이",
            xaxis_title="날짜",
            yaxis_title=yaxis_label,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=50, r=40, t=80, b=120),
            height=650
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📊 상세 데이터 테이블 보기"):
            st.dataframe(active_df, use_container_width=True)
