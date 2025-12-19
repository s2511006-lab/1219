import streamlit as st
import pandas as pd
import numpy as np
import os

# 페이지 기본 설정
st.set_page_config(page_title="기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def process_data(file):
    # 데이터 읽기 (한글 인코딩 호환성)
    try:
        df = pd.read_csv(file, encoding='cp949')
    except:
        df = pd.read_csv(file, encoding='utf-8')
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 컬럼 데이터 정제 (탭, 따옴표 등 특수문자 제거)
    if '날짜' in df.columns:
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 연도 컬럼 생성
    df['년'] = df['날짜'].dt.year
    
    return df

# 2. 파일 불러오기 로직 (자동 감지 or 직접 업로드)
file_path = 'test.py.csv'
df = None

# Case 1: 서버에 파일이 이미 있는 경우 (GitHub에 같이 올린 경우)
if os.path.exists(file_path):
    df = process_data(file_path)
# Case 2: 파일이 없는 경우 -> 업로더 표시
else:
    st.info("⚠️ 서버에서 'test.py.csv' 파일을 찾지 못했습니다. 아래에 파일을 업로드해주세요.")
    uploaded_file = st.file_uploader("데이터 파일 업로드 (CSV)", type=['csv'])
    
    if uploaded_file is not None:
        df = process_data(uploaded_file)

# 3. 데이터 분석 및 시각화 실행
if df is not None and not df.empty:
    st.success("데이터 로드 성공!")
    
    # 연도별 평균 기온 계산
    df_yearly = df.groupby('년')['평균기온(℃)'].mean().reset_index()
    
    # 추세선(Trend Line) 계산
    if len(df_yearly) > 1:
        z = np.polyfit(df_yearly['년'], df_yearly['평균기온(℃)'], 1)
        p = np.poly1d(z)
        df_yearly['추세선'] = p(df_yearly['년'])
        
        # 차트 데이터 준비
        chart_data = df_yearly.set_index('년')[['평균기온(℃)', '추세선']]
        
        # 시각화 (스트림릿 내장 차트)
        st.subheader("📈 연도별 평균 기온 및 추세")
        st.line_chart(chart_data, color=["#bdc3c7", "#ff0000"]) 
        
        # 분석 결과 요약
        st.subheader("📊 분석 결과 요약")
        
        first_10_years = df_yearly.head(10)['평균기온(℃)'].mean()
        last_10_years = df_yearly.tail(10)['평균기온(℃)'].mean()
        diff = last_10_years - first_10_years
        
        col1, col2, col3 = st.columns(3)
        col1.metric("초기 10년 평균", f"{first_10_years:.2f} ℃")
        col2.metric("최근 10년 평균", f"{last_10_years:.2f} ℃")
        col3.metric("상승폭", f"{diff:+.2f} ℃", delta_color="inverse")
        
        st.divider()
        
        # 결론 텍스트
        slope = z[0]
        if slope > 0:
            st.warning(f"📉 결론: 지난 110여 년간 기온은 연평균 약 {slope:.4f}℃씩 **상승**하고 있습니다.")
        else:
            st.info("📉 결론: 기온 상승 추세가 뚜렷하지 않거나 하락했습니다.")
            
    else:
        st.warning("데이터가 부족하여 추세를 분석할 수 없습니다.")

    with st.expander("원본 데이터 보기"):
        st.dataframe(df)

elif df is None and not os.path.exists(file_path):
    # 파일이 없고 업로드도 안 된 상태면 아무것도 표시하지 않음 (업로더만 대기)
    pass
else:
    st.error("데이터를 처리하는 중 문제가 발생했습니다.")
