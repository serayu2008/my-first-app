import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="서울-양평 도시 열섬현상 분석", layout="wide")
st.title("서울 vs 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
본 웹앱은 대도시인 **서울**과 근교 지역인 **양평**의 2025년 시간별 기온 데이터를 비교하여, 
도시화로 인해 발생하는 도시 열섬현상을 시각적으로 확인하기 위해 제작되었습니다.
""")

# 2. 데이터 로드 함수 (캐싱 적용으로 속도 향상)
@st.cache_data
def load_data():
    # 파일 읽기 (요청하신 cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
    
    # 일시 컬럼을 datetime 형식으로 변환
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
    
    # 분석에 필요한 월, 시 정보 추출
    seoul['월'] = seoul['일시'].dt.month
    seoul['시'] = seoul['일시'].dt.hour
    yangpyeong['월'] = yangpyeong['일시'].dt.month
    yangpyeong['시'] = yangpyeong['일시'].dt.hour
    
    return seoul, yangpyeong

try:
    seoul_df, yang_df = load_data()
    
    # 두 데이터프레임을 일시 기준으로 병합하여 차이 계산
    df = pd.merge(
        seoul_df[['일시', '월', '시', '기온(°C)']], 
        yang_df[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    # 기온차 (서울 - 양평) 계산
    df['기온차(서울-양평)'] = df['기온(°C)_서울'] - df['기온(°C)_양평']

    # =========================================================================
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    # =========================================================================
    st.subheader("① 1년간 두 지역의 기온 변화")
    st.markdown("2025년 1년 동안 서울과 양평의 전체적인 기온 흐름을 보여줍니다.")
    
    # 선그래프를 위한 데이터 가공 (일시를 인덱스로 지정)
    line_data = df.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
    line_data.columns = ['서울 기온 (°C)', '양평 기온 (°C)']
    
    # streamlit 내장 선그래프 실행
    st.line_chart(line_data)

    # 레이아웃 분할 (시각별, 월별 막대그래프를 좌우로 배치)
    col1, col2 = st.columns(2)

    # =========================================================================
    # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
    # =========================================================================
    with col1:
        st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
        st.markdown("하루 중 어느 시간대에 도시 열섬현상이 더 뚜렷한지 확인합니다.")
        
        # 시각별 평균 기온차 계산 및 막대그래프 시각화
        hour_diff = df.groupby('시')['기온차(서울-양평)'].mean()
        st.bar_chart(hour_diff)
        st.caption("💡 요약: 대개 인공열 축적이 많은 야간 및 새벽 시간대에 대도시(서울)와 교외(양평)의 기온차가 두드러집니다.")

    # =========================================================================
    # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
    # =========================================================================
    with col2:
        st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
        st.markdown("계절 변화에 따른 도시 열섬현상의 강도를 확인합니다.")
        
        # 월별 평균 기온차 계산 및 막대그래프 시각화
        month_diff = df.groupby('월')['기온차(서울-양평)'].mean()
        st.bar_chart(month_diff)
        st.caption("💡 요약: 계절별 기상 조건과 일사량에 따라 월별 평균 기온차가 다르게 나타납니다.")

    # 추가 피처: 데이터 요약 대시보드 메트릭
    st.markdown("---")
    st.subheader("📊 2025년 전체 요약 지표")
    m1, m2, m3 = st.columns(3)
    m1.metric("연평균 서울 기온", f"{df['기온(°C)_서울'].mean():.2f} °C")


import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="기온 및 전력수요 분석", layout="wide")
st.title("🏙️ 서울-양평 기온 비교 및 전력수요 분석")

# 1. 파일 존재 여부 확인
files = ["서울_기온.csv", "양평_기온.csv", "전력수요.csv"]
missing = [f for f in files if not os.path.exists(f)]

if missing:
    st.error(f"❌ 데이터 파일 누락: {', '.join(missing)}")
    st.info("웹앱 스크립트와 같은 폴더에 CSV 파일들을 넣어주세요.")
else:
    # 2. 데이터 불러오기 (cp949 인코딩 적용)
    seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
    yang = pd.read_csv("양평_기온.csv", encoding="cp949")
    power = pd.read_csv("전력수요.csv", encoding="cp949")
    
    # 3. 데이터 전처리 (시간축 통일 및 변수 생성)
    seoul['일시'] = pd.to_datetime(seoul['일시'])
    yang['일시'] = pd.to_datetime(yang['일시'])
    power['일시'] = pd.to_datetime(power['일시'])
    
    seoul['월'] = seoul['일시'].dt.month
    seoul['시'] = seoul['일시'].dt.hour
    
    # 데이터 병합
    df_temp = pd.merge(seoul[['일시', '월', '시', '기온(°C)']], yang[['일시', '기온(°C)']], on='일시', suffixes=('_서울', '_양평'))
    df_temp['기온차(서울-양평)'] = df_temp['기온(°C)_서울'] - df_temp['기온(°C)_양평']
    
    df_power = pd.merge(seoul[['일시', '월', '기온(°C)']], power[['일시', '전력수요(MWh)']], on='일시')
    
    # 4. 탭 구성 (st.tabs)
    t1, t2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # -------------------------------------------------------------------------
    # [탭1: 열섬 분석]
    # -------------------------------------------------------------------------
    with t1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        
        st.subheader("① 1년간 두 지역 기온 변화")
        line_df = df_temp.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
        line_df.columns = ['서울 기온', '양평 기온']
        st.line_chart(line_df)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            st.bar_chart(df_temp.groupby('시')['기온차(서울-양평)'].mean())
        with c2:
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            st.bar_chart(df_temp.groupby('월')['기온차(서울-양평)'].mean())
            
    # -------------------------------------------------------------------------
    # [탭2: 전력 연결]
    # -------------------------------------------------------------------------
    with t2:
        st.header("기온과 전력수요의 관계 분석")
        
        st.subheader("① 기온과 전력수요 산점도")
        st.scatter_chart(data=df_power, x='기온(°C)', y='전력수요(MWh)')
        
        c3, c4 = st.columns(2)
        with c3:
            st.subheader("② 기온 구간별 평균 전력수요")
            # 5도 단위로 구간을 나누고 정렬 순서 유지를 위해 카테고리형 활용
            df_power['구간'] = pd.cut(df_power['기온(°C)'], bins=range(-20, 45, 5)).astype(str)
            chart_data = df_power.groupby('구간', sort=False)['전력수요(MWh)'].mean()
            st.bar_chart(chart_data)
        with c4:
            st.subheader("③ 월별 평균 전력수요")
            st.bar_chart(df_power.groupby('월')['전력수요(MWh)'].mean())
