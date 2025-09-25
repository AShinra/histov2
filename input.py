import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime
import time
from common import get_fqdn, is_valid_url




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
    st.title(":violet[Data Entry]")

    # get collections
    db = client["histo"]
    collection = db["data"]
    documents = collection.find()
    
    agencies_list = []
    companies_list = []
    # get agencies and convert to list
    for document in documents:
        agency = document['AGENCY']
        agencies_list.append(agency)
        company = document['CLIENT NAME']
        companies_list.append(company)
    
    agencies_list = set(agencies_list)
    agencies_list = list({item for item in agencies_list if item not in [None, '']})
    agencies_list = [str(item) for item in agencies_list]
    # st.write(sorted(agencies_list))
    # exit()
    companies_list = set(companies_list.sort())

    # load tier data
    fqdn_collection = db['tier']
    fqdn_documents = fqdn_collection.find()

    # load temp
    temp_collection = db['temp']
    id_list = list(temp_collection.distinct('_id'))
    
    with st.container(border=True):
        col1, col2, col3 = st.columns([0.15, 0.6, 0.25], border=True)
        with col1:
            input_date = st.date_input(':calendar: Date', key='i_date', format='YYYY-MM-DD')
            input_date = datetime.combine(input_date, datetime.min.time())
            input_captured = st.selectbox(
                label='Captured',
                options=['Yes', 'No'],
                accept_new_options=False
            )
            checkbox_adhoc = st.checkbox('Ad Hoc')

        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                input_agency = st.selectbox(
                    label='Agency',
                    options=agencies_list,
                    key='in_agency',
                    accept_new_options=True
                    )                
            with col2b:
                    input_client = st.selectbox(
                    label='Client',
                    options=companies_list,
                    key='in_client',
                    accept_new_options=True)

            input_hyperlink = st.text_area('Hyperlink', key='in_hyperlink')
        with col3:
            b_add = st.button('Add' , key='input_archive', use_container_width=True)
            
            if temp_collection.count_documents({}) > 0:
                b_submit = st.button('Submit', use_container_width=True, disabled=False)
                id_delete = st.selectbox('ID to Delete', options=id_list, disabled=False)
                b_delete = st.button('Delete', use_container_width=True, disabled=False)
            else:
                b_submit = st.button('Submit', use_container_width=True, disabled=True)                
                id_delete = st.selectbox('ID to Delete', options=id_list, disabled=True)
                b_delete = st.button('Delete', use_container_width=True, disabled=True)

        

    if b_add:
        
        with st.spinner('Processing Data', show_time=True):
                
            if input_captured == 'Yes':
                captured = 'Y'
            elif input_captured == 'No':
                captured = 'N'
            
            if checkbox_adhoc:
                ad_hoc = 'AD HOC'
            else:
                ad_hoc = ''

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
                        input_tier = 'Unlisted'
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
                    'TYPE':ad_hoc
                }

                # check if link exists
                if not temp_collection.find_one({'LINK':_hyperlink}):
                    result = temp_collection.insert_one(data)

        with st.expander(label='Click to see details', expanded=True):
            # display data in dataframe
            # docs = list(temp_collection.find({}, {'_id':0}))
            docs = list(temp_collection.find({}))
            df = pd.DataFrame(docs)
            st.dataframe(df, hide_index=True)

                    
    if b_submit:

        with st.spinner('Processing Data', show_time=True):
            
            # count the documents stored in temp collection
            temp_count = temp_collection.count_documents({})

            # insert all the documents in temp collection to database collection
            collection.insert_many(temp_collection.find())
            st.success(f'Added {temp_count} entries')

            # delete all documents from temp collection
            temp_collection.delete_many({})
    
    if b_delete:
        
        temp_collection.delete_one({'_id':id_delete})
        st.success('Deleted Record')
        st.rerun()
    
    return
