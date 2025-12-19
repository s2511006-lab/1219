import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# 페이지 기본 설정
st.set_page_config(page_title="110년 기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")
st.markdown("데이터를 분석하여 실제로 기온이 상승하고 있는지 시각적으로 확인합니다.")

# 1. 데이터 로드 및 전처리 함수
@st.cache_data
def load_data(file_path):
    # 인코딩 문제 해결: utf-8을 우선 시도하고 실패 시 cp949 시도
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')
    
    # 컬럼명 앞뒤 공백 제거
    df.columns = df.columns.str.strip()
    
    # 날짜 데이터 정제 (탭 \t, 따옴표 " 제거)
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

# 2. 메인 로직
file_name = 'test.py.csv'

# 파일이 같은 폴더에 있는지 확인
if os.path.exists(file_name):
    try:
        df = load_data(file_name)
        
        if df is not None and 'Year' in df.columns:
            st.success(f"'{file_name}' 파일을 성공적으로 불러왔습니다.")
            
            # 연도별 평균 기온 계산 (결측치 제외)
            df_yearly = df.groupby('Year')['평균기온(℃)'].mean().reset_index()
            
            # 3. 데이터 분석 및 시각화
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("📈 연도별 기온 추세 그래프")
                
                # 캔버스 생성
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # 산점도 (실제 데이터)
                ax.scatter(df_yearly['Year'], df_yearly['평균기온(℃)'], color='gray', alpha=0.5, s=15, label='Yearly Avg Temp')
                
                # 추세선 (Trend Line) 계산 - 1차 함수 (y = ax + b)
                z = np.polyfit(df_yearly['Year'], df_yearly['평균기온(℃)'], 1)
                p = np.poly1d(z)
                
                # 추세선 그리기
                ax.plot(df_yearly['Year'], p(df_yearly['Year']), "r--", linewidth=2, label='Trend Line')
                
                # 그래프 꾸미기 (한글 깨짐 방지를 위해 영문 라벨 사용)
                ax.set_title("Temperature Trend Over 110 Years", fontsize=15)
                ax.set_xlabel("Year")
                ax.set_ylabel("Average Temperature (C)")
                ax.legend()
                ax.grid(True, linestyle='--', alpha=0.3)
                
                # 스트림릿에 그래프 표시
                st.pyplot(fig)
            
            with col2:
                st.subheader("📊 분석 결과")
                
                # 기울기 확인
                slope = z[0]
                
                st.metric("연간 기온 변화율", f"{slope:.4f} ℃/년")
                
                start_temp = p(df_yearly['Year'].min())
                end_temp = p(df_yearly['Year'].max())
                total_change = end_temp - start_temp
                
                st.metric(f"지난 {len(df_yearly)}년간 변화", f"{total_change:.2f} ℃")
                
                st.divider()
                
                if slope > 0:
                    st.error("결론: 기온은 **상승**하고 있습니다.")
                elif slope < 0:
                    st.info("결론: 기온은 하락하고 있습니다.")
                else:
                    st.warning("결론: 뚜렷한 변화가 없습니다.")

            # 데이터 원본 확인 (옵션)
            with st.expander("데이터 원본 확인하기"):
                st.dataframe(df.head(100))
                
        else:
            st.error("데이터 파일에서 '날짜' 컬럼을 찾을 수 없거나 형식이 올바르지 않습니다.")
            st.write("컬럼 목록:", df.columns if df is not None else "파일 읽기 실패")
            
    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
else:
    st.warning(f"'{file_name}' 파일을 찾을 수 없습니다. 같은 폴더에 파일이 있는지 확인해주세요.")
    # 파일이 없을 경우 업로드 옵션 제공
    uploaded_file = st.file_uploader("또는 CSV 파일을 직접 업로드하세요", type=['csv'])
    if uploaded_file is not None:
        # 업로드된 파일 처리 로직 (위와 동일한 함수 재사용 가능)
        # 여기서는 간단히 안내만 함
        st.info("파일이 업로드되었습니다. 코드를 재실행하거나 위 로직에 업로드 파일 처리를 연결해야 합니다.")
