import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 페이지 기본 설정
st.set_page_config(page_title="지난 110년 기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")
st.markdown("업로드된 기상 데이터를 바탕으로 실제로 기온이 상승했는지 분석합니다.")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_and_clean_data():
    # 데이터 읽기 (한글 인코딩 cp949 또는 euc-kr 사용)
    try:
        df = pd.read_csv('test.py.csv', encoding='cp949')
    except:
        df = pd.read_csv('test.py.csv', encoding='utf-8')
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 컬럼 데이터 정제 (탭, 따옴표 제거)
    if '날짜' in df.columns:
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
    
    # 연도 컬럼 생성
    df['년'] = df['날짜'].dt.year
    
    return df

# 데이터 불러오기
try:
    df = load_and_clean_data()
    
    # 데이터가 정상적으로 로드되었는지 확인
    if df is not None and not df.empty:
        st.success("데이터를 성공적으로 불러왔습니다.")
        
        # 2. 연도별 평균 기온 계산
        # 결측치가 있을 수 있으므로 연도별로 그룹화하여 평균 계산
        df_yearly = df.groupby('년')['평균기온(℃)'].mean().reset_index()
        
        # 3. 시각화 (matplotlib 사용)
        st.subheader("📈 연도별 평균 기온 추세")
        
        # 그래프 그리기
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # 실제 데이터 (회색 점선)
        ax.plot(df_yearly['년'], df_yearly['평균기온(℃)'], color='#bdc3c7', label='Yearly Avg Temp', alpha=0.6)
        ax.scatter(df_yearly['년'], df_yearly['평균기온(℃)'], color='#bdc3c7', s=10, alpha=0.6)
        
        # 추세선 (Trend Line) 계산 - 1차 함수 (y = ax + b)
        z = np.polyfit(df_yearly['년'], df_yearly['평균기온(℃)'], 1)
        p = np.poly1d(z)
        
        # 추세선 그리기 (빨간 실선)
        ax.plot(df_yearly['년'], p(df_yearly['년']), "r--", linewidth=2, label='Trend Line')
        
        # 그래프 스타일 설정 (한글 폰트 문제 방지를 위해 영문 라벨 사용)
        ax.set_xlabel("Year")
        ax.set_ylabel("Average Temperature (C)")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        
        st.pyplot(fig)

        # 4. 분석 결과 요약
        st.subheader("📊 분석 결과 요약")
        
        # 시작 연도와 마지막 연도 데이터 비교
        first_10_years = df_yearly.head(10)['평균기온(℃)'].mean()
        last_10_years = df_yearly.tail(10)['평균기온(℃)'].mean()
        diff = last_10_years - first_10_years
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("초기 10년 평균 기온", f"{first_10_years:.2f} ℃")
        with col2:
            st.metric("최근 10년 평균 기온", f"{last_10_years:.2f} ℃")
        with col3:
            st.metric("기온 상승폭", f"{diff:+.2f} ℃", delta_color="inverse")
            
        st.divider()
        
        # 결론 도출
        slope = z[0] # 기울기
        st.markdown(f"### 💡 결론")
        if slope > 0:
            st.warning(f"데이터 분석 결과, 지난 110여 년간 기온은 **상승하는 추세**를 보입니다. (연간 약 {slope:.4f}℃ 상승)")
        elif slope < 0:
            st.info("데이터 분석 결과, 기온은 하락하는 추세를 보입니다.")
        else:
            st.markdown("기온의 뚜렷한 변화 추세가 보이지 않습니다.")

        # 데이터 미리보기 (디버깅용)
        with st.expander("원본 데이터 확인하기"):
            st.dataframe(df)

    else:
        st.error("데이터에 문제가 있어 처리할 수 없습니다.")

except Exception as e:
    st.error(f"오류가 발생했습니다: {e}")
    st.markdown("데이터 파일 이름이 `test.py.csv`가 맞는지 확인해주세요.")
