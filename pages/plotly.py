import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 주식 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 글로벌 주식 인터랙티브 대시보드")
st.markdown("최근 1년 데이터 기준 주가와 시가총액 변화를 추적합니다. (캐싱 적용 버전)")

# 기본 제공 기업 리스트
@st.cache_data
def get_default_companies():
    return {
        "MSFT": "마이크로소프트 (Microsoft)", "AAPL": "애플 (Apple)", "NVDA": "엔비디아 (NVIDIA)",
        "GOOGL": "알파벳 A (Alphabet)", "AMZN": "아마존 (Amazon)", "META": "메타 (Meta)",
        "BRK-B": "버크셔 해서웨이 (Berkshire Hathaway)", "LLY": "일라이 릴리 (Eli Lilly)",
        "AVGO": "브로드컴 (Broadcom)", "TSLA": "테슬라 (Tesla)", "TSM": "TSMC",
        "V": "비자 (Visa)", "WMT": "월마트 (Walmart)", "UNH": "유나이티드헬스 (UnitedHealth)",
        "XOM": "엑슨모빌 (Exxon Mobil)", "MA": "마스터카드 (Mastercard)", "JPM": "JP모건 체이스 (JPMorgan Chase)",
        "NVO": "노보 노디스크 (Novo Nordisk)", "PG": "프록터 앤 갬블 (P&G)", "ASML": "ASML",
        "ORCL": "오라클 (Oracle)", "COST": "코스트코 (Costco)", "HD": "홈디포 (Home Depot)",
        "BAC": "뱅크 오브 아메리카 (Bank of America)", "NFLX": "넷플릭스 (Netflix)", "AMD": "AMD",
        "QCOM": "퀄컴 (Qualcomm)", "TM": "토요타 (Toyota)", "ADBE": "어도비 (Adobe)",
        "SNDK": "샌디스크 (SanDisk)", "INTC": "인텔 (Intel)", "CSCO": "시스코 (Cisco)",
        "AMGN": "암젠 (Amgen)", "PEP": "펩시코 (PepsiCo)", "KO": "코카콜라 (Coca-Cola)"
    }

ticker_dict = get_default_companies()

# --- 캐싱을 활용한 데이터 로딩 함수 (서버 요청 최소화) ---
@st.cache_data(ttl=3600)  # 1시간 동안 결과 캐싱 (하루 동안 쓰려면 86400)
def load_stock_data(tickers, start, end):
    if not tickers:
        return None
    # 일괄 다운로드로 요청 횟수 단축
    return yf.download(tickers, start=start, end=end, group_by='ticker')

@st.cache_data(ttl=86400) # 발행주식수는 자주 변하지 않으므로 24시간 캐싱
def get_shares_outstanding(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info.get('sharesOutstanding', 1)
    except:
        return 1

@st.cache_data(ttl=3600)
def get_single_ticker_info(ticker):
    try:
        t = yf.Ticker(ticker)
        return t.info.get('longName', ticker)
    except:
        return None
# --------------------------------------------------

# 3. 사이드바 구성
st.sidebar.header("⚙️ 대시보드 설정")

# 종목 검색 및 추가 기능
st.sidebar.subheader("🔍 종목 추가하기")
search_ticker = st.sidebar.text_input("야후 파이낸스 티커 입력 (예: SQ, 기호 분리):").upper().strip()

if 'custom_tickers' not in st.session_state:
    st.session_state.custom_tickers = {}

if st.sidebar.button("종목 추가"):
    if search_ticker:
        if search_ticker in ticker_dict or search_ticker in st.session_state.custom_tickers:
            st.sidebar.info(f"💡 {search_ticker}는 이미 리스트에 존재합니다.")
        else:
            with st.spinner(f"{search_ticker} 정보를 확인하는 중..."):
                comp_name = get_single_ticker_info(search_ticker)
                if comp_name:
                    st.session_state.custom_tickers[search_ticker] = f"{comp_name} ({search_ticker}) *"
                    st.sidebar.success(f"✅ {search_ticker} 추가 완료!")
                else:
                    st.sidebar.error("❌ 유효하지 않은 티커이거나 요청이 제한되었습니다.")

full_options = {**ticker_dict, **st.session_state.custom_tickers}

selected_names = st.sidebar.multiselect(
    "시각화할 기업 선택:",
    options=list(full_options.values()),
    default=list(ticker_dict.values())[:5]
)

selected_tickers = [ticker for ticker, name in full_options.items() if name in selected_names]

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
    
    with st.spinner('Yahoo Finance에서 데이터를 안전하게 불러오는 중...'):
        data_download = load_stock_data(selected_tickers, start_date, end_date)

    if data_download is not None and not data_download.empty:
        df_price = pd.DataFrame(index=data_download.index)
        df_cap = pd.DataFrame(index=data_download.index)
        
        for ticker in selected_tickers:
            # 주가 데이터 추출
            if len(selected_tickers) == 1:
                close_data = data_download['Close'] if 'Close' in data_download.columns else None
            else:
                close_data = data_download[ticker]['Close'] if ticker in data_download.columns.levels[0] else None

            if close_data is not None:
                df_price[ticker] = close_data
                
                # 토글이 시가총액일 때만 주식수 가져오도록 최적화
                if "시가총액" in view_mode:
                    shares_out = get_shares_outstanding(ticker)
                    df_cap[ticker] = close_data * shares_out

        # 현재 모드에 맞는 데이터프레임 선택
        active_df = df_price if "주가" in view_mode else df_cap
        yaxis_label = "주가 ($)" if "주가" in view_mode else "시가총액 ($)"
        
        # 차트 그리기
        fig = go.Figure()
        for ticker in active_df.columns:
            display_name = full_options.get(ticker, ticker)
            valid_data = active_df[ticker].dropna()
            
            if not valid_data.empty:
                hover_format = f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>값: %{{y:,.2f}}<extra></extra>"
                fig.add_trace(go.Scatter(
                    x=valid_data.index, y=valid_data,
                    mode='lines', name=display_name,
                    hovertemplate=hover_format
                ))
            
        fig.update_layout(
            title=f"최근 1년 {view_mode} 변화 추이",
            xaxis_title="날짜", yaxis_title=yaxis_label,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=50, r=40, t=80, b=120), height=650
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("📊 상세 데이터 테이블 보기"):
            st.dataframe(active_df, use_container_width=True)
    else:
        st.error("⚠️ 야후 파이낸스 제한으로 데이터를 가져오지 못했습니다. 잠시 후 다시 시도해 주세요.")
