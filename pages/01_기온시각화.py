import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 페이지 기본 설정
st.set_page_config(page_title="110년 기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")
st.markdown("데이터를 분석하여 실제로 기온이 상승하고 있는지 시각적으로 확인합니다.")

# ---------------------------------------------------------
# 1. 데이터 로드 및 전처리 함수 (청소 기능 강화)
# ---------------------------------------------------------
@st.cache_data
def load_data(file):
    df = None
    encodings = ['utf-8', 'cp949']
    
    for enc in encodings:
        try:
            if hasattr(file, 'seek'):
                file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            break
        except Exception:
            continue
    
    if df is None:
        return None

    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # [수정됨] 데이터 청소: 날짜 처리
    if '날짜' in df.columns:
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce') # 날짜 아닌 건 NaT로 변환
        df['Year'] = df['날짜'].dt.year
    else:
        return None

    # [추가됨] 데이터 청소: 기온 데이터 숫자 변환 및 결측치 제거
    if '평균기온(℃)' in df.columns:
        # 숫자가 아닌 것(문자, 공백 등)을 강제로 NaN으로 만듦
        df['평균기온(℃)'] = pd.to_numeric(df['평균기온(℃)'], errors='coerce')
        # 기온이나 연도가 비어있는 행을 싹 지움 (이게 nan 해결 핵심!)
        df = df.dropna(subset=['평균기온(℃)', 'Year'])
        
    return df

# ---------------------------------------------------------
# 2. 메인 실행 로직
# ---------------------------------------------------------

file_name = 'test.py.csv'
df = None

# (1) 파일 확인 및 로드
if os.path.exists(file_name):
    df = load_data(file_name)

# (2) 파일 없으면 업로더 표시
if df is None:
    st.info("👋 서버에 데이터 파일이 없습니다. 아래 버튼을 눌러 파일을 업로드해주세요.")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=['csv'])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)

# (3) 분석 및 시각화
if df is not None:
    if 'Year' in df.columns and '평균기온(℃)' in df.columns:
        # 메시지 처리
        if os.path.exists(file_name) and not hasattr(df, 'name'):
             st.success(f"📂 '{file_name}' 로드 완료")
        else:
             st.success("📂 데이터 로드 완료")

        # 연도별 평균 계산
        df_yearly = df.groupby('Year')['평균기온(℃)'].mean().reset_index()
        
        # 데이터가 너무 적으면 계산 불가하므로 체크
        if len(df_yearly) > 1:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("📈 연도별 기온 추세 그래프")
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # 산점도
                ax.scatter(df_yearly['Year'], df_yearly['평균기온(℃)'], color='gray', alpha=0.5, s=15)
                
                # 추세선 계산 (이제 nan이 안 뜰 겁니다)
                z = np.polyfit(df_yearly['Year'], df_yearly['평균기온(℃)'], 1)
                p = np.poly1d(z)
                
                ax.plot(df_yearly['Year'], p(df_yearly['Year']), "r--", linewidth=2, label='Trend Line')
                
                ax.set_title("Temperature Trend", fontsize=15)
                ax.set_xlabel("Year")
                ax.set_ylabel("Average Temp (C)")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.3)
                st.pyplot(fig)
            
            with col2:
                st.subheader("📊 분석 결과")
                slope = z[0]
                total_change = p(df_yearly['Year'].max()) - p(df_yearly['Year'].min())
                
                st.metric("연간 기온 변화율", f"{slope:.4f} ℃/년")
                st.metric("총 기온 변화", f"{total_change:.2f} ℃")
                st.divider()
                
                if slope > 0:
                    st.error("결론: 기온 상승 중")
                else:
                    st.info("결론: 기온 하락 또는 유지")
        else:
            st.warning("데이터가 너무 적어서 추세선을 그릴 수 없습니다.")

        with st.expander("데이터 원본 확인하기"):
            st.dataframe(df.head(100))
            
    else:
        st.error("필수 컬럼('날짜', '평균기온(℃)')이 없습니다.")
