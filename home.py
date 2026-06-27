import streamlit as st
import common
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
    
    # Ruby Charcoal Twilight global theme styling with small caps
    theme_style = """<style>
    :root {
        --primary: #C41E3A;
        --dark: #1A1A2E;
        --charcoal: #36454F;
        --twilight: #8B7BA8;
        --light: #F5F1E8;
    }
    
    /* Small caps font for entire application */
    * {
        font-variant: small-caps !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }
    
    /* Hide streamlit toolbar */
    [data-testid="stToolbar"] {display: none;}
    [data-testid="manage-app-button"] {display: none !important;}
    [data-testid="stSidebarCollapseButton"] {display: none !important;}
    [data-testid="stSidebarHeader"] {height: 1rem;}
    
    /* Sidebar theme */
    .stSidebar {
        background-color: #1A1A2E !important;
        border-right: 2px solid #8B7BA8 !important;
    }
    
    /* Main content styling */
    .main {
        background-color: #1A1A2E !important;
        color: #F5F1E8 !important;
    }
    
    /* Text inputs styling */
    .stTextInput input, .stTextArea textarea {
        background-color: #36454F !important;
        color: #F5F1E8 !important;
        border: 1px solid #8B7BA8 !important;
    }
    
    /* Button styling */
    button[kind="primary"] {
        background-color: #C41E3A !important;
        color: #F5F1E8 !important;
    }
    button[kind="primary"]:hover {
        background-color: #A01A30 !important;
    }
    
    /* Header styling */
    h1, h2, h3, h4, h5, h6 {
        color: #C41E3A !important;
    }
    
    /* Accent color for orange elements */
    .stMarkdown [style*="orange"] {
        color: #C41E3A !important;
    }

    div[data-testid="stTextInput"] label {
    color: white !important;
    }

    </style>"""
    st.markdown(theme_style, unsafe_allow_html=True)
    
    # try:
    #     st.sidebar.image(get_logo())
    # except FileNotFoundError:
    #     st.sidebar.write("Image file not found. Please check the path.")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if 'username' not in st.session_state:
        st.session_state.username = ''
    
    if 'rights' not in st.session_state:
        st.session_state.rights = ''
    
    ph = PasswordHasher()
    user_collection = common.connect_to_collections('users')

    if st.session_state.logged_in:
        main(st.session_state.username, st.session_state.rights)
        with st.sidebar:
            if st.button("🚪 **Log Out**", width='stretch'):
                st.session_state.logged_in = False
                st.rerun()
    else:
        with st.sidebar:
            username = st.text_input(
                label="👤 **USERNAME**",
                key='login_username')
            password = st.text_input(
                label="🔐 **PASSWORD**",
                type="password",
                key='login_password')
            submit_btn = st.button(
                label='✅ **LOGIN**',
                width='stretch',
                key='login_submit_btn'
            )

        if submit_btn:
            doc = user_collection.find_one({"username": username})
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
            
            st.cache_data.clear()
    
        
