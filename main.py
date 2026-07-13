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

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="기온 분석 및 전력수요 예측 대시보드", layout="wide")
st.title("🏙️ 서울-양평 기온 비교(열섬현상) 및 전력수요 분석")

# 파일 존재 여부 먼저 체크
required_files = ["서울_기온.csv", "양평_기온.csv", "전력수요.csv"]
missing_files = [f for f in required_files if not os.path.exists(f)]

if missing_files:
    st.error(f"❌ 필요한 데이터 파일이 없습니다: {', '.join(missing_files)}")
    st.info("웹앱 스크립트(main.py)와 같은 폴더에 csv 파일들을 넣어주세요.")
else:
    # 2. 데이터 로드 함수 (캐싱 적용)
    @st.cache_data
    def load_data():
        # 파일 읽기 (cp949 인코딩 적용)
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        power = pd.read_csv("전력수요.csv", encoding="cp949")
        
        # 일시 컬럼을 datetime 형식으로 변환
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        power['일시'] = pd.to_datetime(power['일시'])
        
        # 월, 시 정보 추출
        seoul['월'] = seoul['일시'].dt.month
        seoul['시'] = seoul['일시'].dt.hour
        
        return seoul, yangpyeong, power

    # 데이터 가져오기
    seoul_df, yang_df, power_df = load_data()
    
    # 데이터 병합
    # [탭1용] 서울-양평 기온 데이터 병합
    df_temp = pd.merge(
        seoul_df[['일시', '월', '시', '기온(°C)']], 
        yang_df[['일시', '기온(°C)']], 
        on='일시', 
        suffixes=('_서울', '_양평')
    )
    df_temp['기온차(서울-양평)'] = df_temp['기온(°C)_서울'] - df_temp['기온(°C)_양평']
    
    # [탭2용] 서울 기온과 전력수요 데이터 병합
    df_power = pd.merge(
        seoul_df[['일시', '월', '기온(°C)']], 
        power_df[['일시', '전력수요(MWh)']], 
        on='일시'
    )
    
    # -------------------------------------------------------------------------
    # 탭 구성
    # -------------------------------------------------------------------------
    tab1, tab2 = st.tabs(["🏙️ 탭1: 열섬 분석", "⚡ 탭2: 전력 연결"])
    
    # =========================================================================
    # [탭1: 열섬 분석]
    # =========================================================================
    with tab1:
        st.header("도시 열섬현상(Urban Heat Island) 분석")
        st.markdown("대도시(서울)와 근교 지역(양평)의 기온 차이를 시각화하여 열섬현상을 살펴봅니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        line_data = df_temp.set_index('일시')[['기온(°C)_서울', '기온(°C)_양평']]
        line_data.columns = ['서울 기온 (°C)', '양평 기온 (°C)']
        st.line_chart(line_data)
        
        # 레이아웃 분할
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각별 평균 기온차 (막대그래프)
            st.subheader("② 시각별 평균 기온차 (서울 - 양평)")
            hour_diff = df_temp.groupby('시')['기온차(서울-양평)'].mean()
            st.bar_chart(hour_diff)
            st.caption("💡 야간 및 대기 복사냉각 시간대에 서울과 양평의 기온차가 크게 벌어지는 경향을 확인할 수 있습니다.")
            
        with col2:
            # ③ 월별 평균 기온차 (막대그래프)
            st.subheader("③ 월별 평균 기온차 (서울 - 양평)")
            month_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(month_diff)
            st.caption("💡 계절에 따른 일사량과 기상 변화가 열섬현상 강도에 미치는 영향을 보여줍니다.")

    # =========================================================================
    # [탭2: 전력 연결]
    # =========================================================================
    with tab2:
        st.header("기온과 전력수요의 관계 분석")
        st.markdown("서울의 기온 변화가 실제 전력수요에 어떠한 영향을 미치는지 분석합니다.")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온과 전력수요의 산점도 (Scatter Plot)")
        st.scatter_chart(data=df_power, x='기온(°C)', y='전력수요(MWh)')
        
        # 레이아웃 분할
        col3, col4 = st.columns(2)
        
        with col3:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 기온 구간별 평균 전력수요")
            df_power['기온구간'] = pd.cut(df_power['기온(°C)'], bins=range(-20, 45, 5))
            df_power['기온구간_표시'] = df_power['기온구간'].astype(str)
            group_bin = df_power.groupby('기온구간_표시', sort=False)['전력수요(MWh)'].mean()
            
            bin_order = [str(b) for b in pd.cut(df_power['기온(°C)'], bins=range(-20, 45, 5)).unique().dropna().sort_values()]
            group_bin = group_bin.reindex(bin_order).dropna()
            
            st.bar_chart(group_bin)
            st.caption("💡 기온 구간별 평균치를 통해 냉·난방 임계 기온 지점을 명확히 파악할 수 있습니다.")
            
        with col4:
            # ③ 월별 평균 전력수요 (막대그래프)
            st.subheader("③ 월별 평균 전력수요")
            month_power = df_power.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(month_power)
            st.caption("💡 여름철(7~8월) 냉방 수요와 겨울철(12~1월) 난방 수요의 크기를 비교해볼 수 있습니다.")
