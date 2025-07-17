import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_carousel import carousel

# 클러스터링 관련 함수들
def calculate_scores(data):
    """각 차량에 대해 3파트별 점수 계산 - 균형잡힌 분포"""
    
    # 정규화 함수 (0-1 범위로 변환)
    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())
    
    # 1. 속도 점수 (가속성능에 더 큰 가중치)
    # 제로백이 낮을수록 좋으므로 역순 정규화
    speed_norm = normalize(data['top_speed_kmh']) * 0.4
    accel_norm = normalize(data['acceleration_0_100_s'].max() - data['acceleration_0_100_s']) * 0.6
    speed_score = (speed_norm + accel_norm) * 100
    
    # 2. 배터리 성능 점수 (효율성에 더 큰 가중치)
    battery_norm = normalize(data['battery_capacity_kWh']) * 0.3
    range_norm = normalize(data['range_km']) * 0.3
    # 효율성은 낮을수록 좋으므로 역순 정규화
    efficiency_norm = normalize(data['efficiency_wh_per_km'].max() - data['efficiency_wh_per_km']) * 0.4
    battery_score = (battery_norm + range_norm + efficiency_norm) * 100
    
    # 3. 충전 속도 점수 (급속충전에 집중)
    charging_norm = normalize(data['fast_charging_power_kw_dc']) * 0.9
    battery_capacity_norm = normalize(data['battery_capacity_kWh']) * 0.1
    charging_score = (charging_norm + battery_capacity_norm) * 100
    
    return speed_score, battery_score, charging_score

def assign_clusters(data):
    """임계값 기반 클러스터 분류"""
    
    # 임계값 설정 (상위 30%)
    speed_cutoff = np.percentile(data['speed_score'], 70)
    battery_cutoff = np.percentile(data['battery_score'], 70) 
    charging_cutoff = np.percentile(data['charging_score'], 70)
    
    clusters = []
    for _, row in data.iterrows():
        # 임계값 이상인 점수들만 후보로 선정
        candidates = []
        if row['speed_score'] >= speed_cutoff:
            candidates.append(('speed', row['speed_score']))
        if row['battery_score'] >= battery_cutoff:
            candidates.append(('battery', row['battery_score']))
        if row['charging_score'] >= charging_cutoff:
            candidates.append(('charging', row['charging_score']))
        
        if len(candidates) == 0:
            # 임계값을 넘지 못한 경우 가장 높은 점수의 클러스터로 배정
            max_score = max(row['speed_score'], row['battery_score'], row['charging_score'])
            if max_score == row['speed_score']:
                clusters.append('speed')
            elif max_score == row['battery_score']:
                clusters.append('battery')
            else:
                clusters.append('charging')
        else:
            # 임계값을 넘은 점수 중 가장 높은 것으로 분류
            candidates.sort(key=lambda x: x[1], reverse=True)
            clusters.append(candidates[0][0])
    
    return clusters

def get_top_models_by_cluster(data, cluster_name, score_column, top_n=5):
    """클러스터별 상위 모델 선정"""
    cluster_data = data[data['cluster'] == cluster_name]
    if len(cluster_data) == 0:
        return pd.DataFrame()
    
    top_indices = cluster_data[score_column].nlargest(min(top_n, len(cluster_data))).index
    return data.loc[top_indices]

