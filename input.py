import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
import common


def input():

    common.page_title('Data Entry')
    
    agencies_clients = common.get_agencies_list()

    agencies_list = []
    for k, v in agencies_clients.items():
        agencies_list.append(k)

    # load temp
    temp_collection = common.connect_to_collections('temp')
    temp_collection_count = temp_collection.count_documents({})    
    
    if 'in_hyperlink' not in st.session_state:
        st.session_state.in_hyperlink = ''
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.2, 0.55, 0.25], border=True)
        with col1:
            input_date = st.date_input(':calendar: **:violet[DATE]**', key='i_date', format='YYYY-MM-DD')
            input_date = datetime.combine(input_date, datetime.min.time())

            cola, colb = st.columns(2, border=True)
            with cola:
                input_captured = st.radio(
                    label='**:violet[CAPTURED]**',
                    options=['Yes', 'No'])

            with colb:
                radio_reqtype = st.radio(
                    label='**:violet[TYPE]**',
                    options=['Regular', 'Ad Hoc', 'TOA'])
           
        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                input_agency = st.selectbox(
                    label='Agency',
                    options=agencies_list,
                    key='in_agency',
                    accept_new_options=True)
                
            with col2b:
                    input_client = st.selectbox(
                    label='Client',
                    options=sorted(agencies_clients[input_agency]),
                    key='in_client',
                    accept_new_options=True)
            
            input_hyperlink = st.text_area('Hyperlink', key='in_hyperlink')
        
        with col3:
            btn_add = st.button('Add' , key='input_archive', use_container_width=True)                        
        
    with st.expander(label='Click to see details', expanded=True):
        
        cole1, cole2 = st.columns([0.75, 0.25])
        with cole1:
            # display data in dataframe
            docs = list(temp_collection.find({}, {'_id':0}))            
            df = pd.DataFrame(docs)
            if df.empty:
                st.write('No Data to display')
            else:
                df.index = df.index+1
                st.dataframe(df)
        with cole2:
            with st.container(border=True):
                if df.empty:
                    btn_submit = st.button(
                        label='Submit',
                        use_container_width=True,
                        disabled=True
                    )
                else:
                    btn_submit = st.button(
                        label='Submit',
                        use_container_width=True,
                        disabled=False
                    )
                record_no = st.selectbox(
                label='Record',
                options = list(range(1, temp_collection_count+1))
                )
                btn_delete = st.button(
                    label='Delete',
                    use_container_width=True
                )
                btn_delete_all = st.button(
                    label='Delete All',
                    use_container_width=True
                )
                
                
        

    if btn_add:

        # load tier data
        fqdn_collection = common.connect_to_collections('tier')
        fqdn_documents = fqdn_collection.find()
        
        with st.spinner('Adding Data', show_time=True):
                
            if input_captured == 'Yes':
                captured = 1
            elif input_captured == 'No':
                captured = 0

            if radio_reqtype=='Regular':
                reqtype = 1
            elif radio_reqtype=='Ad Hoc':
                reqtype = 2
            elif radio_reqtype=='TOA':
                reqtype = 3

            _hyperlinks = input_hyperlink.splitlines()
            data = []

            # create a blank dataframe
            df = pd.DataFrame(columns=['Date', 'Client', 'Tier', 'Url', 'Captured', 'fqdn', 'Agency', 'Ad Hoc'])
            
            for _hyperlink in _hyperlinks:
                if common.is_valid_url(_hyperlink) == True:
                    fqdn = common.get_fqdn(_hyperlink)
                    result = fqdn_collection.find_one({'fqdn':fqdn})
                    if result:
                        input_fqdn = result['fqdn']
                        input_tier = result['tier']
                    else:
                        input_fqdn = fqdn
                        input_tier = 0
                else:
                    st.error(f'Invalid URL - {_hyperlink}')
                    continue
                
                data = {
                    'DATE':input_date,
                    'CLIENT NAME':input_client.upper(),
                    'TIER':input_tier,
                    'LINK':_hyperlink,
                    'CAPTURED':captured,
                    'FQDN':input_fqdn,
                    'AGENCY':(str(input_agency)).upper(),
                    'TYPE':reqtype
                }

                # check if link exists
                if not temp_collection.find_one({'LINK':_hyperlink}):
                    result = temp_collection.insert_one(data)
                else:
                    st.toast('Record already exists!!!')

            del st.session_state['in_hyperlink']
            time.sleep(2)
        st.rerun()
        st.cache_data.clear()
                    
    if btn_submit:        

        with st.spinner('Sending Record', show_time=True):

            data_collection  = common.connect_to_collections('data')
            
            # count the documents stored in temp collection
            temp_count = temp_collection.count_documents({})

            # insert all the documents in temp collection to database collection
            data_collection.insert_many(temp_collection.find())
            st.toast(f'Added {temp_count} entries')

            # delete all documents from temp collection
            temp_collection.delete_many({})
        
        st.rerun()
        st.cache_data.clear()
    
    if btn_delete:
        with st.spinner('Deleting Record', show_time=True):
            data_to_delete = df.at[record_no,'LINK']
            temp_collection.delete_one({'LINK':data_to_delete})
            time.sleep(2)
        
        st.rerun()
        st.cache_data.clear()
    
    if btn_delete_all:
        with st.spinner('Deleting All Records', show_time=True):
            temp_collection.delete_many({})
            time.sleep(2)

        st.rerun()    
        st.cache_data.clear()