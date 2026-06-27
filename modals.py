import streamlit as st
import common

@st.dialog("Agencies & Clients", dismissible=True)
def agencies_clients():

    tab1, tab2, tab3  = st.tabs(['🔎 Check', '➕ Add', '➖ Delete'], )

    with tab1:
        collections = common.connect_to_collections('agencies')

        common.label_name('Company Name')
        company_input = st.text_input(
            label='',
            value='',
            key='check_company_input',
            label_visibility='collapsed')

        if st.button(label='Check Client', key='check_agency', width='stretch'):
            document = collections.find_one({'CLIENTS':company_input.upper()})

            if document:
                st.write(f"Client is under {document['AGENCY NAME']}")
            else:
                st.write(f"{company_input.upper()} not found!!!")
        
        
