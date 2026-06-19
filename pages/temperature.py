import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 기본 설정
st.set_page_config(page_title="120년 기온 데이터 분석기", layout="wide", page_icon="🌡️")

st.title("🌡️ 1907 ~ 2026 역사적인 기온 데이터 분석 대시보드")
st.markdown("깃허브에 업로드한 기상 데이터를 바탕으로 구축된 인터랙티브 웹 앱입니다.")

# 2. 데이터 로드 및 전처리 함수 (캐싱을 통해 속도 최적화)
@st.cache_data
def load_data():
    # 파일 로드 (공백 및 인코딩 주의)
    df = pd.read_csv('ta_20260619190504.csv', encoding='utf-8')
    
    # 영문/깔끔한 컬럼명으로 변경
    df.columns = ['날짜', '지점', '평균기온', '최저기온', '최고기온']
    
    # 중요: 날짜 데이터 앞뒤의 공백 및 '\t'(탭) 문자 제거 후 datetime 변환
    df['날짜'] = df['날짜'].str.strip()
    df['날짜'] = pd.to_datetime(df['날짜'])
    
    # 분석을 위한 연도, 월, 일, 일교차 변수 파생
    df['연도'] = df['날짜'].dt.year
    df['월'] = df['날짜'].dt.month
    df['일'] = df['날짜'].dt.day
    df['일교차'] = df['최고기온'] - df['최저기온']
    
    # 역사적 공백기(예: 전쟁 시기 등)로 인한 기온 결측치는 선형 보간법으로 처리
    df['평균기온'] = df['평균기온'].interpolate()
    df['최저기온'] = df['최저기온'].interpolate()
    df['최고기온'] = df['최고기온'].interpolate()
    
    return df

try:
    df = load_data()
    
    # 사이드바 메뉴 메뉴 구성
    st.sidebar.header("📍 메뉴 선택")
    menu = st.sidebar.radio("원하는 분석 기능을 선택하세요:", ["📈 기후 변화 트렌드", "📅 역대 오늘 날씨 조회", "🏆 기온 기네스북"])
    
    # ----------------------------------------------------
    # 메뉴 1: 기후 변화 트렌드
    # ----------------------------------------------------
    if menu == "📈 기후 변화 트렌드":
        st.header("📈 장기 기후 변화 및 온난화 추세")
        
        # 연도 범위 슬라이더 위젯
        year_range = st.sidebar.slider(
            "조회할 연도 범위를 지정하세요:",
            int(df['연도'].min()), int(df['연도'].max()),
            (int(df['연도'].min()), int(df['연도'].max()))
        )
        
        # 선택된 연도로 데이터 필터링
        filtered_df = df[(df['연도'] >= year_range[0]) & (df['연도'] <= year_range[1])]
        
        # 연도별 평균 기온 계산
        annual_df = filtered_df.groupby('연도')['평균기온'].mean().reset_index()
        
        # 대시보드 상단 지표(st.metric) 배치
        col1, col2 = st.columns(2)
        start_temp = annual_df.iloc[0]['평균기온']
        end_temp = annual_df.iloc[-1]['평균기온']
        temp_diff = end_temp - start_temp
        
        col1.metric(f"{year_range[0]}년 무렵 평균 기온", f"{start_temp:.2f} °C")
        col2.metric(f"{year_range[1]}년 무렵 평균 기온", f"{end_temp:.2f} °C", delta=f"{temp_diff:+.2f} °C")
        
        # Plotly 대화형 라인 차트 시각화
        fig = px.line(annual_df, x='연도', y='평균기온', 
                      title=f"{year_range[0]}년 ~ {year_range[1]}년 연평균 기온 변화 추이 (지구온난화 지표)")
        fig.update_traces(line_color='crimson')
        st.plotly_chart(fig, use_container_width=True)
        
    # ----------------------------------------------------
    # 메뉴 2: 역대 오늘 날씨 조회
    # ----------------------------------------------------
    elif menu == "📅 역대 오늘 날씨 조회":
        st.header("📅 역사 속 '오늘'은 얼마나 더웠거나 추웠을까?")
        
        # 월/일 선택 셀렉트박스
        col_m, col_d = st.columns(2)
        with col_m:
            selected_month = st.selectbox("월을 선택하세요:", list(range(1, 13)), index=5)  # 기본값 6월
        with col_d:
            selected_day = st.selectbox("일을 선택하세요:", list(range(1, 32)), index=18)   # 기본값 19일
            
        day_df = df[(df['월'] == selected_month) & (df['일'] == selected_day)]
        
        # 그래프 플로팅
        fig_day = px.line(day_df, x='연도', y=['평균기온', '최저기온', '최고기온'],
                          title=f"1907년~2026년 역대 {selected_month}월 {selected_day}일 기온 역사 추이")
        st.plotly_chart(fig_day, use_container_width=True)
        
        # 간단 요약 통계 정보
        max_hot_row = day_df.loc[day_df['최고기온'].idxmax()]
        min_cold_row = day_df.loc[day_df['최저기온'].idxmin()]
        
        st.info(f"💡 **{selected_month}월 {selected_day}일 흥미로운 기록:**\n"
                f"- 역사상 가장 더웠던 날: **{max_hot_row['연도']}년** (최고 기온 {max_hot_row['최고기온']} °C)\n"
                f"- 역사상 가장 추웠던 날: **{min_cold_row['연도']}년** (최저 기온 {min_cold_row['최저기온']} °C)")

    # ----------------------------------------------------
    # 메뉴 3: 기온 기네스북
    # ----------------------------------------------------
    elif menu == "🏆 기온 기네스북":
        st.header("🏆 120년간의 극단적 기온 기네스북")
        st.write("데이터 전체 기간 중 가장 극단적인 수치를 기록한 날짜들입니다.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("🔥 역대 최고 기온 TOP 5")
            top_hot = df.sort_values(by='최고기온', ascending=False).head(5)[['날짜', '최고기온']]
            top_hot['날짜'] = top_hot['날짜'].dt.strftime('%Y-%m-%d')
            st.dataframe(top_hot, use_container_width=True)
            
        with col2:
            st.subheader("❄️ 역대 최저 기온 TOP 5")
            top_cold = df.sort_values(by='최저기온', ascending=True).head(5)[['날짜', '최저기온']]
            top_cold['날짜'] = top_cold['날짜'].dt.strftime('%Y-%m-%d')
            st.dataframe(top_cold, use_container_width=True)
            
        with col3:
            st.subheader("🔄 역대 최대 일교차 TOP 5")
            top_gap = df.sort_values(by='일교차', ascending=False).head(5)[['날짜', '일교차']]
            top_gap['날짜'] = top_gap['날짜'].dt.strftime('%Y-%m-%d')
            st.dataframe(top_gap, use_container_width=True)

except Exception as e:
    st.error(f"데이터를 읽거나 처리하는 과정에서 오류가 발생했습니다. 파일명과 포맷을 확인해 주세요. 오류 내용: {e}")
