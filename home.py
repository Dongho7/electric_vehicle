import streamlit as st
import pandas as pd


def app(df):
    st.subheader("나에게 맞는 전기차 찾기")
    st.subheader("")
    image = 'log.png'

    hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(image)
        
    st.write("hello")

    filter_column = ['car_size', 'drivetrain', 'car_body_type']  # 필터 변수
    car_column = ['brand', 'model']  # 고정 값
    axis_column = [col_name for col_name in df.columns if col_name not in filter_column + car_column]  # 축 변수
    

    def generate_multiselect_filter(df, filter_column) -> list:
        '''
        "필터"용으로 지정된 column 에 대해서 복수 선택이 가능한
        multiselect UI 생성
        '''
        filtered_variable = []
        for filter_element in filter_column:
            selected = st.multiselect(
                f'{filter_element} 를 한개 이상 골라주세요',
                options=df[filter_element].unique().tolist()
            )
            filtered_variable.append((filter_element, selected))
        return filtered_variable

    def return_filtered_df(df: pd.DataFrame, filter_zip: list) -> pd.DataFrame:
        '''
        선택된 필터 기준으로 DataFrame 필터링
        df = 전체 df
        filter_zip = ['차종', ['SUV', '헷지백']]
        '''
        for col, selected_values in filter_zip:
            if selected_values:  # 선택된 값이 있다면 필터 적용
                df = df[df[col].isin(selected_values)]
        return df


    def 반전(x, y):
        '''
        버튼 x y 축 칼럼명 반전
        '''

    # 체크박스 (축 선택 x, y)
    def select_checkbox(axis_column):
        '''
        인풋 : [칼럼명, 칼럼명]
        return : x : 칼럼명 선택 1, y : ㅋ
        '''
        return x, y






############# 실행 ##################

    selected_filters = generate_multiselect_filter(df, filter_column)

    # 필터링된 DataFrame 생성
    filtered_df = return_filtered_df(df, selected_filters)

    # 결과 출력
    st.write("적용된 필터:", selected_filters)
    st.dataframe(filtered_df)


################
#### 참고용 #####
    st.slider('Slide me', min_value=0, max_value=10)

    st.select_slider('Slide to select', options=[1,'2'])

    st.text_input('Enter Article')

    st.number_input('Enter required number')

    st.text_area('Entered article text')

    st.date_input('Select date')

    st.time_input('Select Time')

    st.file_uploader('File CSV uploader')

    data= "hello"


    if data:= st.camera_input("Click a Snap"): 
        st.download_button('Download Source data', data, "my.png")

    st.color_picker('Pick a color')



    #출력 
    st.text('Tushar-Aggarwal.com')
    st.markdown('[Tushar-Aggarwal.com](https://tushar-aggarwal.com)')
    st.caption('Success')
    st.latex(r''' e^{i\pi} + 1 = 0 ''')
    st.write('Supreme Applcations by Tushar Aggarwal')
    st.write(['st', 'is <', 3]) # see *
    st.title('Streamlit Magic Cheat Sheets')
    st.header('Developed by Tushar Aggarwal')
    st.subheader('visit tushar-aggarwal.com')
    st.code('for i in range(8): print(i)')
    st.image('https://i.imgur.com/t2ewhfH.png')
    # * optional kwarg unsafe_allow_html = Trues





