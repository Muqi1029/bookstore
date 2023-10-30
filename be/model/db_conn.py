from be.model import store
from pymongo import MongoClient


class DBConn:
    def __init__(self):
        # self.client = MongoClient('mongodb://localhost:27017/')
        # self.db = self.client['bookstore']
        # self.conn = self.db
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        user_query = {"user_id": user_id}
        user_doc = self.conn.user_collection.find_one(user_query)
        if user_doc is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        query = {"store_id": store_id, "book_id": book_id}
        book_doc = self.conn.store_collection.find_one(query)
        if book_doc is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        query = {"store_id": store_id}
        store_doc = self.conn.user_store_collection.find_one(query)
        if store_doc is None:
            return False
        else:
            return True
