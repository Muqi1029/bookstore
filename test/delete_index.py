import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017")
bookstore = client['bookstore']

bookstore['user_store'].drop_index("user_id_1")



