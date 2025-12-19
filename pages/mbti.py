import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(
    page_title="국가별 MBTI 성향 분석",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. 국가명 한글 매핑 데이터 (수정됨) ---
def get_country_mapping():
    return {
        "Afghanistan": "아프가니스탄", "Albania": "알바니아", "Algeria": "알제리", "Andorra": "안도라", "Angola": "앙골라",
        "Antigua and Barbuda": "앤티가 바부다", "Argentina": "아르헨티나", "Armenia": "아르메니아", "Australia": "호주", "Austria": "오스트리아",
        "Azerbaijan": "아제르바이잔", "Bahamas": "바하마", "Bahrain": "바레인", "Bangladesh": "방글라데시", "Barbados": "바베이도스",
        "Belarus": "벨라루스", "Belgium": "벨기에", "Belize": "벨리즈", "Benin": "베냉", "Bhutan": "부탄",
        "Bolivia": "볼리비아", "Bosnia and Herzegovina": "보스니아 헤르체고비나", "Botswana": "보츠와나", "Brazil": "브라질", "Brunei": "브루나이",
        "Bulgaria": "불가리아", "Burkina Faso": "부르키나파소", "Burundi": "부룬디", "Cambodia": "캄보디아", "Cameroon": "카메룬",
        "Canada": "캐나다", "Cape Verde": "카보베르데", "Central African Republic": "중앙아프리카공화국", "Chad": "차드", "Chile": "칠레",
        "China": "중국", "Colombia": "콜롬비아", "Comoros": "코모로", "Congo": "콩고", "Congo (Kinshasa)": "콩고 민주 공화국",
        "Costa Rica": "코스타리카", "Croatia": "크로아티아", "Cuba": "쿠바", "Cyprus": "키프로스", "Czech Republic": "체코",
        "Denmark": "덴마크", "Djibouti": "지부티", "Dominica": "도미니카 연방", "Dominican Republic": "도미니카 공화국", "Ecuador": "에콰도르",
        "Egypt": "이집트", "El Salvador": "엘살바도르", "Equatorial Guinea": "적도 기니", "Eritrea": "에리트레아", "Estonia": "에스토니아",
        "Eswatini": "에스와티니", "Ethiopia": "에티오피아", "Fiji": "피지", "Finland": "핀란드", "France": "프랑스",
        "Gabon": "가봉", "Gambia": "감비아", "Georgia": "조지아", "Germany": "독일", "Ghana": "가나",
        "Greece": "그리스", "Grenada": "그레나다", "Guatemala": "과테말라", "Guinea": "기니", "Guinea-Bissau": "기니비사우",
        "Guyana": "가이아나", "Haiti": "아이티", "Honduras": "온두라스", "Hungary": "헝가리", "Iceland": "아이슬란드",
        "India": "인도", "Indonesia": "인도네시아", "Iran": "이란", "Iraq": "이라크", "Ireland": "아일랜드",
        "Israel": "이스라엘", "Italy": "이탈리아", "Jamaica": "자메이카", "Japan": "일본", "Jordan": "요르단",
        "Kazakhstan": "카자흐스탄", "Kenya": "케냐", "Kiribati": "키리바시", "North Korea": "북한", "South Korea": "대한민국",
        "Korea, Republic of": "대한민국", "Korea, South": "대한민국", "Kuwait": "쿠웨이트", "Kyrgyzstan": "키르기스스탄", "Laos": "라오스",
        "Latvia": "라트비아", "Lebanon": "레바논", "Lesotho": "레소토", "Liberia": "라이베리아", "Libya": "리비아",
        "Liechtenstein": "리히텐슈타인", "Lithuania": "리투아니아", "Luxembourg": "룩셈부르크", "Madagascar": "마다가스카르", "Malawi": "말라위",
        "Malaysia": "말레이시아", "Maldives": "몰디브", "Mali": "말리", "Malta": "몰타", "Marshall Islands": "마셜 제도",
        "Mauritania": "모리타니", "Mauritius": "모리셔스", "Mexico": "멕시코", "Micronesia": "미크로네시아", "Moldova": "몰도바",
        "Monaco": "모나코", "Mongolia": "몽골", "Montenegro": "몬테네그로", "Morocco": "모로코", "Mozambique": "모잠비크",
        "Myanmar": "미얀마", "Namibia": "나미비아", "Nauru": "나우루", "Nepal": "네팔", "Netherlands": "네덜란드",
        "New Zealand": "뉴질랜드", "Nicaragua": "니카라과", "Niger": "니제르", "Nigeria": "나이지리아", "North Macedonia": "북마케도니아",
        "Macedonia": "북마케도니아",  # 추가된 부분
        "Norway": "노르웨이", "Oman": "오만", "Pakistan": "파키스탄", "Palau": "팔라우", "Panama": "파나마",
        "Papua New Guinea": "파푸아뉴기니", "Paraguay": "파라과이", "Peru": "페루", "Philippines": "필리핀", "Poland": "폴란드",
        "Portugal": "포르투갈", "Qatar": "카타르", "Romania": "루마니아", "Russia": "러시아", "Rwanda": "르완다",
        "Saint Kitts and Nevis": "세인트키츠 네비스", "Saint Lucia": "세인트루시아", "Saint Vincent and the Grenadines": "세인트빈센트 그레나딘", "Samoa": "사모아", "San Marino": "산마리노",
        "Sao Tome and Principe": "상투메 프린시페", "Saudi Arabia": "사우디아라비아", "Senegal": "세네갈", "Serbia": "세르비아", "Seychelles": "세이셸",
        "Sierra Leone": "시에라리온", "Singapore": "싱가포르", "Slovakia": "슬로바키아", "Slovenia": "슬로베니아", "Solomon Islands": "솔로몬 제도",
        "Somalia": "소말리아", "South Africa": "남아프리카 공화국", "South Sudan": "남수단", "Spain": "스페인", "Sri Lanka": "스리랑카",
        "Sudan": "수단", "Suriname": "수리남", "Sweden": "스웨덴", "Switzerland": "스위스", "Syria": "시리아",
        "Taiwan": "대만", "Tajikistan": "타지키스탄", "Tanzania": "탄자니아", "Thailand": "태국", "Timor-Leste": "동티모르",
        "Togo": "토고", "Tonga": "통가", "Trinidad and Tobago": "트리니다드 토바고", "Tunisia": "튀니지", "Turkey": "튀르키예",
        "Turkmenistan": "투르크메니스탄", "Tuvalu": "투발루", "Uganda": "우간다", "Ukraine": "우크라이나", "United Arab Emirates": "아랍에미리트",
        "United Kingdom": "영국", "United States": "미국", "Uruguay": "우루과이", "Uzbekistan": "우즈베키스탄", "Vanuatu": "바누아투",
        "Vatican City": "바티칸 시국", "Venezuela": "베네수엘라", "Vietnam": "베트남", "Yemen": "예멘", "Zambia": "잠비아", "Zimbabwe": "짐바브웨"
    }

# --- 2. 데이터 로드 및 전처리 ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('countries (1).csv')
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 'countries (1).csv' 파일을 같은 폴더에 업로드해주세요.")
        return None

    # 국가 이름 한글 변환
    country_map = get_country_mapping()
    df['Country'] = df['Country'].map(country_map).fillna(df['Country'])

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

    # --- 공통 함수: 원그래프(도넛 차트) ---
    def make_donut_chart(data, value_col, category_col, title):
        base = alt.Chart(data).encode(
            theta=alt.Theta(field=value_col, stack=True)
        )
        
        pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
            color=alt.Color(field=category_col, legend=alt.Legend(title="MBTI 유형")),
            order=alt.Order(field=value_col, sort="descending"),
            tooltip=[category_col, alt.Tooltip(field=value_col, format=".2%")]
        )
        
        text = base.mark_text(radius=140).encode(
            text=alt.Text(field=value_col, format=".1%"),
            order=alt.Order(field=value_col, sort="descending"),
            color=alt.value("black")  
        ).transform_filter(
            alt.datum[value_col] > 0.05
        )
        
        return (pie + text).properties(title=title, height=400)

    # --- 메뉴 1: 국가별 상세 분석 ---
    if menu == "국가별 상세 분석":
        st.header("🏳️ 국가별 MBTI 성향 분석")
        
        # 한국 찾기 (이름이 '대한민국'으로 바뀜)
        default_country = '대한민국'
        country_list = df['Country'].tolist()
        
        if default_country in country_list:
            default_index = country_list.index(default_country)
        else:
            default_index = 0
        
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
        
        global_avg = df[mbti_list].mean().reset_index()
        global_avg.columns = ['MBTI', 'Average']
        
        top_global = global_avg.sort_values(by='Average', ascending=False).iloc[0]
        st.write(f"전 세계적으로 가장 흔한 유형은 **{top_global['MBTI']}** ({top_global['Average']:.2%}) 입니다.")
        
        chart_global = make_donut_chart(global_avg, 'Average', 'MBTI', "전 세계 MBTI 평균 분포")
        st.altair_chart(chart_global, use_container_width=True)

    # --- 메뉴 3: 유형별 랭킹 & 한국 비교 ---
    elif menu == "유형별 랭킹 & 한국 비교":
        st.header("🏆 MBTI 유형별 TOP 10 국가 & 한국 비교")
        st.caption("※ 랭킹은 구성 비율이 아닌 국가 간 크기 비교이므로 막대그래프가 적합합니다.")
        
        target_mbti = st.selectbox("순위를 확인하고 싶은 MBTI 유형을 선택하세요:", mbti_list)
        
        # 정렬
        sorted_df = df[['Country', target_mbti]].sort_values(by=target_mbti, ascending=False).reset_index(drop=True)
        sorted_df['Rank'] = sorted_df.index + 1
        
        top_10 = sorted_df.head(10)
        
        # '대한민국' 데이터 찾기
        korea_row = sorted_df[sorted_df['Country'] == '대한민국']
        
        col_rank1, col_rank2 = st.columns([2, 1])
        
        with col_rank1:
            st.subheader(f"{target_mbti} 비율 상위 10개국")
            
            # 차트 데이터
            chart_data = top_10.copy()
            if not korea_row.empty:
                if korea_row.iloc[0]['Rank'] > 10:
                     chart_data = pd.concat([chart_data, korea_row])
            
            bars = alt.Chart(chart_data).mark_bar().encode(
                x=alt.X(target_mbti, title='비율', axis=alt.Axis(format='%')),
                y=alt.Y('Country', sort='-x', title='국가'),
                color=alt.condition(
                    alt.datum.Country == '대한민국',
                    alt.value('red'),
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
                st.warning("데이터에서 대한민국을 찾을 수 없습니다.")

else:
    st.stop()
