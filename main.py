import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
from PIL import Image
import requests
from io import BytesIO
from common import connect_to_mongodb

from archive import archive
from input import input
from summary import summary
from settings import settings

@st.cache_resource
def get_logo():

    url = "https://i.ibb.co/JRW19H4Y/AShinra-Logo.png"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    image = Image.open(BytesIO(response.content))

    return image

@st.cache_resource
def get_bgimage():

    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
    background-image: url("https://i.ibb.co/8D4hLbSX/natural-light-white-background.jpg");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;}</style>"""

    st.markdown(background_image, unsafe_allow_html=True)

    return


def main(username, rights):
# if __name__ == "__main__":

    client = connect_to_mongodb()

    # get_bgimage()

    hide_streamlit_style = """<style>
    ._profileContainer_gzau3_63{display: none;}
    </style>"""
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)    


    st.set_page_config(
        layout="wide",
        page_title='HISTO')
    
    # hide streamlit toolbar
    st.markdown("""<style>[data-testid="stToolbar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.markdown("""<style>[data-testid="manage-app-button"] {display: none !important;}</style>""", unsafe_allow_html=True)
    st.markdown("""<style>.stApp {background-image: url("https://i.ibb.co/8D4hLbSX/natural-light-white-background.jpg");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;}</style>""", unsafe_allow_html=True)
    
    try:
        st.sidebar.image(get_logo())
    except FileNotFoundError:
        st.sidebar.write("Image file not found. Please check the path.")

    with st.sidebar:

        if rights=='admin':
            options_list=['Entry', 'Archive', 'Summary', 'Settings']
            icons_list=['pencil-square', 'archive', 'journals', 'gear']
        else:
            options_list=['Archive', 'Summary']
            icons_list=['archive', 'journals']

        st.sidebar.header(f':red[Welcome :blue[*{username.title()}*]] 👤')
        selected = option_menu(
            menu_title='Request History',
            menu_icon='clock-history',
            options=options_list,
            icons=icons_list
        )
        btn_clearcache = st.button('Clear Cache', use_container_width=True)
    
    client_list = []
    if selected == 'Entry':
        input(client, client_list)
    
    if selected == 'Archive':
        archive(client)
    
    if selected == 'Summary':
        summary(client)
    
    if selected == 'Settings':
        settings(client)

    if btn_clearcache:
        st.cache_data.clear()
    
    

