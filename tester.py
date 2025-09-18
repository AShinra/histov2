# vYk9PVyQ7mQCn0Rj

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


from urllib.parse import quote_plus

uri = "mongodb+srv://jonpuray:vYk9PVyQ7mQCn0Rj@cluster1.v4m9pq1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# try:
#     db = client['histodb']
#     collection = db['request']
#     document = collection.find_one({'name':'Jane Doe'})
#     print(document)
    # for doc in collection.find():
    #     print(doc)
    # collection_names = db.list_collection_names()
    # print(f"Collections in {db}:")
    # for name in collection_names:
    #     print(name)

    # document = collection.find_one({'article_clean_url':link})
    # document = collection.find_one({'Agency':'Rebel Marketing'})
    # print(document)
# except Exception as e:
#     print(e)