import streamlit as st
from common import connect_to_mongodb
from argon2 import PasswordHasher
from main import main, get_logo


if __name__ == '__main__':

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
            if st.button("Logout", use_container_width=True):
                st.session_state.logged_in = False
                st.rerun()
    else:
        with st.sidebar:
            username = st.text_input(
                label="Username",
                key='login_username')
            password = st.text_input(
                label="Password",
                type="password",
                key='login_password')
            submit_btn = st.button(
                label='Submit',
                use_container_width=True,
                key='login_submit_btn'
            )

    
        if submit_btn:
            doc = collection.find_one({"username": username})
            if not doc:
                st.error("No such user")
            else:
                try:
                    ph.verify(doc["password_hash"], password)
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.rights = doc['rights']
                    st.rerun()
                except Exception:
                    st.error("Wrong password")
    
        
