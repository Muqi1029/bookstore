

import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017")
bookstore = client['bookstore']

for name in bookstore.list_collection_names():
    bookstore[name].delete_many({})
