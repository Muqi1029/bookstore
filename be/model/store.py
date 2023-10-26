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
        self.store_collection = self.db['store']
        self.new_order_collection = self.db['new_order']
        self.new_order_detail_collection = self.db['new_order_detail']
        self.new_order_paid = self.db['new_order_paid']
        self.new_order_cancel = self.db['new_order_cancel']
        


database_instance = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance
