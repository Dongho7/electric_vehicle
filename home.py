import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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
    axis_column = [col for col in df.columns if col not in filter_column + car_column + hover_column]

    def generate_multiselect_filter(df, filter_column) -> list:
        filtered_variable = []
        for filter_element in filter_column:
            options = sorted(df[filter_element].dropna().unique().tolist())
            default_value = [options[0]] if options else []
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

    # 🎛️ 대시보드 구조로 레이아웃 나누기
    col_filter, col_control, col_output = st.columns([1.5, 1.2, 3.3])

    with col_filter:
        st.markdown("### 🚗 필터")
        selected_filters = generate_multiselect_filter(df, filter_column)
        filtered_df = return_filtered_df(df, selected_filters)
        st.write("적용된 필터:")
        st.dataframe(filtered_df, use_container_width=True, height=300)

    with col_control:
        st.markdown("### 📊 축 선택")
        if len(filtered_df) > 0 and axis_column:
            x_axis, y_axis = select_checkbox(axis_column)

            st.markdown("### ✅ 브랜드 선택")
            brand_list = sorted(filtered_df["brand"].dropna().unique().tolist())
            selected_brands = []
            for brand in brand_list:
                if st.checkbox(brand, value=True, key=f"brand_{brand}"):
                    selected_brands.append(brand)

    with col_output:
        st.markdown("### 📈 시각화")
        
        if len(filtered_df) > 0 and axis_column and x_axis and y_axis and x_axis != "-- 축을 선택하세요 --" and y_axis != "-- 축을 선택하세요 --":
            brand_filtered_df = filtered_df[filtered_df["brand"].isin(selected_brands)]

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

        else:
            st.info("축과 브랜드를 모두 선택하면 그래프가 표시됩니다.")

    if len(filtered_df) > 0 and axis_column and x_axis and x_axis != "-- 축을 선택하세요 --":
        valid_series = filtered_df[x_axis].dropna()
        data_min = valid_series.min()
        data_max = valid_series.max()

        # 예쁜 숫자로 반올림
        rounded_min = np.floor(data_min / 10) * 10
        rounded_max = np.ceil(data_max / 10) * 10

        # 균등한 bin
        n_bins = 10
        bin_edges = np.linspace(rounded_min, rounded_max, n_bins + 1)

        # 안전하게 bin 적용
        filtered_df = filtered_df.dropna(subset=[x_axis])
        filtered_df['bin'] = pd.cut(filtered_df[x_axis], bins=bin_edges, include_lowest=True)
        filtered_df['bin'] = filtered_df['bin'].astype(str)

        # 3. 그룹핑
        grouped = filtered_df.groupby(['bin', 'brand'], observed=True).size().reset_index(name='count')

        # 4. 시각화
        fig2 = px.bar(
            grouped,
            x='bin',
            y='count',
            color='brand',
            title=f'Brand Distribution by {eng_to_kor.get(x_axis, x_axis)}',
            labels={
                'bin': f"{eng_to_kor.get(x_axis, x_axis)} 구간",
                'count': '차량 수',
                'brand': '브랜드'
            }
        )
        fig2.update_layout(
            xaxis_tickangle=-45,
            barmode='stack',
            height=500
        )
        st.plotly_chart(fig2, use_container_width=True)

    if len(filtered_df) > 0 and axis_column and y_axis and y_axis != "-- 축을 선택하세요 --":
        valid_series = filtered_df[y_axis].dropna()
        data_min = valid_series.min()
        data_max = valid_series.max()

        # 예쁜 숫자로 반올림
        rounded_min = np.floor(data_min / 10) * 10
        rounded_max = np.ceil(data_max / 10) * 10

        # 균등한 bin
        n_bins = 10
        bin_edges = np.linspace(rounded_min, rounded_max, n_bins + 1)

        # 안전하게 bin 적용
        filtered_df = filtered_df.dropna(subset=[y_axis])
        filtered_df['bin'] = pd.cut(filtered_df[y_axis], bins=bin_edges, include_lowest=True)
        filtered_df['bin'] = filtered_df['bin'].astype(str)

        # 3. 그룹핑
        grouped = filtered_df.groupby(['bin', 'brand'], observed=True).size().reset_index(name='count')

        # 4. 시각화
        fig3 = px.bar(
            grouped,
            x='bin',
            y='count',
            color='brand',
            title=f'Brand Distribution by {eng_to_kor.get(y_axis, y_axis)}',
            labels={
                'bin': f"{eng_to_kor.get(y_axis, y_axis)} 구간",
                'count': '차량 수',
                'brand': '브랜드'
            }
        )
        fig3.update_layout(
            xaxis_tickangle=-45,
            barmode='stack',
            height=500
        )
        st.plotly_chart(fig3, use_container_width=True)
        
