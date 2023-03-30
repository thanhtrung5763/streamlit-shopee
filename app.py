import requests
import app_helper
import streamlit as st
from streamlit_option_menu import option_menu

from general_page import general
from shop_page import shop_page

import plotly.io as pio
pio.templates.default = "plotly_dark"
def menu_side_bar():
    with st.sidebar:
        menu = option_menu(
            menu_title='Main Menu',
            menu_icon='bar-chart-line-fill',
            options=['General', 'Shop Info', 'Product Info'],
            icons=['emoji-sunglasses-fill',
                   'emoji-expressionless-fill', 'emoji-smile-fill'],
            default_index=0,
            styles={
                "icon": {"font-size": "25px"},
                "nav-link-selected": {"background-color": "#636EFA"},
            }
        )
        return menu

def main():
    df = app_helper.get_data(
        '/shopee-streamlit/data_with_tag_parquet', type='parquet')

    menu = menu_side_bar()

    if menu == 'General':
        ### --- GENERAL PAGE ---###
        general(df)
    elif menu == 'Shop Info':
        ### --- SHOP INFO PAGE ---###
        shop_page(df)
    elif menu == 'Product Info':
        def load_lottieurl(url):
            r = requests.get(url)
            if r.status_code != 200:
                return None
            return r.json()
        from streamlit_lottie import st_lottie
        lottie_404_url = 'https://assets3.lottiefiles.com/packages/lf20_9Fhz02H45R.json'
        lottie_404 = load_lottieurl(lottie_404_url)
        st_lottie(lottie_404, height=800)


if __name__ == '__main__':
    st.set_page_config(page_title=f"Shopee Streamlit",
                       page_icon=":bar_chart:", layout="wide")
    with open('main.css') as style:
        st.markdown(f'<style>{style.read()}</style>', unsafe_allow_html=True)
    main()
# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
