import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
from common import get_fqdn, is_valid_url, get_agencies_list, page_title




@st.dialog('Delete Entry', width='large')
def delete_entry(data):
    
    col1, col2 = st.columns(2)
    with col1:
        record_number = int(st.number_input(
        label='Record Number to Delete',
        min_value=0,))
        
        btn_deleterecord = st.button(
            label='Delete Record')    


@st.cache_data
def load_data(_date, client, link):

    data = {'DATE':[], 'CLIENT':[], 'LINK':[]}

    data['DATE'].append(_date)

    return data


def input(client, client_list):

    page_title('Data Entry')

    # get collections
    agencies_list = get_agencies_list(client)

    # load tier data
    db = client['histo']
    fqdn_collection = db['tier']
    fqdn_documents = fqdn_collection.find()

    # load temp
    temp_collection = db['temp']
    temp_collection_count = temp_collection.count_documents({})    
    id_list = list(temp_collection.distinct('_id'))
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.15, 0.6, 0.25], border=True)
        with col1:
            input_date = st.date_input(':calendar: **:violet[Date]**', key='i_date', format='YYYY-MM-DD')
            input_date = datetime.combine(input_date, datetime.min.time())
            
            input_captured = st.pills(
                label='**:violet[Captured]**',
                options=['Yes', 'No'],
                default='Yes',
                width='stretch'
            )

            cola, colb = st.columns(2)
            with cola:
                radio_reqtype = st.pills(
                    label='**:violet[Request]**',
                    options=['Regular', 'Ad Hoc', 'TOA'],
                    default='Regular',
                    width='stretch'
                )
           
        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                input_agency = st.selectbox(
                    label='Agency',
                    options=agencies_list,
                    key='in_agency',
                    accept_new_options=True
                    )
            agency_collection = db['agencies']
            document = agency_collection.find_one({'AGENCY NAME':input_agency})
            companies_list = document['CLIENTS']
            
            with col2b:
                    input_client = st.selectbox(
                    label='Client',
                    options=companies_list,
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
                if is_valid_url(_hyperlink) == True:
                    fqdn = get_fqdn(_hyperlink)
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
        
            time.sleep(2)
        st.rerun()
                    
    if btn_submit:        

        with st.spinner('Sending Record', show_time=True):

            data_collection  = db['data']
            
            # count the documents stored in temp collection
            temp_count = temp_collection.count_documents({})

            # insert all the documents in temp collection to database collection
            data_collection.insert_many(temp_collection.find())
            st.toast(f'Added {temp_count} entries')

            # delete all documents from temp collection
            temp_collection.delete_many({})
        
        st.rerun()
    
    if btn_delete:
        with st.spinner('Deleting Record', show_time=True):
            data_to_delete = df.at[record_no,'LINK']
            temp_collection.delete_one({'LINK':data_to_delete})
            time.sleep(2)
        
        st.rerun()
    
    if btn_delete_all:
        with st.spinner('Deleting All Records', show_time=True):
            temp_collection.delete_many({})
            time.sleep(2)

        st.rerun()    
