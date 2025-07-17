import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from streamlit_carousel import carousel

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
        pair = frozenset([x_axis.lower(), y_axis.lower()])

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
                "넓은 실내를 가진 전기 밴이나 SUV 중에서도 DC 급속 포트가 없는 모델이 존재합니다. 외부 활동이나 여행 시 꼭 필요한 기능이므로 꼼꼼히 확인해야 합니다."
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
                        데이터 시각화 전에 null 값을 반드시 처리하세요!
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
    if len(filtered_df) > 0 and axis_column and x_axis and y_axis and x_axis != "-- 축을 선택하세요 --" and y_axis != "-- 축을 선택하세요 --":

        if len(selected_brands) == 0 or len(brand_filtered_df) == 0:
            st.warning("선택된 브랜드가 없습니다. 하나 이상 선택해주세요.")

        else:

            images = brand_filtered_df['image_url'].values.tolist()
            index = st.slider("차량 이미지 넘기기", 0, len(images) - 1, 0)
            st.image(images[index], use_column_width=True)

    carousel(items=[dict(title=model, text=brand, img=image_url) for model, brand, image_url in brand_filtered_df[['model', 'brand', 'image_url']].values.tolist() if image_url != ''])


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