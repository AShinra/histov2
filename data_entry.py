import streamlit as st
from common import connect_to_mongodb
from datetime import datetime


def data_entry():

    client = connect_to_mongodb()

    db = client['histodb']
    collection = db['requests']
    # st.write(db.list_collection_names())

    document = collection.find_one({'agency':'EGGSHELL'})

    st.write(document)

