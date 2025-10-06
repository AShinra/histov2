import streamlit as st
from common import connect_to_mongodb
from argon2 import PasswordHasher
from main import main, get_logo


if __name__ == '__main__':

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
    st.markdown("""<style>[data-testid="stSidebarCollapseButton"] {display: none !important;}</style>""", unsafe_allow_html=True)
    st.markdown("""<style>[data-testid="stSidebarHeader"] {height: 1rem;}</style>""", unsafe_allow_html=True)
    st.markdown("""<style>.stSidebar.st-emotion-cache-1legitb {background-color: black;}</style>""", unsafe_allow_html=True)
    
    try:
        st.sidebar.image(get_logo())
    except FileNotFoundError:
        st.sidebar.write("Image file not found. Please check the path.")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if 'username' not in st.session_state:
        st.session_state.username = ''
    
    if 'rights' not in st.session_state:
        st.session_state.rights = ''
    
    ph = PasswordHasher()
    client = connect_to_mongodb()
    db = client['histo']
    collection = db['users']

    if st.session_state.logged_in:
        main(st.session_state.username, st.session_state.rights)
        with st.sidebar:
            if st.button(":orange[**Log Out**]", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
    else:
        with st.sidebar:
            username = st.text_input(
                label=":orange[**USERNAME**]",
                key='login_username')
            password = st.text_input(
                label=":orange[**PASSWORD**]",
                type="password",
                key='login_password')
            submit_btn = st.button(
                label=':orange[**LOGIN**]',
                use_container_width=True,
                key='login_submit_btn'
            )

        if submit_btn:
            doc = collection.find_one({"username": username})
            if not doc:
                st.sidebar.error("No such user")
            else:
                try:
                    ph.verify(doc["password_hash"], password)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.rights = doc['rights']
                    st.rerun()
                except Exception:
                    st.sidebar.error("Wrong password")
    
        
