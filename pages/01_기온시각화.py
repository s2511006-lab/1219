import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# 페이지 기본 설정
st.set_page_config(page_title="110년 기온 변화 분석", layout="wide")

st.title("🌡️ 지난 110년 기온 변화 분석 (Interactive)")
st.markdown("마우스를 그래프 위에 올리면 상세 정보를 볼 수 있으며, 확대/축소가 가능합니다.")

# ---------------------------------------------------------
# 1. 데이터 로드 및 전처리 함수
# ---------------------------------------------------------
@st.cache_data
def load_data(file):
    df = None
    encodings = ['utf-8', 'cp949', 'euc-kr']
    
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
    
    # [날짜 데이터 정제] 탭(\t)이나 따옴표(")가 섞여 있어도 처리
    if '날짜' in df.columns:
        df['날짜'] = df['날짜'].astype(str).str.replace('"', '').str.replace('\t', '').str.strip()
        df['날짜'] = pd.to_datetime(df['날짜'], errors='coerce')
        df['Year'] = df['날짜'].dt.year
    else:
        return None

    # [기온 데이터 정제] 숫자로 변환 후 결측치 제거 (NaN 방지)
    if '평균기온(℃)' in df.columns:
        df['평균기온(℃)'] = pd.to_numeric(df['평균기온(℃)'], errors='coerce')
        # 연도나 기온이 없는 행은 삭제
        df = df.dropna(subset=['Year', '평균기온(℃)'])
        
    return df

# ---------------------------------------------------------
# 2. 메인 실행 로직
# ---------------------------------------------------------

file_name = 'test.py.csv'
df = None

# (1) 파일 확인 (서버 파일 or 업로드)
if os.path.exists(file_name):
    df = load_data(file_name)

if df is None:
    st.info("👋 서버에 데이터 파일이 없습니다. 파일을 업로드해주세요.")
    uploaded_file = st.file_uploader("CSV 파일 업로드", type=['csv'])
    if uploaded_file is not None:
        df = load_data(uploaded_file)

# (3) 분석 및 Plotly 시각화
if df is not None:
    if 'Year' in df.columns and '평균기온(℃)' in df.columns:
        
        # 안내 메시지
        if os.path.exists(file_name) and not hasattr(df, 'name'):
             st.success(f"📂 '{file_name}' 데이터를 분석합니다.")
        else:
             st.success("📂 업로드된 데이터를 분석합니다.")

        # 연도별 평균 기온 계산
        df_yearly = df.groupby('Year')['평균기온(℃)'].mean().reset_index()

        if len(df_yearly) > 1:
            # --- 추세선 계산 (Numpy) ---
            z = np.polyfit(df_yearly['Year'], df_yearly['평균기온(℃)'], 1)
            p = np.poly1d(z)
            slope = z[0] # 기울기
            
            # --- Plotly 그래프 그리기 ---
            fig = go.Figure()

            # 1) 산점도 (실제 기온 데이터)
            fig.add_trace(go.Scatter(
                x=df_yearly['Year'], 
                y=df_yearly['평균기온(℃)'],
                mode='markers',
                name='연평균 기온',
                marker=dict(color='#bdc3c7', size=8, opacity=0.7),
                hovertemplate='<b>%{x}년</b><br>평균기온: %{y:.2f}℃<extra></extra>'
            ))

            # 2) 추세선 (Trend Line)
            fig.add_trace(go.Scatter(
                x=df_yearly['Year'], 
                y=p(df_yearly['Year']),
                mode='lines',
                name='추세선',
                line=dict(color='red', width=3, dash='dash'),
                hovertemplate='추세값: %{y:.2f}℃<extra></extra>'
            ))

            # 레이아웃 설정
            fig.update_layout(
                title="📈 지난 110년간의 기온 변화 추이",
                xaxis_title="연도 (Year)",
                yaxis_title="평균 기온 (℃)",
                hovermode="x unified", # X축 기준으로 툴팁 통합 표시
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )

            # 스트림릿에 그래프 표시 (반응형)
            st.plotly_chart(fig, use_container_width=True)

            # --- 결과 분석 지표 ---
            st.subheader("📊 분석 요약")
            col1, col2, col3 = st.columns(3)
            
            start_temp = p(df_yearly['Year'].min())
            end_temp = p(df_yearly['Year'].max())
            total_change = end_temp - start_temp
            
            col1.metric("연평균 기온 상승률", f"{slope:.4f} ℃/년")
            col2.metric(f"총 기온 변화량 ({len(df_yearly)}년)", f"{total_change:.2f} ℃")
            
            # 상승/하락 판정
            if slope > 0:
                col3.error("판정: 기온 상승 중 🔥")
            elif slope < 0:
                col3.info("판정: 기온 하락 중 ❄️")
            else:
                col3.warning("판정: 변화 없음 ➖")

        else:
            st.warning("데이터가 부족하여 추세선을 그릴 수 없습니다.")

        with st.expander("📋 데이터 원본 보기"):
            st.dataframe(df)

    else:
        st.error("데이터에서 필수 컬럼('날짜', '평균기온(℃)')을 찾을 수 없습니다.")
