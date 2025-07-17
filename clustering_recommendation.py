import streamlit as st
import pandas as pd
import numpy as np

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

# 사용 예시 함수
def add_clustering_to_streamlit_app(df, filtered_df):
    """
    기존 Streamlit 앱에 클러스터링 추천 기능을 추가하는 함수
    
    Parameters:
    df: 전체 데이터프레임
    filtered_df: 필터링된 데이터프레임
    
    사용법:
    from clustering_recommendation import add_clustering_to_streamlit_app
    add_clustering_to_streamlit_app(df, filtered_df)
    """
    # 클러스터링 데이터 준비
    cluster_data = prepare_clustering_data(df)
    
    # AI 추천 시스템 표시
    display_cluster_recommendations_streamlit(cluster_data, filtered_df)

if __name__ == "__main__":
    # 테스트용 코드
    st.title("전기차 클러스터링 추천 시스템 테스트")
    
    # 샘플 데이터 로드 (실제 사용 시에는 실제 데이터 경로로 변경)
    try:
        df = pd.read_csv('./dropped_df_processed.csv')
        cluster_data = prepare_clustering_data(df)
        display_cluster_recommendations_streamlit(cluster_data, df)
    except FileNotFoundError:
        st.error("데이터 파일을 찾을 수 없습니다. 파일 경로를 확인해주세요.")
