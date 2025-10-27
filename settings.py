import streamlit as st
import common

def add_agency():
    # connect to agencies collection
    collections = common.connect_to_collections('agencies')

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


def add_client():

    # connect to agencies collection
    collections = common.connect_to_collections('agencies')
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

        st.cache_data.clear()


def delete_agency():

    # connect to agencies collection
    collections = common.connect_to_collections('agencies')
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
        st.cache_data.clear()

def delete_client():

    # connect to agencie collection
    collections = common.connect_to_collections('agencies')
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
        collections.update_one(
            {'AGENCY NAME':agency_del},
            {'$pull':{'CLIENTS':client_del}}
        )
        st.toast(f"👌 {client_del} successfully deleted!!!")
        st.cache_data.clear()
    


def settings():
    
    common.page_title('Client Management')

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
                add_agency()
            elif entity=='Client':
                add_client()
    
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
                delete_agency()
            elif _entity=='Client':
                delete_client()