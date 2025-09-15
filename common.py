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
