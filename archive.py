import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, date
import time


@st.cache_data
def get_data(_client):
    
    try:
        # client = get_gsheet_client()
        sheet_id = "1VVLZ0O3NncvMjex8gonkgPTfIKzkJh22UON55991_QE"
        sheet = _client.open_by_key(sheet_id)

        data = sheet.sheet1.get_all_values()

        df = pd.DataFrame(data)
        df.columns = df.iloc[0]
        df = df[1:]


    except Exception as e:
        st.error(f"Error accessing Google Sheet: {e}")

    return df


def archive(client):

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
    
    st.title(":violet[Archive Data]")

    db = client['histo']
    collection = db['data']
    documents = list(collection.find({}))

    df = pd.DataFrame(documents)

    st.dataframe(df)
    
    client_collection = db['agencies']
    cursor = client_collection.find({}, {'CLIENTS':1, '_id':0})

    client_list = []
    for items in cursor:
        for item in items['CLIENTS']:
            client_list.append(item)
    
    client_list = sorted(list(dict.fromkeys(client_list)))
    st.write(client_list)

    exit()

    client_list = df['CLIENT NAME'].unique()
    client_list = sorted(client_list)    

    with st.container(border=True):
        col1, col2, col3 = st.columns([0.15, 0.20, 0.65], border=True)
        
        with col1:
            radio_options = st.radio(
                label=':blue[**OPTIONS**]',
                options=['Off', 'All Dates', 'All Clients'],
                horizontal=False)
                        
            with st.popover(label=':orange[**Help**]'):
                st.write('Off - Generates data for chosen client/s and choses dates')
                st.write('All Dates - Generates data for chosen client/s for all dates')
                st.write('All Clients - Generates data for chosen date/s for all clients')
            
            
        with col2:

            try:
                today = date.today()
                start_date = today
                end_date = today

                _date = st.date_input(
                    label=':calendar: :blue[**DATE RANGE**]',
                    key='a_date',
                    value=(start_date, end_date),
                    min_value=date(2025, 1, 1),
                    max_value=date(2030, 12, 31))
                
                st_date, en_date = _date
                st_date = st_date.isoformat()
                en_date = en_date.isoformat()
                
            except:
                st.write("Please select a valid date range.")
    
        with col3:
            _client = st.multiselect(
                label=':blue[**CLIENT**]',
                key='a_client',
                options=client_list)
        
    b_search = st.button(':orange[**Search Archive**]' , key='search_archive', use_container_width=True)
        
     
    if b_search:

        df['DATE'] = pd.to_datetime(df['DATE'])

        with st.spinner(text="Reading Archives", show_time=True, width="content"):
            time.sleep(5)

            if radio_options == 'Off':
                if _client == []:
                    st.error('No Client/s Selected')
                else:
                    for cl in _client:

                        with st.container(border=True):
                                                        
                            st.header(f':violet[{cl}]')

                            col_off1, col_off2 = st.columns(2, border=True)

                            with col_off1:

                                off_captured = df[(df['DATE'] >= st_date) & (df['DATE'] <= en_date) & (df['CLIENT NAME'] == cl) & (df['CAPTURED'] == 'Y')]
                                sel_off_captured = off_captured[['DATE', 'TIER', 'LINK']]

                                st.subheader(f':green[Captured - {sel_off_captured.shape[0]}]')
                                st.dataframe(sel_off_captured, hide_index=True, use_container_width=True)
                            
                            with col_off2:
                                off_missed = df[(df['DATE'] >= st_date) & (df['DATE'] <= en_date) & (df['CLIENT NAME'] == cl) & (df['CAPTURED'] == 'N')]
                                sel_off_missed = off_missed[['DATE', 'TIER', 'LINK']]

                                st.subheader(f':red[Missed - {sel_off_missed.shape[0]}]')
                                st.dataframe(sel_off_missed, hide_index=True, use_container_width=True)
                        

            elif radio_options == 'All Clients':

                filtered_df = df[(df['DATE'] >= st_date) & (df['DATE'] <= en_date)]
                new_cl = filtered_df['CLIENT NAME'].unique()

                for cl in new_cl:
                    with st.container(border=True):
                        
                        st.header(f':violet[{cl}]')

                        col_cap, col_mis = st.columns(2, border=True)

                        with col_cap:
                            captured_df = df[(df['DATE'] >= st_date) & (df['DATE'] <= en_date) & (df['CAPTURED'] == 'Y')]
                            cl_captured = captured_df[captured_df['CLIENT NAME']==cl]
                            sel_cl_captured = cl_captured[['DATE', 'TIER', 'LINK']]

                            st.subheader(f':green[Captured - {sel_cl_captured.shape[0]}]')

                            st.dataframe(sel_cl_captured, use_container_width=True, hide_index=True)
                        
                        with col_mis:
                            missed_df = df[(df['DATE'] >= st_date) & (df['DATE'] <= en_date) & (df['CAPTURED'] == 'N')]
                            cl_missed = missed_df[missed_df['CLIENT NAME']==cl]
                            sel_cl_missed = cl_missed[['DATE', 'TIER', 'LINK']]

                            st.subheader(f':red[Missed - {sel_cl_missed.shape[0]}]')

                            st.dataframe(sel_cl_missed, use_container_width=True, hide_index=True)                       
            
            elif radio_options == 'All Dates':
                if _client == []:
                    st.error('No Client/s Selected')
                else:
                    for cl in _client:

                        with st.container(border=True):

                            st.header(f':violet[{cl}]')

                            col_ad1, col_ad2 = st.columns(2, border=True)

                            with col_ad1:
                                
                                captured_df = df[(df['CLIENT NAME'] == cl) & (df['CAPTURED'] == 'Y')]
                                sel_captured = captured_df[['DATE', 'TIER', 'LINK']]

                                st.subheader(f':green[Captured - {sel_captured.shape[0]}]')
                                st.dataframe(sel_captured, use_container_width=True, hide_index=True)
                            
                            with col_ad2:

                                missed_df = df[(df['CLIENT NAME'] == cl) & (df['CAPTURED'] == 'N')]
                                sel_missed = missed_df[['DATE', 'TIER', 'LINK']]

                                st.subheader(f':red[Missed - {sel_missed.shape[0]}]')
                                st.dataframe(sel_missed, use_container_width=True, hide_index=True)
            
    return