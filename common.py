import streamlit as st
from pymongo import MongoClient
import re
from urllib.parse import urlparse
from PIL import Image
import requests
from io import BytesIO

@st.cache_resource
def connect_to_mongodb():
    return MongoClient(st.secrets["mongodb"]["uri"])    

@st.cache_resource
def connect_to_db():
    client = connect_to_mongodb()
    return client['histo']

@st.cache_resource
def connect_to_collections():
    db = connect_to_db()
    return db['agencies'], db['data'], db['temp'], db['tier'], db['users']

@st.cache_data
def get_agencies_list():

    agencies_clients = {}

    db = connect_to_db()
    collection = db["agencies"]
    cursor = collection.find({}, {'AGENCY NAME':1, '_id':0})
    agency_list = [doc['AGENCY NAME'] for doc in cursor if 'AGENCY NAME' in doc]

    for x in agency_list:
        cursor = collection.find_one({
            'AGENCY NAME':x
        })
        agencies_clients[x] = cursor.get('CLIENTS')

    return agencies_clients

@st.cache_resource
def get_logo():
    url = "https://i.ibb.co/JRW19H4Y/AShinra-Logo.png"
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return Image.open(BytesIO(response.content))

@st.cache_resource
def get_bgimage():

    background_image = """
    <style>
    [data-testid="stAppViewContainer"] > .main {
    background-image: url("https://i.ibb.co/8D4hLbSX/natural-light-white-background.jpg");
    background-size: 100vw 100vh;  # This sets the size to cover 100% of the viewport width and height
    background-position: center;
    background-repeat: no-repeat;}</style>"""
    st.markdown(background_image, unsafe_allow_html=True)

@st.cache_resource
def connect_to_zeno():
    client = MongoClient('mongodb://admin:q8vm5dz-h29piX%3FMo%26%3ClO4e0zn@mongodb4:27017,arbiter:27017/zeno_db?authSource=admin&replicaSet=rs1')
    # client = MongoClient('mongodb://admin:q8vm5dz-h29piX%3FMo%26%3ClO4e0zn@103.198.27.3:27017,103.198.27.2:27017/zeno_db?authSource=admin&replicaSet=rs1')
    return client['zeno_db']    
    

@st.cache_resource
def connect_to_articles():
    db = connect_to_zeno()
    return db["articles_app_article"]


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
    