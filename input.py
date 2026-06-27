import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
import common
import modals


def input():
    # Ruby Charcoal Twilight theme styling
    st.markdown("""<style>
    :root {
        --primary: #C41E3A;
        --dark: #1A1A2E;
        --charcoal: #36454F;
        --twilight: #8B7BA8;
        --light: #F5F1E8;
    }
    .stMarkdown {margin-bottom: 0rem !important;}
    .stSelectbox {margin-bottom: 0.0rem !important;}
    .stDateInput {margin-bottom: 0.0rem !important;}
    .stRadio {margin-bottom: 0.0rem !important;}
    .stTextArea {margin-bottom: 0.0rem !important;}
    .stButton {margin-bottom: 0.0rem !important;}
    .stInfo {margin-bottom: 0.0rem !important;}
    .stDataFrame {margin-bottom: 0.0rem !important;}
    div[data-testid="stVerticalBlock"] {gap: 0.5rem;}
    
    /* Button styling with Ruby accent */
    button[kind="primary"] {
        background-color: #C41E3A !important;
        color: #F5F1E8 !important;
        border: none !important;
    }
    button[kind="primary"]:hover {
        background-color: #A01A30 !important;
    }
    
    /* Subheader styling */
    h2 {
        color: #C41E3A !important;
        border-bottom: 2px solid #8B7BA8 !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* Container border styling */
    .stContainer {
        border-color: #8B7BA8 !important;
    }
    
    /* Text styling */
    body {
        color: #F5F1E8 !important;
    }
    
    /* Text area styling to match select boxes */
    .stTextArea textarea {
        background-color: #C1C0C0 !important;
        color: #262730 !important;
        border-color: #ddd !important;
    }
    .stTextArea textarea:focus {
        background-color: #C1C0C0 !important;
        border-color: #F54B5D !important;
    }
    </style>""", unsafe_allow_html=True)

    common.page_title('Data Entry')
    agencies_clients = common.get_agencies_list()
    agencies_list = [k for k, v in agencies_clients.items()]
    temp_collection = common.connect_to_collections('temp')
    temp_collection_count = temp_collection.count_documents({})
    if 'in_hyperlink' not in st.session_state:
        st.session_state.in_hyperlink = ''
    
    main_cols = st.columns(2, gap='small')
    with main_cols[0]:
        st.subheader('📝 Entry Form')
        with st.container(border=True):
            sub_cols = st.columns([3.5, 6.5], gap='small')
            with sub_cols[0]:
                
                common.label_name('Verifier')
                verified_by = st.selectbox(
                    label='Verifier',
                    options=['Joel','Mary', 'Terence', 'Virna'],
                    key='verified_by_select',
                    label_visibility='collapsed')
                
                common.label_name('Date')
                input_date = st.date_input(
                    label='Date',
                    key='i_date',
                    format='YYYY-MM-DD',
                    label_visibility='collapsed')
                input_date = datetime.combine(input_date, datetime.min.time())

            with sub_cols[1]:
                
                common.label_name('Agency')
                input_agency = st.selectbox(
                    label='Agency',
                    options=agencies_list,
                    key='in_agency',
                    accept_new_options=False,
                    label_visibility='collapsed')
                
                common.label_name('Client')
                input_client = st.selectbox(
                    label='Client',
                    options=sorted(agencies_clients[input_agency]),
                    key='in_client',
                    accept_new_options=False,
                    label_visibility='collapsed')
                
            cols = st.columns([3.5, 6.5], gap='small')
            with cols[0]:

                common.label_name('Captured')
                input_captured = st.radio(
                    label='Captured',
                    options=['Yes', 'No'],
                    width='stretch',
                    horizontal=True,
                    label_visibility='collapsed')
                
            with cols[1]:

                common.label_name('Type')
                radio_reqtype = st.radio(
                    label='Type',
                    options=['Regular', 'Ad Hoc', 'TOA'],
                    width='stretch',
                    horizontal=True,
                    label_visibility='collapsed')
            
            common.label_name('Hyperlinks')
            input_hyperlink = st.text_area(
                label='Hyperlink Input',
                key='in_hyperlink',
                height=200,
                placeholder='Enter one or more hyperlinks (one per line)',
                label_visibility='collapsed')

            cols = st.columns([7, 3], gap='small')
            with cols[0]:
                btn_add = st.button('➕ Add Record' , key='input_archive', width='stretch')
            with cols[1]:
                btn_companies = st.button('⚙️ Agencies/Clients', key='check_client', width='stretch')
    
    with main_cols[1]:
        st.subheader('📊 Records Preview')
        with st.container(border=True):
            docs = list(temp_collection.find({}, {'_id':0}))
            df = pd.DataFrame(docs)
            if df.empty:
                st.info('No records added yet...')
                disable_button=True
                record_options=[]
            else:
                df.index = df.index+1
                st.dataframe(df, width='stretch', height=337)
                disable_button=False
                record_options = list(range(1, temp_collection_count+1))
            
            with st.container():
                btn_submit = st.button(
                    label='✅ Submit All',
                    width='stretch',
                    disabled=disable_button,
                    help='Add records first before submitting')
                
                cols = st.columns([2, 8], gap='small')
                with cols[0]:
                    record_no = st.selectbox(
                        label='Select Record',
                        options = record_options,
                        label_visibility='collapsed')
                
                with cols[1]:
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
        fqdn_collection = common.connect_to_collections('tier')
        fqdn_documents = fqdn_collection.find()
        with st.spinner('Adding Data', show_time=True):
            captured = 1 if input_captured == 'Yes' else 0
            reqtype = {'Regular': 1, 'Ad Hoc': 2, 'TOA': 3}[radio_reqtype]
            _hyperlinks = input_hyperlink.splitlines()
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
            temp_count = temp_collection.count_documents({})
            data_collection.insert_many(temp_collection.find())
            st.toast(f'Added {temp_count} entries')
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

    if btn_companies:
        modals.agencies_clients()
