import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        order_id = ""
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                query = {"store_id": store_id, "book_id": book_id}
                book_doc = self.conn.store_collection.find_one(query)
                if not book_doc:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book_doc.get("stock_level")
                book_info = book_doc.get("book_info")
                price = book_info.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                query = {"store_id": store_id, "book_id": book_id, "stock_level": {"$gte": count}}
                update = {"$inc": {"stock_level": -count}}
                update_result = self.conn.store_collection.update_one(query, update)
                if update_result.modified_count == 0:
                    return error.error_stock_level_low(book_id) + (order_id,)

                order_detail_data = {
                    "order_id": uid,
                    "book_id": book_id,
                    "count": count,
                    "price": price
                }   
                self.conn.new_order_detail_collection.insert_one(order_detail_data)
            
            order_data = {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id
            }
            self.conn.new_order_collection.insert_one(order_data)
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order_query = {"order_id": order_id}
            order_doc = self.conn.new_order_collection.find_one(order_query)
            if order_doc is None:
                return error.error_invalid_order_id(order_id)

            order_id = order_doc.get("order_id")
            buyer_id = order_doc.get("user_id")
            store_id = order_doc.get("store_id")

            if buyer_id != user_id:
                return error.error_authorization_fail()

            user_query = {"user_id": buyer_id}
            user_doc = self.conn.user_collection.find_one(user_query)
            if user_doc is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user_doc.get("balance", 0)
            if password != user_doc.get("password", ""):
                return error.error_authorization_fail()
            
            user_store_query = {"store_id": store_id}
            user_store_doc = self.conn.user_store_collection.find_one(user_store_query)
            if user_store_doc is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = user_store_doc.get("user_id")

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)
            
            order_detail_query = {"order_id": order_id}
            order_detail_cursor = self.conn.new_order_detail_collection.find(order_detail_query)
            total_price = 0
            for order_detail_doc in order_detail_cursor:
                count = order_detail_doc.get("count")
                price = order_detail_doc.get("price")
                total_price += price * count

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            
            user_query = {"user_id": buyer_id, "balance": {"$gte": total_price}}
            user_update = {"$inc": {"balance": -total_price}}
            update_result = self.conn.user_collection.update_one(user_query, user_update)
            if update_result.modified_count == 0:
                return error.error_not_sufficient_funds(order_id)
            
            user_query = {"user_id": buyer_id}
            user_update = {"$inc": {"balance": total_price}}
            update_result = self.conn.user_collection.update_one(user_query, user_update)
            if update_result.modified_count == 0:
                return error.error_non_exist_user_id(buyer_id)

            order_query = {"order_id": order_id}
            delete_result = self.conn.new_order_collection.delete_one(order_query)
            if delete_result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

            order_detail_query = {"order_id": order_id}
            delete_result = self.conn.new_order_detail_collection.delete_many(order_detail_query)
            if delete_result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            user_query = {"user_id": user_id}
            user_doc = self.conn.user_collection.find_one(user_query)
            if user_doc is None:
                return error.error_authorization_fail()

            if user_doc.get("password") != password:
                return error.error_authorization_fail()

            user_query = {"user_id": user_id}
            update = {"$inc": {"balance": add_value}}
            update_result = self.conn.user_collection.update_one(user_query, update)
            if update_result.modified_count == 0:
                return error.error_non_exist_user_id(user_id)

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
