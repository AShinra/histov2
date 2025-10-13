import streamlit as st
from pymongo import MongoClient
import re
from urllib.parse import urlparse

def connect_to_mongodb():
    try:
        # client = MongoClient("mongodb://192.168.2.156:27017/", serverSelectionTimeoutMS=40000)
        client = MongoClient('mongodb+srv://jonpuray:vYk9PVyQ7mQCn0Rj@cluster1.v4m9pq1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1')
    except Exception as e:
        st.write(e)

    return client

def remove_field_from_document(collection, fieldname):
    collection.update_many(
        {},                  # filter ({} = all docs)
        {"$unset": {fieldname: ""}}   # removes the "status" field
    )

def remove(collection, fieldname, old_value, new_value):
    collection.update_many(
        {fieldname: old_value},  # filter where field is null
        {"$set": {fieldname: new_value}}
    )

def get_fqdn(url):
    try:
        match = re.search(r'^https?://(www\.)?([^/]+)', url)
        return match.group(2)
    except:
        match = re.search(r'^https?://([^/]+)', url)
        return match.group(1)

def is_valid_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def clean_url(url: str):
    try:
        url = re.sub('https', 'http', url)
    except:
        pass

    try:
        url =re.sub('www.','', url)
    except:
        pass


def get_agencies_list():

    client = connect_to_mongodb()

    agencies_clients = {}

    db = client["histo"]
    collection = db["agencies"]
    cursor = collection.find({}, {'AGENCY NAME':1, '_id':0})
    agency_list = [doc['AGENCY NAME'] for doc in cursor if 'AGENCY NAME' in doc]

    for x in agency_list:
        cursor = collection.find_one({
            'AGENCY NAME':x
        })
        agencies_clients[x] = cursor.get('CLIENTS')

    return agencies_clients

def has_upper_and_number(text: str) -> bool:
    has_upper = any(c.isupper() for c in text)
    has_digit = any(c.isdigit() for c in text)
    if len(text)>=8:
        text_length = True
    else:
        text_length = False
    return has_upper, has_digit, text_length

def page_title(title):
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
    
    # st.markdown(
    #     """<style>h1{color: blue !important;}</style>""", unsafe_allow_html=True)
    
    st.title(f":blue[{title}]")
    