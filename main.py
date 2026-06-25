import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
from PIL import Image
import requests
from io import BytesIO
from common import get_logo, get_bgimage, connect_to_mongodb, get_agencies_list

from archive import archive
from input import input
from summary import summary
from settings import settings
from users import user_management
from team_monitor import team_monitor
from upload_monitor import upload_monitor

# get_logo()
get_bgimage()

def main(username, rights):
# if __name__ == "__main__":

    # get agencies_clients dict
    agencies_clients = get_agencies_list()
    
    # Ruby Charcoal Twilight theme for main content with small caps
    main_theme = """<style>
    /* Small caps font */
    * {
        font-variant: small-caps;
        font-weight: 600;
    }
    
    [data-testid="stHeader"] {display: none;}
    
    .stSidebar [data-testid="stMarkdownContainer"] h1 {
        color: #C41E3A !important;
    }
    
    .stSidebar .stMarkdown {
        color: #F5F1E8 !important;
    }
    
    .option-menu {
        background-color: #36454F !important;
    }
    
    .option-menu button {
        color: #F5F1E8 !important;
    }
    
    .option-menu button:hover {
        background-color: #8B7BA8 !important;
    }
    </style>"""
    st.markdown(main_theme, unsafe_allow_html=True)

    with st.sidebar:

        if rights=='admin':
            options_list=['Entry', 'Archive', 'Summary', 'Client Management', 'User Management']
            icons_list=['pencil-square', 'archive', 'journals', 'gear', 'people-fill']
        elif rights=='sub-admin':
            options_list=['Entry', 'Archive', 'Summary', 'Client Management']
            icons_list=['pencil-square', 'archive', 'journals', 'gear']
        else:
            options_list=['Archive', 'Summary']
            icons_list=['archive', 'journals']

        st.sidebar.header(f'Welcome **{username.title()}** 👤')
        selected = option_menu(
            menu_title='Online Monitoring',
            menu_icon='clock-history',
            options=options_list,
            icons=icons_list
        )
        btn_clearcache = st.button('🔄 **Reset**', width='stretch')
    
    client_list = []
    if selected == 'Entry':
        input()
    
    if selected == 'Archive':
        archive()
    
    if selected == 'Summary':
        summary()
    
    if selected == 'Client Management':
        settings()
    
    if selected == 'User Management':
        user_management()
    
    # if selected == 'Team Monitor':
    #     team_monitor()
    
    # if selected == 'Upload Monitor':
    #     upload_monitor()

    if btn_clearcache:
        st.cache_data.clear()
        # st.cache_resource.clear()
    
    

