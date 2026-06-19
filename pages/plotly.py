import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 시가총액 TOP 30 주식 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 글로벌 시가총액 TOP 30 주식 대시보드")
st.markdown("최근 1년 동안의 주가 변화를 Plotly 차트로 확인하세요. (데이터 출처: Yahoo Finance)")

# 2. 글로벌 시가총액 Top 30 기업 정보 (티커 및 기업명)
# * 시가총액 순위는 시장 상황에 따라 변동될 수 있습니다.
ticker_dict = {
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
    "MRK": "머크 (Merck)",
    "AMD": "AMD",
    "CVX": "셰브론 (Chevron)",
    "KO": "코카콜라 (Coca-Cola)",
    "PEP": "펩시코 (PepsiCo)"
}

# 3. 사이드바 구성
st.sidebar.header("⚙️ 설정")

# 초기 화면 복잡도를 줄이기 위해 기본값은 Top 5만 선택되도록 설정 (원하는 대로 전체 선택 변경 가능)
default_selection = list(ticker_dict.values())[:5]

selected_names = st.sidebar.multiselect(
    "시각화할 기업을 선택하세요 (다중 선택 가능):",
    options=list(ticker_dict.values()),
    default=default_selection
)

# 선택된 기업의 티커 리스트 추출
selected_tickers = [ticker for ticker, name in ticker_dict.items() if name in selected_names]

# 4. 데이터 로드 및 시각화
if not selected_tickers:
    st.warning("⚠️ 최소 한 개 이상의 기업을 선택해 주세요.")
else:
    # 최근 1년 기간 설정
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    with st.spinner('Yahoo Finance에서 데이터를 불러오는 중입니다...'):
        try:
            # yfinance 최신 버전의 Multi-index 반환 형태 대응을 위해 group_by='ticker' 설정
            data_download = yf.download(selected_tickers, start=start_date, end=end_date, group_by='ticker')
            
            # 주가 데이터프레임 빌드
            df = pd.DataFrame(index=data_download.index)
            for ticker in selected_tickers:
                if len(selected_tickers) == 1:
                    # 단일 티커일 경우 데이터 구조 처리
                    if 'Close' in data_download.columns:
                        df[ticker] = data_download['Close']
                else:
                    if ticker in data_download.columns.levels[0]:
                        df[ticker] = data_download[ticker]['Close']
                        
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
            df = None

    if df is not None and not df.empty:
        # Plotly를 이용한 인터랙티브 선 그래프 생성
        fig = go.Figure()
        
        for ticker in df.columns:
            display_name = ticker_dict.get(ticker, ticker)
            
            # 데이터에 NaN 값이 있을 수 있으므로 dropna()로 안정적인 라인 렌더링
            valid_data = df[ticker].dropna()
            
            if not valid_data.empty:
                fig.add_trace(go.Scatter(
                    x=valid_data.index,
                    y=valid_data,
                    mode='lines',
                    name=display_name,
                    hovertemplate=f"<b>{display_name}</b><br>날짜: %{{x|%Y-%m-%d}}<br>주가: $%{{y:.2f}}<extra></extra>"
                ))
            
        fig.update_layout(
            title="최근 1년 주가 변화 추이 (종가 기준, USD)",
            xaxis_title="날짜",
            yaxis_title="주가 ($)",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.15, # 기업 수가 많아 하단 범례 배치 조절
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=40, r=40, t=80, b=100),
            height=650
        )
        
        # Streamlit에 차트 출력
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터프레임 미리보기
        with st.expander("📊 원본 데이터 보기"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.error("불러온 데이터가 없거나 형식이 올바르지 않습니다.")
