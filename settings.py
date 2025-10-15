import streamlit as st
from common import get_agencies_list, page_title


def add_agency(client):

    db = client.histo
    collections = db.agencies

    with st.container(border=True, width=400):
        new_agency = st.text_input(
            label='New Agency'
        )

        if new_agency=='':
            add_btn_disabled = True
        else:
            add_btn_disabled = False

        add_btn = st.button(
            label='➕ **Add**',
            use_container_width=True,
            disabled=add_btn_disabled
        )
    
    if add_btn:
        # Check if agency already exists
        existing = collections.find_one({'AGENCY NAME': new_agency.upper()})

        if existing:
            st.toast(f"🚫 Agency '{new_agency}' already exists.")
        else:
            collections.insert_one(
                {
                    'AGENCY NAME': new_agency.upper(),
                    'CLIENTS': []
                }
            )                
            st.toast(f"👌 New Agency successfully added!!!")        


def add_client(client):

    db = client.histo
    collections = db.agencies
    agency_options = [doc['AGENCY NAME'] for doc in collections.find()]
    
    with st.container(border=True, width=400):
        selected_agency = st.selectbox(
            label='Agency',
            options=agency_options
        )

        new_client = st.text_input(
            label='New Client'
        )

        if new_client=='':
            btn_disabled = True
        else:
            btn_disabled = False

        add_btn = st.button(
            label='➕ **Add**',
            use_container_width=True,
            disabled=btn_disabled
        )
    
    if add_btn:
        document = collections.find_one({'AGENCY NAME':selected_agency})

        if new_client.upper() in document['CLIENTS']:
            st.toast(f"🚫 Agency '{new_client}' already exists.")
        else:
            collections.update_one(
                {'AGENCY NAME': selected_agency},
                {'$addToSet': {'CLIENTS': new_client.upper()}}
            )
            st.toast(f"👌 New Client successfully added!!!")


def delete_agency(client):

    db = client.histo
    collections = db.agencies
    agency_options = [doc['AGENCY NAME'] for doc in collections.find()]

    with st.container(border=True, width=400):
        for_delete_agency = st.selectbox(
            label='Agency',
            options=agency_options,
            key='for_delete_agency'
        )

        del_btn = st.button(
            label='**Delete**',
            use_container_width=True,            
        )
    
    if del_btn:
        collections.delete_one(
            {'AGENCY NAME':for_delete_agency}
        )
        st.toast(f"👌 {for_delete_agency} successfully deleted!!!")

def delete_client(client):

    db = client.histo
    collections = db.agencies
    agency_options = [doc['AGENCY NAME'] for doc in collections.find()]
    
    with st.container(border=True, width=400):
        agency_del = st.selectbox(
            label='Agency',
            options=agency_options,
            key='agency_del'
        )

        document = collections.find_one({'AGENCY NAME':agency_del})
        client_options = document['CLIENTS']
        
        client_del = st.selectbox(
            label='Client',
            options=client_options
        )

        del_btn = st.button(
            label='**Delete**',
            use_container_width=True
        )
    
    if del_btn:
        db.agencies.update_one(
            {'AGENCY NAME':agency_del},
            {'$pull':{'CLIENTS':client_del}}
        )
        st.toast(f"👌 {client_del} successfully deleted!!!")
    




def settings(client):
    
    page_title('Client Management')

    tab1, tab2 = st.tabs(['Add', 'Delete'], )

    with tab1:
        with st.container(border=True, width=400):
            entity = st.pills(
                label='Edit',
                options=['Agency', 'Client'],
                label_visibility='collapsed',
                width='stretch',
                default='Agency'
            )
        
            if entity=='Agency':
                add_agency(client)
            elif entity=='Client':
                add_client(client)
    
    with tab2:
        with st.container(border=True, width=400):
            _entity = st.pills(
                label='Edit',
                options=['Agency', 'Client'],
                label_visibility='collapsed',
                width='stretch',
                default='Agency',
                key='_entity'
            )
        
            if _entity=='Agency':
                delete_agency(client)
            elif _entity=='Client':
                delete_client(client)
        

    
    # exit()
    # db = client['histo']
    # collection = db['agencies']

    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     with st.container(border=True):
    #         agency_count = len(get_agencies_list(client))

    #         selectd_agency = st.selectbox(
    #             label=f'Existing Agencies ({agency_count})',
    #             options=get_agencies_list(client)
    #         )

    #         new_agency = st.text_input(
    #             label='New Agency',
    #             placeholder='Enter new agency to add'
    #         )

    #         if new_agency=='':
    #             add_agency_btn = st.button(
    #                 label='Add',
    #                 use_container_width=True,
    #                 disabled=True,
    #                 key='hidden_add_agency_btn'
    #             )
    #         else:
    #             add_agency_btn = st.button(
    #                 label='Add',
    #                 use_container_width=True,
    #                 disabled=False,
    #                 key='visible_add_agency_btn'
    #             )


    #     # add client menu
    #     with st.container(border=True):
    #         new_client = st.text_input(
    #             label='New Client',
    #             placeholder='Enter new client to add'
    #         )

    #         if new_client=='':
    #             add_client_btn = st.button(
    #                 label='Add',
    #                 use_container_width=True,
    #                 disabled=True,
    #                 key='hidden_add_client_btn'
    #             )
    #         else:
    #             add_client_btn = st.button(
    #                 label='Add',
    #                 use_container_width=True,
    #                 disabled=False,
    #                 key='visible_add_client_btn'
    #             )


    #     # delete client menu
    #     with st.container(border=True):
            
    #         document = collection.find_one({'AGENCY NAME':selectd_agency})
    #         # items = '\n'.join(document['CLIENTS'])
    #         client_count = len(document['CLIENTS'])               
            
    #         existing_clients = st.selectbox(
    #             label=f'Existing Clients ({client_count})',
    #             options=sorted(document['CLIENTS'])
    #         )

    #         if client_count > 0:
    #             delete_client_btn = st.button(
    #                 label='Delete',
    #                 use_container_width=True,
    #                 disabled=False,
    #                 key='hidden_delete_client_btn'
    #             )
    #         else:
    #             delete_client_btn = st.button(
    #                 label='Delete',
    #                 use_container_width=True,
    #                 disabled=True,
    #                 key='visible_delete_client_btn'
    #             )
        
    # if add_agency_btn:

    #     # Check if agency already exists
    #     existing = collection.find_one({'AGENCY NAME': new_agency.upper()})

    #     if existing:
    #         st.toast(f"🚫 Agency '{new_agency}' already exists.")
    #     else:
    #         collection.insert_one(
    #             {
    #                 'AGENCY NAME': new_agency.upper(),
    #                 'CLIENTS': []
    #             }
    #         )                
    #         st.toast(f"👌 New Agency successfully added!!!")

    #     st.rerun()


    # if add_client_btn:

    #     if new_client.upper() in document['CLIENTS']:
    #         st.toast(f"🚫 Agency '{new_client}' already exists.")
    #     else:
    #         collection.update_one(
    #             {'AGENCY NAME': selectd_agency},
    #             {'$addToSet': {'CLIENTS': new_client.upper()}}
    #         )
    #         st.toast(f"👌 New Client successfully added!!!")

    #     st.rerun()

    # if delete_client_btn:

    #     collection.update_one(
    #         {'AGENCY NAME':selectd_agency},
    #         {'$pull':{'CLIENTS':existing_clients}}
    #     )

    #     st.toast(f"👌 Client successfully removed!!!")

    #     st.rerun()