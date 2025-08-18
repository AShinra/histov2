import streamlit as st
from pymongo import MongoClient

def connect_to_mongodb():
    try:
        client = MongoClient("mongodb://192.168.2.156:27017/", serverSelectionTimeoutMS=30000)
    except Exception as e:
        st.write(e)

    return client