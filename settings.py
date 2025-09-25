import streamlit as st
from common import get_agencies_list




def settings(client):

    
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
    st.title(":violet[Settings]")

    col1, col2, col3 = st.columns(3)

    with col1:
        selectd_agency = st.selectbox(
            label='Agency',
            options=get_agencies_list(client)
        )


    return