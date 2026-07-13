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
            df_power['구간'] = pd.cut(df_power['기온(°C)'], bins=range(-20, 45, 5)).astype(str)
            chart_data = df_power.groupby('구간', sort=False)['전력수요(MWh)'].mean()
            st.bar_chart(chart_data)
        with c4:
            st.subheader("③ 월별 평균 전력수요")
            st.bar_chart(df_power.groupby('월')['전력수요(MWh)'].mean())
