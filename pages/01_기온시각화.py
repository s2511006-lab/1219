import streamlit as st
import pandas as pd
import numpy as np

# 페이지 기본 설정
st.set_page_config(page_title="기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")
st.markdown("별도의 라이브러리 설치 없이, 스트림릿 기본 기능만으로 기온 변화를 분석합니다.")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_and_clean_data():
    file_name = 'test.py.csv'
    
    # 데이터 읽기 (한글 인코딩 호환성)
    try:
        df = pd.read_csv(file_name, encoding='cp949')
    except:
        df = pd.read_csv(file_name, encoding='utf-8')
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 컬럼 데이터 정제 (탭, 따옴표 등 특수문자 제거)
    if '날짜' in df.columns:
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 연도 컬럼 생성
    df['년'] = df['날짜'].dt.year
    
    return df

try:
    df = load_and_clean_data()
    
    if df is not None and not df.empty:
        # 2. 연도별 평균 기온 계산
        df_yearly = df.groupby('년')['평균기온(℃)'].mean().reset_index()
        
        # 3. 추세선(Trend Line) 계산 (numpy 사용)
        # 1차 함수(직선) 계수 계산
        z = np.polyfit(df_yearly['년'], df_yearly['평균기온(℃)'], 1)
        p = np.poly1d(z)
        
        # 데이터프레임에 추세선 값 추가
        df_yearly['추세선'] = p(df_yearly['년'])
        
        # 차트를 그리기 위해 '년'을 인덱스로 설정
        chart_data = df_yearly.set_index('년')[['평균기온(℃)', '추세선']]
        
        # 4. 시각화 (스트림릿 내장 차트 사용 - 설치 불필요)
        st.subheader("📈 연도별 평균 기온 및 추세")
        st.line_chart(chart_data, color=["#bdc3c7", "#ff0000"]) 
        # 참고: 평균기온은 회색 계열, 추세선은 붉은색 계열로 표시됩니다 (테마에 따라 다를 수 있음)

        # 5. 분석 결과 요약
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

        with st.expander("원본 데이터 보기"):
            st.dataframe(df)

    else:
        st.error("데이터를 불러올 수 없습니다.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