def generate_web_comment(cluster_name):
    """웹페이지용 코멘트 생성"""
    comments = {
        'speed': {
            'title': '🏎️ 스피드 매니아를 위한 전기차',
            'subtitle': '짜릿한 가속과 최고속도를 자랑하는 퍼포먼스 전기차',
            'description': '드라이빙의 재미와 스포티한 성능을 중시하는 당신을 위해 선별된 전기차들입니다. 강력한 모터와 뛰어난 가속력으로 도로 위의 스릴을 만끽하세요.',
            'target': '스포츠카 애호가, 퍼포먼스 중시 운전자'
        },
        'battery': {
            'title': '🔋 장거리 여행의 최적 파트너',
            'subtitle': '효율성과 주행거리가 뛰어난 실용성 전기차',
            'description': '한 번의 충전으로 더 멀리, 더 경제적으로 이동하고 싶은 당신을 위한 전기차들입니다. 넉넉한 배터리 용량과 뛰어난 에너지 효율로 여행의 자유를 선사합니다.',
            'target': '장거리 통근자, 여행 애호가, 경제성 중시 운전자'
        },
        'charging': {
            'title': '⚡ 빠른 충전의 혁신',
            'subtitle': '급속충전으로 시간을 절약하는 편의성 전기차',
            'description': '바쁜 일상 속에서도 빠른 충전으로 시간을 절약하고 싶은 당신을 위한 전기차들입니다. 최신 급속충전 기술로 짧은 시간에 충분한 에너지를 공급받으세요.',
            'target': '바쁜 직장인, 시간 효율성 중시 운전자'
        }
    }
    return comments.get(cluster_name, {})

def prepare_clustering_data(df):
    """클러스터링을 위한 데이터 준비"""
    # 필요한 컬럼 정의
    features = ['top_speed_kmh', 'acceleration_0_100_s', 'battery_capacity_kWh', 
                'efficiency_wh_per_km', 'range_km', 'fast_charging_power_kw_dc']
    
    # 결측치 제거
    df_clean = df[features + ['brand', 'model']].dropna()
    X = df_clean[features].copy()
    
    # 점수 계산
    speed_scores, battery_scores, charging_scores = calculate_scores(X)
    
    X['speed_score'] = speed_scores
    X['battery_score'] = battery_scores  
    X['charging_score'] = charging_scores
    X['brand'] = df_clean['brand'].values
    X['model'] = df_clean['model'].values
    
    # 클러스터 분류
    X['cluster'] = assign_clusters(X)
    
    return X

def display_cluster_recommendations_streamlit(cluster_data, filtered_df):
    """Streamlit용 클러스터별 추천 결과 출력"""
    clusters_info = [
        ('speed', 'speed_score', '속도'),
        ('battery', 'battery_score', '배터리'), 
        ('charging', 'charging_score', '충전')
    ]
    
    st.markdown("## 🤖 AI 추천 시스템")
    st.markdown("---")
    
    for cluster_name, score_col, display_name in clusters_info:
        cluster_info = generate_web_comment(cluster_name)
        
        # 전체 클러스터에서 TOP 5 선정
        top_models = get_top_models_by_cluster(cluster_data, cluster_name, score_col, 5)
        
        # 필터링된 데이터와 교집합 (brand, model 기준)
        if len(filtered_df) > 0:
            # brand, model을 기준으로 필터링된 데이터와 매칭
            filtered_top = top_models[
                top_models.apply(lambda row: 
                    any((filtered_df['brand'] == row['brand']) & 
                        (filtered_df['model'] == row['model'])), axis=1)
            ]
        else:
            filtered_top = top_models
        
        if len(filtered_top) > 0:
            with st.expander(f"{cluster_info.get('title', f'{display_name} 클러스터')} - {len(filtered_top)}대 추천", expanded=True):
                st.markdown(f"**{cluster_info.get('subtitle', '')}**")
                st.markdown(f"💬 {cluster_info.get('description', '')}")
                st.markdown(f"🎯 **추천 대상**: {cluster_info.get('target', '')}")
                
                st.markdown(f"### 🏆 {display_name} 클러스터 TOP {len(filtered_top)}")
                
                for idx, (_, model_row) in enumerate(filtered_top.iterrows(), 1):
                    if cluster_name == 'speed':
                        st.markdown(f"""
                        **{idx}. {model_row['brand']} {model_row['model']}** (속도점수: {model_row['speed_score']:.1f}점)
                        - 최고속도: {model_row['top_speed_kmh']:.0f}km/h, 제로백: {model_row['acceleration_0_100_s']:.1f}초
                        """)
                    elif cluster_name == 'battery':
                        st.markdown(f"""
                        **{idx}. {model_row['brand']} {model_row['model']}** (배터리점수: {model_row['battery_score']:.1f}점)
                        - 배터리: {model_row['battery_capacity_kWh']:.1f}kWh, 주행거리: {model_row['range_km']:.0f}km
                        - 효율성: {model_row['efficiency_wh_per_km']:.0f}Wh/km
                        """)
                    elif cluster_name == 'charging':
                        st.markdown(f"""
                        **{idx}. {model_row['brand']} {model_row['model']}** (충전점수: {model_row['charging_score']:.1f}점)
                        - 급속충전: {model_row['fast_charging_power_kw_dc']:.0f}kW, 배터리: {model_row['battery_capacity_kWh']:.1f}kWh
                        """)
        else:
            with st.expander(f"{cluster_info.get('title', f'{display_name} 클러스터')} - 조건에 맞는 차량 없음"):
                st.warning(f"현재 필터 조건에서는 {display_name} 클러스터에 해당하는 차량이 없습니다.")

