import streamlit as st
import home
from streamlit_option_menu import option_menu


class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        with st.sidebar:
            app = option_menu(
                menu_title="Electric Vehicle ",
                options=["찾기", "기타 시각화", "개발자"],
                icons=[
                    "house-fill",
                    "person-circle",
                    "chat-fill",
                    "info-circle-fill",
                ],
                menu_icon="chat-text-fill",
                default_index=1,
                styles={
                    "container": {
                        "padding": "5!important",
                        "background-color": "black",
                    },
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {
                        "color": "white",
                        "font-size": "20px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "blue",
                    },
                    "nav-link-selected": {"background-color": "#02ab21"},
                    "menu-title": {"color":"white"}
                },
            )

        if app == "찾기":
            home.app()
        # if app == "기타 시각화":
        #     test.app()
        # if app == "개발자":
        #     about.app()

if __name__ == "__main__":
    multi_app = MultiApp()
    multi_app.run()