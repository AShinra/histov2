from pymongo import MongoClient
import pandas as pd


def get_db():

    link = 'http://philstar.com/starweek-magazine/2025/07/28/2461293/8-10-pinoys-want-vp-sara-face-trial-octa'

    # MongoDB connection string
    mongo_uri = "mongodb://admin:q8vm5dz-h29piX%3FMo%26%3ClO4e0zn@mongodb4:27017,arbiter:27017/zeno_db?authSource=admin&replicaSet=rs1"

    # Connect to MongoDB
    try:
        client = MongoClient(mongo_uri)
        db = client["zeno_db"]
        collection = db['articles_app_article']

        # documents = list(collection.find({}, {
        #     "article_clean_url": 1,
        #     "date_created": 1,
        # }).sort("_id", -1).limit(12000))

        document = collection.find_one({'article_clean_url':link})

        if document:
            print('YES')
            print(document)
        else:
            print('NO')


        # if documents:
        #     # Convert to DataFrame for display
        #     df = pd.DataFrame(documents)
        #     # URLS = df['article_clean_url'].to_list()
        #     # print(URLS)
        #     print(df)
        # else:
        #     print("No documents found in collection.")

    except Exception as e:
        print(f"Error: {e}")

    


get_db()