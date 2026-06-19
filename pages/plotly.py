import streamlit as st
import yfinance as yf
import datetime
import plotly.graph_objects as go
import pandas as pd

# 1. 페이지 설정
st.set_page_config(
    page_title="글로벌 시가총액 TOP 10 주식 대시보드",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 글로벌 시가총액 TOP 10 주식 대시보드")
st.markdown("최근 1년 동안의 주가 변화를 Plotly 차트로 확인하세요. (데이터 출처: Yahoo Finance)")

# 2. 글로벌 시가총액 Top 10 기업 정보 (티커 및 기업명)
# * 시가총액 순위는 시점에 따라 변동될 수 있습니다.
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
    "TSLA": "테슬라 (Tesla)"
}

# 3. 사이드바 구성
st.sidebar.header("⚙️ 설정")

# 멀티 셀렉트를 이용한 기업 선택 (기본값은 전체 선택)
selected_names = st.sidebar.multiselect(
    "시각화할 기업을 선택하세요:",
    options=list(ticker_dict.values()),
    default=list(ticker_dict.values())
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
            # 데이터 일괄 다운로드
            df = yf.download(selected_tickers, start=start_date, end=end_date)['Close']
            
            # 단일 티커 선택 시 DataFrame 구조가 Series로 바뀌는 것 방지
            if len(selected_tickers) == 1:
                df = pd.DataFrame(df, columns=selected_tickers)
                
        except Exception as e:
            st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
            df = None

    if df is not None and not df.empty:
        # Plotly를 이용한 인터랙티브 선 그래프 생성
        fig = go.Figure()
        
        for ticker in df.columns:
            # 티커에 매칭되는 한국어 이름 가져오기
            display_name = ticker_dict.get(ticker, ticker)
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[ticker],
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
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=40, r=40, t=80, b=40),
            height=600
        )
        
        # Streamlit에 차트 출력
        st.plotly_chart(fig, use_container_width=True)
        
        # 데이터프레임 미리보기 (선택 사항)
        with st.expander("📊 원본 데이터 보기"):
            st.dataframe(df, use_container_width=True)
            
    else:
        st.error("불러온 데이터가 비어 있습니다. 잠시 후 다시 시도해 주세요.")
