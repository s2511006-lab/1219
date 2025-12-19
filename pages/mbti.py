import streamlit as st
import pandas as pd
import os

# 페이지 설정
st.set_page_config(page_title="Global MBTI Dashboard", layout="wide")

# 1. 파일 불러오기 (경로 문제 해결을 위한 로직 포함)
FILE_NAME = 'countries.csv'

@st.cache_data
def load_data():
    if not os.path.exists(FILE_NAME):
        return None, None
    
    df = pd.read_csv(FILE_NAME)
    # MBTI 컬럼 추출 (첫 번째 'Country' 컬럼 제외)
    mbti_cols = df.columns[1:].tolist()
    return df, mbti_cols

df, mbti_cols = load_data()

# 파일이 없을 경우 디버깅 메시지 출력
if df is None:
    st.error(f"❌ '{FILE_NAME}' 파일을 찾을 수 없습니다.")
    st.info(f"현재 폴더의 파일 목록: {os.listdir('.')}")
    st.warning("팁: 깃허브 저장소의 루트(최상위) 폴더에 파일이 있는지, 파일명이 정확히 'countries.csv'인지 확인해 주세요.")
    st.stop()

# --- 앱 메인 화면 ---
st.title("🌏 전 세계 MBTI 성향 분석 대시보드")
st.markdown("전 세계 국가별 MBTI 분포 데이터를 분석하고 한국과 비교합니다.")

# 2. 전체 국가 MBTI 평균 비율
st.header("📊 1. 전 세계 MBTI 평균 비율")
global_avg = df[mbti_cols].mean().sort_values(ascending=False)
st.bar_chart(global_avg)
with st.expander("평균 데이터 수치 보기"):
    st.dataframe(global_avg.rename("Global Average Ratio"))

st.divider()

# 3. MBTI 유형별 높은 국가 TOP 10
st.header("🏆 2. MBTI 유형별 국가 랭킹 (TOP 10)")
selected_type = st.selectbox("순위를 확인할 MBTI 유형을 선택하세요", mbti_cols)

top10 = df[['Country', selected_type]].sort_values(by=selected_type, ascending=False).head(10)
st.subheader(f"'{selected_type}' 비율이 가장 높은 국가 TOP 10")
st.bar_chart(top10.set_index('Country'))

st.divider()

# 4. 국가별 상세 분석 및 한국 비교
st.header("🔍 3. 국가별 상세 분석 & 한국 비교")

# 한국 데이터 찾기 (South Korea, Korea 등 포함된 이름 검색)
korea_df = df[df['Country'].str.contains('Korea', case=False, na=False)]
korea_name = korea_df['Country'].values[0] if not korea_df.empty else None

# 분석할 국가 선택
countries_list = df['Country'].unique().tolist()
selected_country = st.selectbox("상세 분석할 국가를 선택하세요", countries_list, index=countries_list.index('United States') if 'United States' in countries_list else 0)

col1, col2 = st.columns(2)

# 선택 국가 데이터
country_data = df[df['Country'] == selected_country][mbti_cols].T
country_data.columns = [selected_country]

with col1:
    st.subheader(f"📍 {selected_country} 분석")
    st.write(f"가장 많은 유형: **{country_data.idxmax()[0]}**")
    st.bar_chart(country_data)

# 한국과 비교
with col2:
    if korea_name:
        st.subheader(f"🇰🇷 한국({korea_name})과 비교")
        korea_data = df[df['Country'] == korea_name][mbti_cols].T
        korea_data.columns = [korea_name]
        
        comparison_df = pd.concat([korea_data, country_data], axis=1)
        st.line_chart(comparison_df)
        
        # 차이가 큰 유형 분석
        comparison_df['Diff'] = (comparison_df[selected_country] - comparison_df[korea_name]).abs()
        biggest_diff = comparison_df.sort_values(by='Diff', ascending=False).head(3)
        st.write("두 국가 간 가장 차이가 큰 유형:")
        st.write(", ".join(biggest_diff.index.tolist()))
    else:
        st.warning("데이터에서 한국(Korea)을 찾을 수 없습니다.")
