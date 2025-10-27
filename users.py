import streamlit as st
import common
from argon2 import PasswordHasher

def add_user():
    # add user
    users = common.connect_to_collections('users')

    ph = PasswordHasher()  # default parameters are sensible; tune if needed
    
    with st.container(border=True, width=400):
        st.subheader("👤 User Details")
        st.divider()
        username = st.text_input("**Username**", key='entry_username')
        password = st.text_input("**Password**", type="password", key='entry_password')
        name = st.text_input("**Name**", key='entry_name')
        
        if st.session_state.entry_username=='' or st.session_state.entry_password=='' or st.session_state.entry_name=='':
            rights_disabled=True
            btn_disabled=True
        else:
            rights_disabled=False
            btn_disabled=False

        rights = st.selectbox("**Rights**", ['admin', 'sub-admin', 'user'], disabled=rights_disabled)
        add_user_btn = st.button("➕ **Add**", use_container_width=True, disabled=btn_disabled)

    if add_user_btn:
        has_upper, has_number, text_length = common.has_upper_and_number(password)

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


def edit_user():
    # edit user
    users = common.connect_to_collections('users')

    # get the users from the db.users
    documents = users.find()
    user_options = [doc['username'] for doc in users.find()]
        
    ph = PasswordHasher()  # default parameters are sensible; tune if needed

    with st.container(border=True, width=400):
        st.subheader("👤 User Details")
        st.divider()

        edit_user = st.selectbox(
            label='**Username**',
            options=user_options
        )
        for_edit = st.pills(
            label='Edit',
            options=['Password', 'Username'],
            width='stretch',
            default='Password'
        )

        if for_edit=='Password':
            st.text_input(
                label='New Password',
                type='password',
                key='new_password'
            )
        elif for_edit=='Username':
            st.text_input(
                label='New Username',
                key='new_username'
            )
        
        edit_btn = st.button(
            label='Edit'
        )

        if edit_btn:
            if for_edit=='Password':
                # re hash the newpassword
                has_upper, has_number, text_length = common.has_upper_and_number(st.session_state.new_password)
                if has_upper and has_number and text_length:
                    pw_hash = ph.hash(st.session_state.new_password)
                    # Update one document where username = "athan"
                    users.update_one({"username": edit_user}, {"$set": {"password_hash": pw_hash}})
                    st.success('Password successfully modified')
                else:
                    st.error('Must contain An uppercase, number and more than 8 characters long')
        
            elif for_edit=='Username':
                users.update_one({'username': edit_user}, {'$set': {'username':st.session_state.new_username}})
                st.success('Username successfully modified')


def user_management():
    # user management
    common.page_title('User Management')

    tab1, tab2 = st.tabs(['**Add User**', '**Edit User**'])

    with tab1:
        add_user()
    with tab2:
        edit_user()