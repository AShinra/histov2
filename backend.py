from fastapi import FastAPI
from pymongo import MongoClient
from bson.json_util import dumps

app = FastAPI()

# Connect to your local MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_local_db"]
collection = db["my_collection"]

@app.get("/get-data")
def get_data():
    # Fetch all docs (limit for safety)
    docs = list(collection.find().limit(10))
    return {"data": docs}

@app.post("/add-data")
def add_data(item: dict):
    result = collection.insert_one(item)
    return {"inserted_id": str(result.inserted_id)}