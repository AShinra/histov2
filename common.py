import streamlit as st
from pymongo import MongoClient
import re
from urllib.parse import urlparse
from PIL import Image
import requests
from io import BytesIO
import logging
import traceback
import os

@st.cache_resource
def connect_to_mongodb():
    """
    Connect to MongoDB with sensible timeouts and validate the connection.
    Looks for a URI in Streamlit secrets under ["mongodb"]["uri"] or the MONGO_URI environment variable.
    On failure, logs a masked version of the URI and full stacktrace to the app logs.
    """
    mongo_uri = None
    if "mongodb" in st.secrets and "uri" in st.secrets["mongodb"]:
        mongo_uri = st.secrets["mongodb"]["uri"]
    else:
        mongo_uri = os.environ.get("MONGO_URI")

    if not mongo_uri:
        raise RuntimeError("MongoDB URI not found. Set in Streamlit secrets (mongodb.uri) or MONGO_URI environment variable.")

    def _mask_uri(uri: str) -> str:
        try:
            return re.sub(r'://([^:@]+):([^@]+)@', '://<user>:<redacted>@', uri)
        except Exception:
            return "<redacted>"

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        # Force a server selection / ping to detect connection issues early
        client.admin.command('ping')
        return client
    except Exception as e:
        masked = _mask_uri(mongo_uri)
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.FileHandler("logs/mongo_errors.log")
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        logger.error("MongoDB connection failed for URI: %s\n%s", masked, traceback.format_exc())
        raise RuntimeError("Unable to connect to MongoDB. Full details written to logs.") from e

@st.cache_resource
def connect_to_db():
    client = connect_to_mongodb()
    return client['histo']

@st.cache_resource
def connect_to_collections(collection_name):
    db = connect_to_db()
    return db[collection_name]

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
def connect_to_client():
    return MongoClient(st.secrets['zenodb']['uri'])

@st.cache_resource
def connect_to_zenodb():
    client = connect_to_client()
    return client['zeno_db']

@st.cache_resource
def connect_to_zeno_collections(collection_name):
    db = connect_to_zenodb()
    return db[collection_name]



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
        url = re.sub('www.','', url)
    except:
        pass
    
    if url[-1] == '/':
        url = url.rstrip('/')
   
    return url




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

    st.markdown(
    f"""
    <h2 style='text-align: center; 
               color: white; 
               background: linear-gradient(90deg, #262730 0%, #3a3b40 40%, #ffffff 100%);
               padding: 10px; 
               border-radius: 10px;'>
        {title}
    </h2>
    """,
    unsafe_allow_html=True)
    gradient_line()


def gradient_line():
    st.markdown("""
    <div style='height: 4px; 
                background: linear-gradient(90deg, #5f27cd, #48dbfb, #10ac84);
                border-radius: 10px; 
                margin-bottom: 20px;'>
    </div>
    """,
    unsafe_allow_html=True)
    