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
import socket

@st.cache_resource
def connect_to_mongodb():
    """
    Connect to MongoDB with DNS pre-checks and sensible timeouts.
    - Reads URI from Streamlit secrets or MONGO_URI env var
    - For non-SRV URIs, pre-resolves each hostname and reports unresolved hosts in the UI
    - Attempts a `ping` on success; logs full details to `logs/mongo_errors.log` on failure
    """
    mongo_uri = None
    if "mongodb" in st.secrets and "uri" in st.secrets["mongodb"]:
        mongo_uri = st.secrets["mongodb"]["uri"]
    else:
        mongo_uri = os.environ.get("MONGO_URI")

    if not mongo_uri:
        # Show a friendly message in Streamlit and raise
        st.error("MongoDB connection details are missing. Set `mongodb.uri` in Streamlit secrets or the `MONGO_URI` environment variable.")
        raise RuntimeError("MongoDB URI not found. Set in Streamlit secrets (mongodb.uri) or MONGO_URI environment variable.")

    def _mask_uri(uri: str) -> str:
        try:
            return re.sub(r'://([^:@]+):([^@]+)@', '://<user>:<redacted>@', uri)
        except Exception:
            return "<redacted>"

    # Ensure logs directory exists
    try:
        os.makedirs("logs", exist_ok=True)
    except Exception:
        pass

    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.FileHandler("logs/mongo_errors.log")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # If using SRV, skip manual host pre-check (SRV uses DNS SRV records)
    if mongo_uri.startswith("mongodb+srv://"):
        st.info("Using an SRV connection string (mongodb+srv://). Skipping per-host DNS pre-check; driver will resolve SRV.")
    else:
        # Extract the hosts portion of the URI (between '://' and the next '/')
        try:
            body = mongo_uri.split('://', 1)[1]
            hosts_part = body.split('/', 1)[0]
            # strip userinfo if present
            if '@' in hosts_part:
                hosts_part = hosts_part.split('@', 1)[1]
            hosts = [h.strip() for h in hosts_part.split(',') if h.strip()]

            unresolved = []
            for h in hosts:
                hostname = h.split(':', 1)[0]
                try:
                    socket.getaddrinfo(hostname, None)
                except Exception:
                    unresolved.append(hostname)

            if unresolved:
                msg = (
                    f"Unable to resolve database hostnames: {', '.join(unresolved)}. "
                    "These hostnames are likely internal to a Docker network or otherwise not resolvable from this environment. "
                    "Ensure your `MONGO_URI` uses publicly resolvable hostnames (e.g., Atlas cluster or FQDN/IP), or run the app in the same network where those hostnames resolve. "
                    "See https://www.mongodb.com/docs/manual/reference/connection-string/ for guidance."
                )
                # Show friendly message in Streamlit
                st.error(msg)

                # Add an expandable debug panel with masked info (does not reveal credentials)
                with st.expander("Show debug details"):
                    st.write("**Masked URI:**")
                    st.code(_mask_uri(mongo_uri))
                    st.write("**Unresolved hostnames:**")
                    st.write(", ".join(unresolved))
                    st.write("**Quick actions:**")
                    st.markdown(
                        "- Use a public MongoDB host (Atlas) or FQDN/IP that this environment can resolve\n"
                        "- Run the app within the same Docker network if hosts are internal\n"
                        "- Check application logs at `logs/mongo_errors.log` for the full stacktrace"
                    )

                # Log masked URI with details for debugging
                logger.error("DNS resolution failed for hosts: %s | URI: %s", unresolved, _mask_uri(mongo_uri))
                raise RuntimeError("One or more MongoDB hosts could not be resolved. See the app message for troubleshooting steps.")
        except Exception as e:
            logger.error("Failed while parsing or resolving hosts: %s\n%s", _mask_uri(mongo_uri), traceback.format_exc())
            st.error("There was an error parsing your MongoDB URI. Check the format and secrets settings.")
            raise RuntimeError("Error parsing MongoDB URI") from e

    # Attempt to connect (fail fast)
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        client.admin.command('ping')
        return client
    except Exception as e:
        masked = _mask_uri(mongo_uri)
        logger.error("MongoDB connection failed for URI: %s\n%s", masked, traceback.format_exc())
        st.error("Unable to connect to MongoDB. Full details are recorded in the application logs.")

        # Show masked summary in an expander for convenience
        with st.expander("Show debug details"):
            st.write("**Masked URI:**")
            st.code(masked)
            st.write("**Error summary:**")
            st.write(str(e))
            st.write("See `logs/mongo_errors.log` for the full stacktrace.")

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
    