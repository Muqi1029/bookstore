from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)
            store_data = {
                "store_id": store_id,
                "book_id": book_id,
                "book_info": book_json_str,
                "stock_level": stock_level
            }
            # store
            self.conn.store_collection.insert_one(store_data)
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)
            
            update_query = {"store_id": store_id, "book_id": book_id}
            update_operation = {"$inc": {"stock_level": add_stock_level}}
            self.conn.store_collection.update_one(update_query, update_operation)
        
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)

            self.conn.user_store_collection.insert_one({"store_id": store_id, "user_id": user_id})
        
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
        
    def send_books(self, user_id: str, order_id: str) -> (int, str):
        try:

            paid_query = {"order_id": order_id}
            paid_doc = self.conn.new_order_paid.find_one(paid_query)

            if paid_doc == None:
                return error.error_invalid_order_id(order_id)   
            store_id = paid_doc.get("store_id")
            paid_status = paid_doc.get("books_status")

            store_query = {"store_id": store_id}
            store_doc = self.conn.user_store_collection.find_one(store_query)
            seller_id = store_doc.get("user_id")
            
            if seller_id != user_id:
                return error.error_authorization_fail()
            
            if paid_status == 1 or paid_status == 2:
                return error.error_books_duplicate_sent()

            self.conn.new_order_paid.update_one(paid_query, {"$set": {"books_status": 1}})     
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
