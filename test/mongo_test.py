import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")


def getUsers():
    bookstore_db = myclient["bookstore"]
    print(bookstore_db.list_collection_names())
    book_col = bookstore_db["books"]
    book_col.drop()
    # user_col.drop()
    # user_col.delete_many({})
    # print(list(user_col.find({})))


# if __name__ == "__main__":
getUsers()
# mydb = myclient["bookstore"]
#
# book_col = mydb['book']
#
# one_data = {
#     "title": 'hello',
#     "content": 'world'
# }
#
# book_col.insert_one(one_data)
#
# print(list(book_col.find({})))
