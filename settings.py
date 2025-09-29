import streamlit as st
from common import get_agencies_list, page_title


def settings(client):
    
    page_title('Settings')

    db = client['histo']
    collection = db['agencies']

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
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