def app(df):
    st.set_page_config(layout="wide")  # 전체 화면 폭 사용
    st.title("🔍 나에게 맞는 전기차 찾기")

    hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    image = 'log.png'
    col_img, col_title = st.columns([1, 4])
    with col_img:
        st.image(image, width=120)

    eng_to_kor = {
    "brand": "브랜드",
    "model": "모델",
    "top_speed_kmh": "최고 속도 (km/h)",
    "battery_capacity_kWh": "배터리 용량 (kWh)",
    "efficiency_wh_per_km": "효율 (Wh/km)",
    "range_km": "주행 가능 거리 (km)",
    "acceleration_0_100_s": "가속력 (0→100km/h, 초)",
    "fast_charging_power_kw_dc": "급속 충전 전력 (kW, DC)",
    "fast_charge_port": "급속 충전 포트",
    "cargo_volume_l": "적재 용량 (L)",
    "seats": "좌석 수",
    "drivetrain": "구동 방식",
    "car_body_type": "차체 형태",
    "car_size": "차 크기",
    "length_mm": "전장 (mm)",
    "width_mm": "전폭 (mm)",
    "height_mm": "전고 (mm)",
    "torque_nm": "토크 (Nm)",
    "battery_type": "배터리 종류"
    }

    filter_column = ['car_size', 'drivetrain', 'car_body_type']
    car_column = ['brand', 'model']
    hover_column = ["length_mm", "width_mm", "height_mm", "torque_nm", "battery_type", "seats"]
    image1 = ["image_url"]
    axis_column = [col for col in df.columns if col not in filter_column + car_column + hover_column + image1]

    def generate_multiselect_filter(df, filter_column) -> list:
        filtered_variable = []
        for filter_element in filter_column:
            options = sorted(df[filter_element].dropna().unique().tolist())
            # default_value = [options[0]] if options else []
            default_value = []
            selected = st.multiselect(f'{filter_element}', options=options, default=default_value)
            filtered_variable.append((filter_element, selected))
        return filtered_variable

    def return_filtered_df(df: pd.DataFrame, filter_zip: list) -> pd.DataFrame:
        for col, selected_values in filter_zip:
            if selected_values:
                df = df[df[col].isin(selected_values)]
        return df

    def select_checkbox(axis_column):
        axis_options = ["-- 축을 선택하세요 --"] + axis_column
        x = st.selectbox("X축 변수", axis_options, key="x_axis")
        y_candidates = [col for col in axis_column if col != x]
        y_options = ["-- 축을 선택하세요 --"] + y_candidates
        y = st.selectbox("Y축 변수", y_options, key="y_axis")
        # if x == "-- 축을 선택하세요 --" or y == "-- 축을 선택하세요 --":
        #     return None, None
        return x, y
    
    def get_ev_spec_relationship(x_axis: str, y_axis: str) -> str:
    # 두 변수의 조합을 세트로 정규화하여 순서 무관하게 비교
        pair = frozenset([x_axis, y_axis])

        # 사전 정의된 관계 설명 매핑
        descriptions = {
            frozenset(["top_speed_kmh", "acceleration_0_100_s"]): 
                "일반적으로 최고 속도가 높은 차량은 고출력 모터를 탑재해 정지 상태에서의 가속 성능도 뛰어납니다. 특히 스포츠 성향의 전기차는 이 두 지표에서 모두 높은 수치를 보입니다. 빠른 출발과 고속 주행이 모두 필요하다면 두 지표를 함께 확인하세요.",

            frozenset(["top_speed_kmh", "range_km"]): 
                "고속 주행이 가능한 차량은 일반적으로 대형 배터리를 탑재한 경우가 많아 장거리 운행도 가능하지만, 고속 주행 시 전비 저하로 실 주행거리는 줄어들 수 있습니다. 고속 주행 빈도에 따라 이 둘의 균형을 보는 것이 중요합니다.",

            frozenset(["top_speed_kmh", "efficiency_wh_per_km"]): 
                "고속 주행은 전력 소모가 커서 일반적으로 전비는 낮아지지만, 최신 고성능 EV 중에는 에너지 회생 제동과 고효율 모터 설계를 통해 고속 + 고효율을 동시에 갖춘 모델도 존재합니다.",

            frozenset(["top_speed_kmh", "fast_charging_power_kw_dc"]): 
                "고성능 차량일수록 대형 배터리를 빠르게 충전하기 위해 높은 출력의 급속 충전 기능을 탑재하는 경우가 많습니다. 주행 성능과 충전 효율을 동시에 고려한 결과입니다.",

            frozenset(["top_speed_kmh", "cargo_volume_l"]): 
                "최고 속도가 높은 차량은 보통 낮고 슬림한 형태로 적재 공간이 제한적인 경우가 많습니다. 실용성과 퍼포먼스를 동시에 원한다면 중형 SUV 계열의 EV를 추천합니다.",

            frozenset(["top_speed_kmh", "fast_charge_port"]): 
                "고속 주행 성능을 가진 차량이라도 DC 급속 충전 포트가 없다면 장거리 운행 시 불편함을 겪을 수 있습니다. 차량의 성능과 더불어 충전 인프라 호환성도 함께 확인하세요.",

            frozenset(["efficiency_wh_per_km", "range_km"]): 
                "높은 효율성을 가진 차량이라도 배터리 용량이 작다면 주행거리는 제한적일 수 있습니다. 전비와 함께 배터리 용량 또는 주행거리를 함께 고려해야 정확한 차량 성능을 이해할 수 있습니다.",

            frozenset(["efficiency_wh_per_km", "acceleration_0_100_s"]): 
                "일반적으로 빠른 가속을 위해 강한 출력을 사용하는 차량은 더 많은 전기를 소비하게 되어 전비가 낮아집니다. 효율 중심의 주행을 원한다면 가속 스펙은 어느 정도 타협이 필요합니다.",

            frozenset(["efficiency_wh_per_km", "cargo_volume_l"]): 
                "크고 무거운 차량일수록 에너지 소비가 많아 전비가 낮아질 가능성이 큽니다. 하지만 최신 경량화 기술로 이러한 트렌드를 극복한 EV도 일부 존재합니다.",

            frozenset(["efficiency_wh_per_km", "fast_charging_power_kw_dc"]): 
                "전비와 충전 속도는 직접적인 상관관계는 없습니다. 다만 프리미엄 전기차의 경우 두 항목 모두 우수한 스펙을 갖추는 경향이 있어 가격 대비 성능 비교가 필요합니다.",

            frozenset(["efficiency_wh_per_km", "fast_charge_port"]): 
                "에너지 효율이 좋은 차량이라도 구형 모델의 경우 DC 급속 충전이 안 될 수 있습니다. 충전 편의성을 고려한다면 전비뿐만 아니라 포트 지원 여부도 확인해야 합니다.",

            frozenset(["range_km", "acceleration_0_100_s"]): 
                "퍼포먼스 중심의 차량은 전력 소모가 커서 동일 배터리 용량 대비 주행거리가 짧을 수 있습니다. 고성능과 긴 거리 모두를 원할 경우 대용량 배터리 탑재 여부를 확인하세요.",

            frozenset(["range_km", "cargo_volume_l"]): 
                "차량 무게가 증가하면 주행거리는 줄어들 수 있습니다. 실사용 조건에서의 테스트 결과나 WLTP 인증거리 외에 소비자 리뷰도 함께 참고하는 것이 좋습니다.",

            frozenset(["range_km", "fast_charging_power_kw_dc"]): 
                "장거리용 차량은 급속충전 성능도 중요한 요소입니다. 배터리 용량이 크기 때문에 고출력 충전이 없으면 충전 시간이 길어져 실용성이 떨어질 수 있습니다.",

            frozenset(["range_km", "fast_charge_port"]): 
                "주행거리가 길어도 충전 인프라 호환성이 낮다면 장거리 운행에서 치명적입니다. DC 급속 충전 지원 여부는 꼭 확인해야 할 체크포인트입니다.",

            frozenset(["acceleration_0_100_s", "cargo_volume_l"]): 
                "적재 공간이 넓은 차량은 일반적으로 무거워서 가속 성능이 떨어지는 경향이 있지만, 전기차는 토크가 즉각 전달되어 무게 대비 빠른 반응성을 보이는 경우도 있습니다.",

            frozenset(["acceleration_0_100_s", "fast_charging_power_kw_dc"]): 
                "퍼포먼스 EV는 보통 대용량 배터리 탑재로 고속충전을 지원합니다. 다만 엔트리급 모델 중엔 가속력은 빠르지만 충전 속도가 느린 모델도 있으니 사양을 꼭 확인하세요.",

            frozenset(["acceleration_0_100_s", "fast_charge_port"]): 
                "일부 고성능 차량도 DC 포트를 생략한 경우가 있으며, 이는 여행이나 외부 이동이 잦은 사용자에겐 불편할 수 있습니다.",

            frozenset(["fast_charging_power_kw_dc", "fast_charge_port"]): 
                "출력이 높아도 차량에 DC 포트가 없다면 해당 속도로 충전할 수 없습니다. 출력과 포트 지원 여부를 함께 확인하세요.",

            frozenset(["fast_charging_power_kw_dc", "cargo_volume_l"]): 
                "화물이나 다인승 모델은 충전 효율이 중요해 고속 충전 기능을 갖춘 경우가 많습니다. 이는 실사용 효율성과 연결됩니다.",

            frozenset(["fast_charge_port", "cargo_volume_l"]): 
                "넓은 실내를 가진 전기 밴이나 SUV 중에서도 DC 급속 포트가 없는 모델이 존재합니다. 외부 활동이나 여행 시 꼭 필요한 기능이므로 꼼꼼히 확인해야 합니다.",

            frozenset(["battery_capacity_kWh", "range_km"]): 
                "일반적으로 배터리 용량이 큰 차량은 더 긴 주행거리를 자랑합니다. 하지만 모터 효율, 공기저항, 차량 무게 등의 요소도 주행거리에 영향을 미치므로, 같은 배터리 용량에서도 주행 가능 거리에 차이가 발생할 수 있습니다.",

            frozenset(["battery_capacity_kWh", "efficiency_wh_per_km"]): 
                "큰 배터리를 탑재한 차량은 일반적으로 무겁고 고출력인 경우가 많아 전비(Wh/km)는 낮을 수 있습니다. 하지만 고효율 플랫폼을 적용한 일부 고급 전기차는 높은 효율과 큰 배터리를 동시에 갖추고 있어, 효율성은 모델별로 반드시 비교가 필요합니다.",

            frozenset(["battery_capacity_kWh", "acceleration_0_100_s"]): 
                "배터리 용량이 크면 전압과 출력이 안정적으로 공급되어 가속 성능이 우수할 가능성이 있습니다. 하지만 고성능 구성이 부족한 대용량 저가 차량은 빠른 가속을 보장하지 않을 수 있어, 실제 성능을 확인하는 것이 중요합니다.",

            frozenset(["battery_capacity_kWh", "fast_charging_power_kw_dc"]): 
                "고용량 배터리를 가진 차량은 일반적으로 더 높은 급속 충전 성능을 갖추는 경향이 있습니다. 다만 충전 속도는 배터리 자체뿐 아니라 배터리 관리 시스템(BMS)의 설계에도 좌우되므로 스펙을 꼼꼼히 살펴야 합니다.",

            frozenset(["battery_capacity_kWh", "fast_charge_port"]): 
                "배터리 용량이 크더라도 DC 급속 충전 포트를 지원하지 않으면 충전 시간이 상당히 길어집니다. 장거리 주행을 고려한다면 단순한 배터리 크기보다 충전 포트 유무가 더 핵심적인 조건이 될 수 있습니다.",

            frozenset(["battery_capacity_kWh", "cargo_volume_l"]): 
                "SUV나 밴처럼 실내 공간이 넓은 차량은 종종 대형 배터리도 함께 장착하지만, 소형 차량도 바닥 공간을 활용해 중형급 배터리를 탑재할 수 있습니다. 따라서 적재 공간과 배터리 용량은 차량 유형에 따라 유연하게 설계됩니다.",

            frozenset(["battery_capacity_kWh", "top_speed_kmh"]): 
                "대용량 배터리는 고속에서도 지속적으로 높은 출력을 공급할 수 있어 최고 속도 성능 향상에 기여합니다. 하지만 최고속도는 차량 설계 철학에 따라 제한될 수 있어, 빠른 속도를 중시한다면 별도 확인이 필요합니다."

        }

        # 결과 반환
        return descriptions.get(pair, "해당 조합에 대한 정보가 없습니다.")




    # 🎛️ 대시보드 구조로 레이아웃 나누기
    col_filter, col_control, col_output = st.columns([1.5, 1.2, 3.3])

    with col_filter:
        st.markdown("### 🚗 필터 ①")
        selected_filters = generate_multiselect_filter(df, filter_column)
        filtered_df = return_filtered_df(df, selected_filters)
        # st.write("적용된 필터:")
        # st.dataframe(filtered_df, use_container_width=True, height=300)
        st.markdown("### 📊 축 선택 ②")
        if len(filtered_df) > 0 and axis_column:
            x_axis, y_axis = select_checkbox(axis_column)

        

    with col_control:
        
        st.markdown("### ✅ 브랜드 선택")
        brand_list = sorted(filtered_df["brand"].dropna().unique().tolist())
        selected_brands = []
        for brand in brand_list:
            if st.checkbox(brand, value=False, key=f"brand_{brand}"):
                selected_brands.append(brand)

    with col_output:
        st.markdown("### 📈 시각화 ③")
        brand_filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]
        if len(filtered_df) > 0 and axis_column and x_axis and y_axis and x_axis != "-- 축을 선택하세요 --" and y_axis != "-- 축을 선택하세요 --":

            if len(selected_brands) == 0 or len(brand_filtered_df) == 0:
                st.warning("선택된 브랜드가 없습니다. 하나 이상 선택해주세요.")

            else:
                fig = px.scatter(
                    brand_filtered_df,
                    x=x_axis,
                    y=y_axis,
                    color="brand",
                    hover_data=car_column + hover_column
                )
                fig.update_traces(
                    marker=dict(size=11)  # 모든 점 크기를 10으로 고정
                )
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(
                    f"""
                    <div style="
                        background-color: #FFF3E0;
                        padding: 15px 20px;
                        border-left: 5px solid #FFA726;
                        border-radius: 8px;
                        margin-bottom: 20px;
                        ">
                        <strong>💡 Tip:\n{get_ev_spec_relationship(x_axis, y_axis)}</strong><br>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                # st.write(get_ev_spec_relationship("range_km", "acceleration_0_100_s"))


        else:
            st.info("축과 브랜드를 모두 선택하면 그래프가 표시됩니다.")

    if len(filtered_df) > 0 and axis_column and x_axis and x_axis != "-- 축을 선택하세요 --":
      
        # 4. 시각화
        fig2 = px.histogram(
            brand_filtered_df,
            x=x_axis,
            color='brand',
            nbins=6,
            title=f'Brand Distribution by {eng_to_kor.get(x_axis, x_axis)}',
            labels={
                x_axis: f"{eng_to_kor.get(x_axis, x_axis)}",
                'count': '차량 수',
                'brand': '브랜드'
            },
            # hover_data=brand_filtered_df.columns
        )

        fig2.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        fig2.update_traces(
            marker_line_width=1,
            marker_line_color='white'
        )
        st.plotly_chart(fig2, use_container_width=True)


    if len(filtered_df) > 0 and axis_column and y_axis and y_axis != "-- 축을 선택하세요 --":
        fig3 = px.histogram(
            brand_filtered_df,
            x=y_axis,
            color='brand',
            nbins=6,
            title=f'Brand Distribution by {eng_to_kor.get(y_axis, y_axis)}',
            labels={
                x_axis: f"{eng_to_kor.get(y_axis, y_axis)}",
                'count': '차량 수',
                'brand': '브랜드'
            },
            # hover_data=brand_filtered_df.columns
        )

        fig3.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
        fig3.update_traces(
            marker_line_width=1,
            marker_line_color='white'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
    st.markdown("### 📈 차량 이미지 ④")
    brand_filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]
    # if len(filtered_df) > 0 and axis_column and x_axis and y_axis and x_axis != "-- 축을 선택하세요 --" and y_axis != "-- 축을 선택하세요 --":

    #     if len(selected_brands) == 0 or len(brand_filtered_df) == 0:
    #         st.warning("선택된 브랜드가 없습니다. 하나 이상 선택해주세요.")

    #     else:
    #         # images = brand_filtered_df['image_url'].values.tolist()
    #         # if len(images) > 0:
    #         #     index = st.slider("차량 이미지 넘기기", 0, len(images) - 1, 0)
    #         #     st.image(images[index], use_column_width=True)

    carousel(items=[dict(title=model, text=brand, img=image_url) for model, brand, image_url in brand_filtered_df[['model', 'brand', 'image_url']].values.tolist() if image_url != ''])
    
    # AI 추천 시스템 추가 (전체 데이터로 클러스터링, 필터된 데이터로 추천)
    try:
        cluster_data = prepare_clustering_data(df)
        display_cluster_recommendations_streamlit(cluster_data, filtered_df)
    except Exception as e:
        st.error(f"추천 시스템 오류: {str(e)}")

    with st.sidebar:
        st.markdown("### 🚗 필터링된 차량 목록")
        
        if len(filtered_df) == 0:
            st.warning("조건에 맞는 차량이 없습니다.")
        else:
            st.markdown(f"**총 {len(filtered_df)}대의 차량이 필터링됨**")
            # 브랜드와 모델만 보여주는 축약 리스트
            st.dataframe(
                filtered_df[["brand", "model"]],
                use_container_width=True,
                height=min(400, 40 + 25 * len(filtered_df))  # 표시 높이 유동 조절
            )

