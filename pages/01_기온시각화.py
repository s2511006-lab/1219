import streamlit as st
import pandas as pd
import numpy as np
import os

# 페이지 설정
st.set_page_config(page_title="기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석")

# 1. 데이터 로드 및 전처리 함수 (안정성 강화)
@st.cache_data
def process_data(file):
    df = None
    # 한글 인코딩 문제 해결을 위한 시도
    encodings = ['cp949', 'utf-8', 'euc-kr']
    
    for enc in encodings:
        try:
            # ★ 핵심 수정: 파일을 다시 읽을 때마다 커서를 맨 앞으로 초기화
            if hasattr(file, 'seek'):
                file.seek(0)
            
            df = pd.read_csv(file, encoding=enc)
            
            # 읽기에 성공하면 루프 탈출
            break
        except Exception:
            continue
            
    if df is None:
        return None
    
    # 컬럼명 공백 제거
    df.columns = df.columns.str.strip()
    
    # '날짜' 컬럼이 있는지 확인하고 처리
    if '날짜' in df.columns:
        # 데이터 정제 (특수문자 제거)
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        
        # 연도 컬럼 생성 (날짜 컬럼이 있을 때만 실행)
        df['년'] = df['날짜'].dt.year
    else:
        # 날짜 컬럼을 못 찾았을 경우, 첫 번째 컬럼을 날짜로 가정해보기 (옵션)
        st.warning(f"⚠️ '날짜' 컬럼을 찾을 수 없습니다. (현재 컬럼: {list(df.columns)})")
        return df # 처리 없이 반환하여 에러 메시지 유도

    return df

# 2. 파일 불러오기
file_path = 'test.py.csv'
df = None

# 서버에 파일이 있으면 우선 로드
if os.path.exists(file_path):
    df = process_data(file_path)

# 없거나 로드 실패 시 업로더 표시
if df is None:
    st.info("파일을 업로드해주세요.")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=['csv'])
    if uploaded_file is not None:
        df = process_data(uploaded_file)

# 3. 데이터 분석 및 시각화
if df is not None and '년' in df.columns:
    st.success("데이터 로드 및 분석 성공!")
    
    # 연도별 평균 기온 계산
    # dropna()로 연도가 없거나 기온이 없는 행 제거
    df_clean = df.dropna(subset=['년', '평균기온(℃)'])
    df_yearly = df_clean.groupby('년')['평균기온(℃)'].mean().reset_index()
    
    if len(df_yearly) > 1:
        # 추세선 계산
        z = np.polyfit(df_yearly['년'], df_yearly['평균기온(℃)'], 1)
        p = np.poly1d(z)
        df_yearly['추세선'] = p(df_yearly['년'])
        
        # 차트 데이터 준비
        chart_data = df_yearly.set_index('년')[['평균기온(℃)', '추세선']]
        
        st.subheader("📈 연도별 평균 기온 및 추세")
        st.line_chart(chart_data, color=["#bdc3c7", "#ff0000"])
        
        # 요약 통계
        st.subheader("📊 분석 결과 요약")
        first_10 = df_yearly.head(10)['평균기온(℃)'].mean()
        last_10 = df_yearly.tail(10)['평균기온(℃)'].mean()
        diff = last_10 - first_10
        
        c1, c2, c3 = st.columns(3)
        c1.metric("초기 10년 평균", f"{first_10:.2f} ℃")
        c2.metric("최근 10년 평균", f"{last_10:.2f} ℃")
        c3.metric("변화량", f"{diff:+.2f} ℃", delta_color="inverse")
        
        st.divider()
        
        slope = z[0]
        if slope > 0:
            st.warning(f"🔥 결론: 지난 {len(df_yearly)}년간 기온은 꾸준히 **상승**했습니다. (연간 +{slope:.4f}℃)")
        else:
            st.info("❄️ 결론: 기온 상승 경향이 뚜렷하지 않습니다.")
    else:
        st.warning("분석할 데이터가 충분하지 않습니다.")
        
    with st.expander("데이터 원본 보기"):
        st.dataframe(df)

elif df is not None:
    st.error("데이터에 '날짜' 또는 '년' 정보를 파악할 수 없습니다. 컬럼명을 확인해주세요.")
