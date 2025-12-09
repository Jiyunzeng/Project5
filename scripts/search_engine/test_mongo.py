from pymongo import MongoClient

try:
    uri = "mongodb+srv://kh:1234@cluster0.fbav0ho.mongodb.net/?retryWrites=true&w=majority"
    client = MongoClient(uri)
    db = client["stock"]

    print("Connected Collections:", db.list_collection_names())
    print("Sample doc:", db["news_crawling"].find_one())

except Exception as e:
    print("❌ ERROR:")
    print(e)
