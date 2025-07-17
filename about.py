import streamlit as st

def app(df=None):
    st.set_page_config(layout="wide")
    st.title("📘 프로젝트 소개")

    st.markdown("""
    ## ⚡ 전기차 스펙 비교 플랫폼

    이 웹 애플리케이션은 다양한 **전기차(EV)** 모델의 성능 데이터를  
    **시각적으로 비교**하고, 브랜드별 특징을 **인터랙티브하게 탐색**할 수 있도록 설계되었습니다.

    ---

    ### 🚗 주요 기능
    - 브랜드별 차량 분포 히스토그램
    - 성능 및 스펙 기준 비교 (속도, 주행 거리, 효율 등)
    - 한글 라벨 및 사용자 친화적 시각화
    - 모델별 상세 스펙 hover 정보 제공

    ---

    ### 📊 사용된 기술 스택
    - **Python / Pandas / Plotly**
    - **Streamlit**
    - CSV 기반 데이터 전처리 및 시각화

    ---

    ### 👤 제작자
    - 개발자: *양다현 신동호 배시훈 박홍준*
    - GitHub: [🔗 Repository 링크](https://github.com/Dongho7/electric_vehicle)

    ---
    """)