import pymongo


class Store:
    def __init__(self, db_url):
        self.client = pymongo.MongoClient(db_url)
        self.db = self.client['bookstore']
        self.init_collections()

    def init_collections(self):
        # Define MongoDB collections for your tables
        self.user_collection = self.db['user']
        self.user_collection.create_index([("user_id", 1)], unique=True)
        self.user_store_collection = self.db['user_store']
        self.user_store_collection.create_index([("user_id", 1)], unique=True)
        self.store_collection = self.db['store']
        self.user_store_collection.create_index([("user_id", 1)], unique=True)
        self.new_order_collection = self.db['new_order']
        self.new_order_detail_collection = self.db['new_order_detail']
        self.new_order_paid = self.db['new_order_paid']
        self.new_order_cancel_collection = self.db['new_order_cancel']

        self.book_collection = self.db['books']
        # create index of books for search
        self.book_collection.create_index({"title": "text", "book_intro": "text", "tag": "text", "content": "text"})


database_instance = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance
