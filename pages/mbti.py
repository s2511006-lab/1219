import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정 (전체 너비 사용)
st.set_page_config(
    page_title="국가별 MBTI 성향 분석",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    # 데이터 로드
    try:
        df = pd.read_csv('countries (1).csv')
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 'countries (1).csv' 파일을 같은 폴더에 업로드해주세요.")
        return None

    # 기본 16가지 MBTI 유형 리스트
    mbti_types = [
        'INTJ', 'INTP', 'ENTJ', 'ENTP',
        'INFJ', 'INFP', 'ENFJ', 'ENFP',
        'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ',
        'ISTP', 'ISFP', 'ESTP', 'ESFP'
    ]

    # -A와 -T를 합산하여 16가지 기본 유형 컬럼 생성
    for mbti in mbti_types:
        col_a = f"{mbti}-A"
        col_t = f"{mbti}-T"
        
        if col_a in df.columns and col_t in df.columns:
            df[mbti] = df[col_a] + df[col_t]
    
    return df, mbti_types

data_load_state = st.text('데이터를 불러오는 중...')
result = load_data()
data_load_state.text('')

if result is not None:
    df, mbti_list = result

    # --- 사이드바 ---
    st.sidebar.title("MBTI 분석 대시보드")
    menu = st.sidebar.radio("메뉴 선택", ["국가별 상세 분석", "전체 국가 평균", "유형별 랭킹 & 한국 비교"])

    st.title("🌏 전 세계 MBTI 데이터 분석")
    st.markdown("---")

    # --- 공통 함수: 원그래프(도넛 차트) 생성 ---
    def make_donut_chart(data, value_col, category_col, title):
        # 기본 차트 설정
        base = alt.Chart(data).encode(
            theta=alt.Theta(field=value_col, stack=True)
        )
        
        # 도넛 차트 (Arc)
        pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
            color=alt.Color(field=category_col, legend=alt.Legend(title="MBTI 유형")),
            order=alt.Order(field=value_col, sort="descending"),
            tooltip=[category_col, alt.Tooltip(field=value_col, format=".2%")]
        )
        
        # 텍스트 라벨 (비율 표시) - 상위 5개만 표시하거나 전체 표시 시 겹칠 수 있어 깔끔하게 처리
        text = base.mark_text(radius=140).encode(
            text=alt.Text(field=value_col, format=".1%"),
            order=alt.Order(field=value_col, sort="descending"),
            color=alt.value("black")  
        ).transform_filter(
            alt.datum[value_col] > 0.05  # 5% 이상인 항목만 텍스트 표시 (가독성 위해)
        )
        
        return (pie + text).properties(title=title, height=400)

    # --- 메뉴 1: 국가별 상세 분석 ---
    if menu == "국가별 상세 분석":
        st.header("🏳️ 국가별 MBTI 성향 분석")
        
        # 한국 찾기
        default_index = 0
        korea_names = ['South Korea', 'Korea, Republic of', 'Korea, South']
        country_list = df['Country'].tolist()
        for k in korea_names:
            if k in country_list:
                default_index = country_list.index(k)
                break
        
        selected_country = st.selectbox("분석할 국가를 선택하세요:", country_list, index=default_index)
        
        # 데이터 필터링
        country_data = df[df['Country'] == selected_country][mbti_list].T
        country_data.columns = ['Percentage']
        country_data = country_data.reset_index().rename(columns={'index': 'MBTI'})
        
        # 가장 높은 비율 찾기
        top_mbti = country_data.sort_values(by='Percentage', ascending=False).iloc[0]
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader(f"{selected_country}의 대표 유형")
            st.metric(label="최다 유형", value=top_mbti['MBTI'], delta=f"{top_mbti['Percentage']:.2%}")
            st.info(f"**{top_mbti['MBTI']}** 유형이 가장 큰 비중을 차지합니다.")

        with col2:
            st.subheader("MBTI 유형별 분포 (원그래프)")
            chart = make_donut_chart(country_data, 'Percentage', 'MBTI', f"{selected_country} MBTI 분포")
            st.altair_chart(chart, use_container_width=True)

    # --- 메뉴 2: 전체 국가 평균 ---
    elif menu == "전체 국가 평균":
        st.header("📊 전 세계 MBTI 평균 비율")
        
        # 전체 평균 계산
        global_avg = df[mbti_list].mean().reset_index()
        global_avg.columns = ['MBTI', 'Average']
        
        top_global = global_avg.sort_values(by='Average', ascending=False).iloc[0]
        st.write(f"전 세계적으로 가장 흔한 유형은 **{top_global['MBTI']}** ({top_global['Average']:.2%}) 입니다.")
        
        # 원그래프 그리기
        chart_global = make_donut_chart(global_avg, 'Average', 'MBTI', "전 세계 MBTI 평균 분포")
        st.altair_chart(chart_global, use_container_width=True)

    # --- 메뉴 3: 유형별 랭킹 & 한국 비교 ---
    elif menu == "유형별 랭킹 & 한국 비교":
        st.header("🏆 MBTI 유형별 TOP 10 국가 & 한국 비교")
        st.caption("※ 랭킹은 구성 비율이 아닌 국가 간 크기 비교이므로 막대그래프가 적합합니다.")
        
        target_mbti = st.selectbox("순위를 확인하고 싶은 MBTI 유형을 선택하세요:", mbti_list)
        
        # 정렬 및 랭킹 생성
        sorted_df = df[['Country', target_mbti]].sort_values(by=target_mbti, ascending=False).reset_index(drop=True)
        sorted_df['Rank'] = sorted_df.index + 1
        
        top_10 = sorted_df.head(10)
        korea_row = sorted_df[sorted_df['Country'].isin(['South Korea', 'Korea, Republic of', 'Korea, South'])]
        
        col_rank1, col_rank2 = st.columns([2, 1])
        
        with col_rank1:
            st.subheader(f"{target_mbti} 비율 상위 10개국")
            
            # 차트 데이터 (TOP 10 + 한국)
            chart_data = top_10.copy()
            if not korea_row.empty:
                if korea_row.iloc[0]['Rank'] > 10:
                     chart_data = pd.concat([chart_data, korea_row])
            
            # 가로 막대 차트 (Ranking에 적합)
            bars = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X(target_mbti, title='비율', axis=alt.Axis(format='%')),
                y=alt.Y('Country', sort='-x', title='국가'), # 값에 따라 내림차순 정렬
                color=alt.condition(
                    alt.FieldOneOfPredicate(field='Country', oneOf=['South Korea', 'Korea, Republic of', 'Korea, South']),
                    alt.value('red'),  # 한국 강조
                    alt.value('lightgray')
                ),
                tooltip=['Country', 'Rank', alt.Tooltip(target_mbti, format='.2%')]
            ).properties(height=500)
            
            text = bars.mark_text(
                align='left',
                baseline='middle',
                dx=3 
            ).encode(
                text=alt.Text(target_mbti, format='.1%')
            )

            st.altair_chart(bars + text, use_container_width=True)

        with col_rank2:
            st.subheader("🇰🇷 한국의 위치")
            if not korea_row.empty:
                k_rank = korea_row.iloc[0]['Rank']
                k_ratio = korea_row.iloc[0][target_mbti]
                
                st.metric(label="한국 순위", value=f"{k_rank}위")
                st.metric(label="한국 비율", value=f"{k_ratio:.2%}")
                
                total_countries = len(df)
                if k_rank <= 10:
                    st.success("상위 10위권!")
                elif k_rank <= total_countries / 2:
                    st.info("평균 이상입니다.")
                else:
                    st.warning("비교적 낮은 편입니다.")
            else:
                st.warning("데이터에서 한국을 찾을 수 없습니다.")

else:
    st.stop()
