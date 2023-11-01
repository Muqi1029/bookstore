from pymongo import MongoClient


class Store:
    def __init__(self, db_url):
        self.client = MongoClient(db_url)
        self.db = self.client['bookstore']
        self.init_collections()

    def init_collections(self):
        # Define MongoDB collections for your tables
        self.user_collection = self.db['user']
        self.user_collection.create_index([("user_id", 1)], unique=True)

        self.user_store_collection = self.db['user_store']
        self.store_collection = self.db['store']

        self.new_order_collection = self.db['new_order']
        self.new_order_detail_collection = self.db['new_order_detail']
        self.new_order_paid = self.db['new_order_paid']
        self.new_order_cancel_collection = self.db['new_order_cancel']

        self.book_collection = self.db['books']
        self.book_collection.create_index(
            [("title", "text"), ("tags", "text"), ("book_intro", "text"), ("content", "text")])


database_instance = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    db_url = 'mongodb://localhost:27017/'
    global database_instance
    database_instance = Store(db_url)
    return database_instance
