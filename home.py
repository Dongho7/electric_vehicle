import streamlit as st
import pandas as pd

def app():
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

    
    


    df = pd.read_csv("C:\\ITstudy\\01_python\\01_electric_vehichle\\dropped_df_processed_encoded.csv") 
    st.dataframe(df)

    selected_drivetrain = st.multiselect('Multiselect', ["FWD", "RWD", "AWD"])

    if selected_drivetrain:
        filtered_df = df[df["drivetrain"].isin(selected_drivetrain)]
        st.dataframe(filtered_df)
        st.dataframe(filtered_df["drivetrain"].value_counts())
    else:
        st.write("구동 방식을 선택해주세요.")


    selected_carbody_type = st.multiselect('Multiselect', ['세단', 'SUV', '승합차', '스포츠카'])
    if selected_carbody_type:
        filtered_df = filtered_df[filtered_df["car_body_type"].isin(selected_carbody_type)]
        st.dataframe(filtered_df)
        st.dataframe(filtered_df["car_body_type"].value_counts())
    else:
        st.write("차종을 선택해주세요.")


    selected_carsize = st.multiselect('Multiselect', ['소형', '준중형', '준대형', '중형', '대형', '승합차', '초소형', '스포츠카'])
    if selected_carsize:
        filtered_df = filtered_df[filtered_df["car_size"].isin(selected_carsize)]
        st.dataframe(filtered_df)
        st.dataframe(filtered_df["car_size"].value_counts())
    else:
        st.write("차 사이즈를 선택해주세요.")






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





