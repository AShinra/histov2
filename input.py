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
    
    # ===== INPUT FORM SECTION =====
    main_cols = st.columns(2, gap='small')
    with main_cols[0]:
        st.subheader('📝 Entry Form')
        with st.container(border=True):
            
            st.markdown('**Basic Information**')
            sub_cols = st.columns([3.5, 6.5], gap='small')
            with sub_cols[0]:
                verified_by = st.selectbox(
                    label='Verifier',
                    options=['Joel','Mary', 'Terence', 'Virna'],
                    key='verified_by_select')
                  
                input_date = st.date_input('Date', key='i_date', format='YYYY-MM-DD')
                input_date = datetime.combine(input_date, datetime.min.time())

            with sub_cols[1]:
                input_agency = st.selectbox(
                    label='Agency',
                    options=agencies_list,
                    key='in_agency',
                    accept_new_options=False)
                
                input_client = st.selectbox(
                    label='Client',
                    options=sorted(agencies_clients[input_agency]),
                    key='in_client',
                    accept_new_options=False)

            cols = st.columns([3.5, 6.5], gap='small')
            with cols[0]:
                input_captured = st.radio(
                    label='Captured',
                    options=['Yes', 'No'],
                    width='stretch',
                    horizontal=True)
            with cols[1]:
                radio_reqtype = st.radio(
                    label='Type',
                    options=['Regular', 'Ad Hoc', 'TOA'],
                    width='stretch',
                    horizontal=True)
            
            # st.markdown('**Hyperlinks**')
            input_hyperlink = st.text_area(
                label='Hyperlink Input',
                key='in_hyperlink',
                height=150,
                placeholder='Enter one or more hyperlinks (one per line)',
                label_visibility='collapsed')
                
            btn_add = st.button('➕ Add Record' , key='input_archive', width='stretch')
        
    # ===== DATA PREVIEW & MANAGEMENT SECTION =====
    with main_cols[1]:
        st.subheader('📊 Records Preview')
        with st.container(border=True):
            # display data in dataframe
            docs = list(temp_collection.find({}, {'_id':0}))            
            df = pd.DataFrame(docs)
            if df.empty:
                st.info('No records added yet. Use the form above to add entries.')
            else:
                df.index = df.index+1
                st.dataframe(df, width='stretch', height=200)
            
            if df.empty:
                disable_button=True
                record_options = []
            else:
                disable_button=False
                record_options = list(range(1, temp_collection_count+1))

            with st.container():
                btn_submit = st.button(
                    label='✅ Submit All',
                    width='stretch',
                    disabled=disable_button,
                    help='Add records first before submitting')                
                                
                record_no = st.selectbox(
                    label='Select Record',
                    options = record_options)
                
                btn_delete = st.button(
                    label='🗑️ Delete Record',
                    width='stretch',
                    disabled=disable_button,
                    help='Remove selected record')
                                
                btn_delete_all = st.button(
                    label='🗑️ Delete All',
                    width='stretch',
                    disabled=disable_button,
                    help='Remove all records')
                
                
        

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
                    _hyperlink = common.clean_url(_hyperlink)
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
                    'TYPE':reqtype,
                    'VERIFIED BY': verified_by
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
    
