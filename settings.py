import streamlit as st
from common import get_agencies_list, has_upper_and_number
from argon2 import PasswordHasher


def settings(client):
    
    st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1rem; /* Adjust this value as needed (e.g., 0rem for minimal padding) */
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)
    st.title(":violet[Settings]")

    db = client['histo']
    collection = db['agencies']

    tab1, tab2, tab3 = st.tabs(['Modify Agency', 'User Management', 'Tab3'])


    # -----Add company tab-----
    with tab1:

        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border=True):
            # Initialize state
            # if "text" not in st.session_state:
            #     st.session_state.text = ""
                agency_count = len(get_agencies_list(client))

                selectd_agency = st.selectbox(
                    label=f'Existing Agencies ({agency_count})',
                    options=get_agencies_list(client)
                )

                new_agency = st.text_input(
                    label='New Agency',
                    placeholder='Enter new agency to add'
                )

                if new_agency=='':
                    add_agency_btn = st.button(
                        label='Add',
                        use_container_width=True,
                        disabled=True,
                        key='hidden_add_agency_btn'
                    )
                else:
                    add_agency_btn = st.button(
                        label='Add',
                        use_container_width=True,
                        disabled=False,
                        key='visible_add_agency_btn'
                    )


            # add client menu
            with st.container(border=True):
                new_client = st.text_input(
                    label='New Client',
                    placeholder='Enter new client to add'
                )

                if new_client=='':
                    add_client_btn = st.button(
                        label='Add',
                        use_container_width=True,
                        disabled=True,
                        key='hidden_add_client_btn'
                    )
                else:
                    add_client_btn = st.button(
                        label='Add',
                        use_container_width=True,
                        disabled=False,
                        key='visible_add_client_btn'
                    )


            # delete client menu
            with st.container(border=True):
                
                document = collection.find_one({'AGENCY NAME':selectd_agency})
                # items = '\n'.join(document['CLIENTS'])
                client_count = len(document['CLIENTS'])               
                
                existing_clients = st.selectbox(
                    label=f'Existing Clients ({client_count})',
                    options=sorted(document['CLIENTS'])
                )

                if client_count > 0:
                    delete_client_btn = st.button(
                        label='Delete',
                        use_container_width=True,
                        disabled=False,
                        key='hidden_delete_client_btn'
                    )
                else:
                    delete_client_btn = st.button(
                        label='Delete',
                        use_container_width=True,
                        disabled=True,
                        key='visible_delete_client_btn'
                    )
            
        if add_agency_btn:

            # Check if agency already exists
            existing = collection.find_one({'AGENCY NAME': new_agency.upper()})

            if existing:
                st.toast(f"🚫 Agency '{new_agency}' already exists.")
            else:
                collection.insert_one(
                    {
                        'AGENCY NAME': new_agency.upper(),
                        'CLIENTS': []
                    }
                )                
                st.toast(f"👌 New Agency successfully added!!!")

            st.rerun()
    

        if add_client_btn:

            if new_client.upper() in document['CLIENTS']:
                st.toast(f"🚫 Agency '{new_client}' already exists.")
            else:
                collection.update_one(
                    {'AGENCY NAME': selectd_agency},
                    {'$addToSet': {'CLIENTS': new_client.upper()}}
                )
                st.toast(f"👌 New Client successfully added!!!")

            st.rerun()

        if delete_client_btn:

            collection.update_one(
                {'AGENCY NAME':selectd_agency},
                {'$pull':{'CLIENTS':existing_clients}}
            )

            st.toast(f"👌 Client successfully removed!!!")

            st.rerun()



    with tab2:
        # user management
        ph = PasswordHasher()  # default parameters are sensible; tune if needed
        users = db.users

        col2a, col2b, col2c = st.columns(3)
        
        with col2a:
            with st.container(border=True):
                
                st.write(st.session_state.setting)
        
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
            st.session_state.setting = True
            st.rerun()