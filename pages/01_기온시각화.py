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
# 1. 데이터 로드 및 전처리 함수
# ---------------------------------------------------------
@st.cache_data
def load_data(file):
    df = None
    # 인코딩 시도 목록 (utf-8, cp949)
    encodings = ['utf-8', 'cp949']
    
    for enc in encodings:
        try:
            # 파일 객체(업로드된 파일)인 경우 읽기 위치를 맨 앞으로 초기화
            if hasattr(file, 'seek'):
                file.seek(0)
            
            df = pd.read_csv(file, encoding=enc)
            break # 성공하면 반복 중단
        except Exception:
            continue # 실패하면 다음 인코딩 시도
    
    if df is None:
        return None

    # 컬럼명 앞뒤 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 데이터 정제 (탭, 따옴표 제거)
    if '날짜' in df.columns:
        # 문자열로 변환 후 특수문자 제거
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        # 날짜 형식으로 변환
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        # 연도 컬럼 생성
        df['Year'] = df['날짜'].dt.year
        return df
    else:
        return None

# ---------------------------------------------------------
# 2. 메인 실행 로직 (파일 확인 -> 로드 -> 분석)
# ---------------------------------------------------------

file_name = 'test.py.csv'
df = None

# (1) 서버(같은 폴더)에 파일이 있는지 확인
if os.path.exists(file_name):
    df = load_data(file_name)

# (2) 파일이 없거나 로드되지 않았으면 -> 업로더 표시
if df is None:
    st.info("👋 서버에 데이터 파일이 없습니다. 아래 버튼을 눌러 파일을 업로드해주세요.")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=['csv'])
    
    if uploaded_file is not None:
        df = load_data(uploaded_file)

# (3) 데이터가 준비되면 분석 및 시각화 실행
if df is not None:
    if 'Year' in df.columns:
        # 데이터 로드 성공 메시지 (조용히 처리하거나 짧게 표시)
        if os.path.exists(file_name) and not hasattr(df, 'name'): # 로컬 파일인 경우
             st.success(f"📂 '{file_name}' 파일을 불러왔습니다.")
        else:
             st.success("📂 업로드된 파일을 불러왔습니다.")

        # 연도별 평균 기온 계산 (결측치 제외)
        df_yearly = df.groupby('Year')['평균기온(℃)'].mean().reset_index()
        
        # 화면 레이아웃 분할 (왼쪽: 그래프, 오른쪽: 설명)
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader("📈 연도별 기온 추세 그래프")
            
            # 캔버스 생성
            fig, ax = plt.subplots(figsize=(10, 5))
            
            # 산점도 (실제 데이터 - 회색 점)
            ax.scatter(df_yearly['Year'], df_yearly['평균기온(℃)'], color='gray', alpha=0.5, s=15, label='Yearly Avg Temp')
            
            # 추세선 (Trend Line) 계산 - 빨간 점선
            z = np.polyfit(df_yearly['Year'], df_yearly['평균기온(℃)'], 1)
            p = np.poly1d(z)
            
            # 추세선 그리기
            ax.plot(df_yearly['Year'], p(df_yearly['Year']), "r--", linewidth=2, label='Trend Line')
            
            # 그래프 꾸미기
            ax.set_title("Temperature Trend Over 110 Years", fontsize=15)
            ax.set_xlabel("Year")
            ax.set_ylabel("Average Temperature (C)")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.3)
            
            st.pyplot(fig)
        
        with col2:
            st.subheader("📊 분석 결과")
            
            # 기울기 및 변화량 계산
            slope = z[0]
            start_temp = p(df_yearly['Year'].min())
            end_temp = p(df_yearly['Year'].max())
            total_change = end_temp - start_temp
            
            st.metric("연간 기온 변화율", f"{slope:.4f} ℃/년")
            st.metric(f"총 기온 변화 ({len(df_yearly)}년)", f"{total_change:.2f} ℃")
            
            st.divider()
            
            if slope > 0:
                st.error("결론: 기온은 **상승**하고 있습니다.")
            elif slope < 0:
                st.info("결론: 기온은 하락하고 있습니다.")
            else:
                st.warning("결론: 뚜렷한 변화가 없습니다.")

        # 원본 데이터 확인 (접이식 메뉴)
        with st.expander("데이터 원본 확인하기"):
            st.dataframe(df.head(100))
            
    else:
        st.error("데이터 형식 오류: '날짜' 컬럼을 찾을 수 없습니다. CSV 파일을 확인해주세요.")
