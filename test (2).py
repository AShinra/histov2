from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb+srv://jonpuray:vYk9PVyQ7mQCn0Rj@cluster1.v4m9pq1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client["histo"]
collection = db["data"]

# docs = collection.find()

# for doc in docs:
#     _date = doc['TYPE']

#     try:
#         new_date = datetime.fromisoformat(_date)
#     except:
#         new_date = _date
    
#     collection.update_one(
#         {"_id": doc["_id"]},    # filter by unique ID
#         {"$set": {"DATE": new_date}}  # update DATE field
#     )

# print("DATE fields updated successfully.")

# collection.update_many(
#     {"TYPE": 'null'},  # filter where field is null
#     {"$set": {"TYPE": ""}}
# )



collection.update_many(
    {},                  # filter ({} = all docs)
    {"$unset": {"status": ""}}   # removes the "status" fieldu
)

    # new_doc = {}
    # for key, value in doc.items():
    #     if key == "DATE":
    #         new_doc[key] = value
    #         continue
    #     try:
    #         # Try to parse string into date
    #         if isinstance(value, str):
    #             new_doc[key] = datetime.fromisoformat(value)
    #         else:
    #             new_doc[key] = value
    #     except Exception:
    #         new_doc[key] = value  # keep original if not date
    
    # # Update document
    # collection.update_one({"DATE": doc["DATE"]}, {"$set": new_doc})
