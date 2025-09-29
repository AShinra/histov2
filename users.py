import streamlit as st
from common import has_upper_and_number, page_title
from argon2 import PasswordHasher


def user_management(client):
    # user management
    page_title('User Management')

    db = client.histo
    users = db.users

    ph = PasswordHasher()  # default parameters are sensible; tune if needed

    col2a, col2b, col2c = st.columns(3)
    
    with col2a:
        with st.container(border=True):
            username = st.text_input(
                label='Username',
                key='entry_username'

            )
            password = st.text_input(
                label='Password',
                type='password',
                key='entry_password',
                help='Minimum of 8 characters with an uppercase letter and number'
            )
            name = st.text_input(
                label='Name',
                key='entry_name'
            )
            
        if st.session_state.entry_username=='' or st.session_state.entry_password=='' or st.session_state.entry_name=='':
            rights_disabled=True
            btn_disabled=True
        else:
            rights_disabled=False
            btn_disabled=False

        rights = st.selectbox(
            label='Rights',
            options=['admin', 'user'],
            disabled=rights_disabled,
        )
        submit_user_btn = st.button(
            label='Submit',
            use_container_width=True, 
            disabled=btn_disabled,
        )
    
    if submit_user_btn:
        has_upper, has_number, text_length = has_upper_and_number(password)

        if has_upper and has_number and text_length:
            pw_hash = ph.hash(password)
            users.insert_one({
                "username": username,
                "name": name,
                "password_hash": pw_hash,
                "rights": rights
                })
            st.success(f'{username} successfully enrolled')
        elif has_upper==False:
            st.error('Should contain an uppercase letter')
        elif has_number==False:
            st.error('Should contain a number')
        elif text_length==False:
            st.error('Should have a minimum of 8 characters')
        st.rerun()
