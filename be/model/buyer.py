import uuid
import json
import logging

from apscheduler.schedulers.background import BackgroundScheduler

from be.model import db_conn
from be.model import error
from datetime import datetime, timedelta


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        try:
            # 判断 user_id 是否存在
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id,)
            # 判断 store_id 是否存在
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id,)

            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
            total_price = 0

            for book_id, count in id_and_count:
                query = {"store_id": store_id, "book_id": book_id}
                book_doc = self.conn.store_collection.find_one(query)
                if not book_doc:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level = book_doc["stock_level"]
                book_info = json.loads(book_doc["book_info"])
                price = book_info["price"]

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
                total_price += price * count

            now_time = datetime.utcnow()
            order_data = {
                "order_id": uid,
                "store_id": store_id,
                "user_id": user_id,
                "place_order_time": now_time,
                "price": total_price

            }

            self.conn.new_order_collection.insert_one(order_data)
            order_id = uid
        except BaseException as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""

        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order_query = {"order_id": order_id}

            # 1. find order
            order_doc = self.conn.new_order_collection.find_one(order_query)
            if order_doc is None:
                return error.error_invalid_order_id(order_id)

            # order_id = order_doc["order_id"]
            buyer_id = order_doc["user_id"]
            store_id = order_doc["store_id"]
            total_price = order_doc["price"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            user_query = {"user_id": buyer_id}

            # 2. find buyer
            user_doc = self.conn.user_collection.find_one(user_query)
            if user_doc is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user_doc.get("balance", 0)
            if password != user_doc.get("password", ""):
                return error.error_authorization_fail()

            # 3. find seller depending on store id
            user_store_query = {"store_id": store_id}
            user_store_doc = self.conn.user_store_collection.find_one(user_store_query)
            if user_store_doc is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = user_store_doc.get("user_id")
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 4. order

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)

            user_query = {"user_id": buyer_id, "balance": {"$gte": total_price}}
            user_update = {"$inc": {"balance": -total_price}}
            update_result = self.conn.user_collection.update_one(user_query, user_update)
            if update_result.matched_count == 0:
                return error.error_not_sufficient_funds(order_id)

            user_query = {"user_id": seller_id}
            user_update = {"$inc": {"balance": total_price}}
            update_result = self.conn.user_collection.update_one(user_query, user_update)
            if update_result.matched_count == 0:
                return error.error_non_exist_user_id(buyer_id)

            order_query = {"order_id": order_id}
            order_data = {
                "order_id": order_id,
                "store_id": store_id,
                "user_id": buyer_id,
                "books_status": 0,
                "price": total_price
            }
            self.conn.new_order_paid.insert_one(order_data)

            delete_result = self.conn.new_order_collection.delete_one(order_query)
            if delete_result.deleted_count == 0:
                return error.error_invalid_order_id(order_id)
        except BaseException as e:
            return 528, "{}".format(str(e))

        return 200, "ok"

    def search(self, keyword, scope=None, store_id=None, page=1, per_page=10):
        try:
            base_query = {"$text": {"$search": keyword}}
            scope_fields = {
                "title": "title",
                "tags": "tags",
                "book_intro": "book_intro",
                "content": "content"
            }
            # if scope and scope in scope_fields:
            #     field_name = scope_fields[scope]
            #     query = {field_name: base_query}
            # else:
            query = base_query

            if store_id:
                results = self.conn.store_collection.find({"store_id": store_id}, {"book_id": 1, "_id": 0})
                books_id = [o['book_id'] for o in results]
                query["id"] = {"$in": books_id}

            # print(query) # for debug
            results = self.conn.book_collection.find(query,
                                                     {"score": {"$meta": "textScore"}, "_id": 0, "picture": 0}).sort(
                [("score", {"$meta": "textScore"})])
            # Perform pagination
            results.skip((int(page) - 1) * per_page).limit(per_page)
        except BaseException as e:
            return 530, f"{str(e)}"
        return 200, list(results)

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

            if update_result.matched_count == 0:
                return error.error_non_exist_user_id(user_id)
        except BaseException as e:
            return 528, "{}".format(str(e))

        return 200, "o"

    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        order_query = {"order_id": order_id}
        order_doc = self.conn.new_order_paid.find_one(order_query)

        if order_doc == None:
            return error.error_invalid_order_id(order_id)

        buyer_id = order_doc.get("user_id")
        paid_status = order_doc.get("books_status")

        if buyer_id != user_id:
            return error.error_authorization_fail()
        if paid_status == 0:
            return error.error_books_not_sent()
        if paid_status == 2:
            return error.error_books_duplicate_receive()
        self.conn.new_order_paid.update_one(order_query, {"$set": {"books_status": 2}})

        return 200, "ok"

    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        order_query = {"order_id": order_id}
        order_doc = self.conn.new_order_collection.find_one(order_query)
        # 取消未付款订单
        if order_doc:
            buyer_id = order_doc.get("user_id")
            if buyer_id != user_id:
                return error.error_authorization_fail()
            store_id = order_doc.get("store_id")
            price = order_doc.get("price")
            self.conn.new_order_collection.delete_one({"order_id": order_id})

        # 取消已付款订单
        else:
            paid_doc = self.conn.new_order_paid.find_one(order_query)
            if paid_doc:
                buyer_id = paid_doc.get("user_id")
                if buyer_id != user_id:
                    return error.error_authorization_fail()
                store_id = paid_doc.get("store_id")
                price = paid_doc.get("price")

                # find the corresponding seller depending on store_id in the new_order_paid
                seller_query = {"store_id": store_id}
                seller_doc = self.conn.user_store_collection.find_one(seller_query)
                if seller_doc is None:
                    return error.error_non_exist_store_id(store_id)
                seller_id = seller_doc.get("user_id")

                # decrease the balance of the seller by price
                user_query = {"user_id": seller_id}
                update = {"$inc": {"balance": -price}}
                update_result = self.conn.user_collection.update_one(user_query, update)
                if update_result is None:
                    return error.error_non_exist_user_id(seller_id)

                # increase the balance of the buyer by price
                user_query1 = {"user_id": buyer_id}
                update1 = {"$inc": {"balance": price}}
                update_result1 = self.conn.user_collection.update_one(user_query1, update1)
                if update_result1 is None:
                    return error.error_non_exist_user_id(user_id)

                # delete the order from the new_order_paid
                delete_result = self.conn.new_order_paid.delete_one(order_query)
                if delete_result is None:
                    return error.error_invalid_order_id(order_id)

            else:
                return error.error_invalid_order_id(order_id)

        # increase the stock level depending on the order detail
        book_doc = self.conn.new_order_detail_collection.find(order_query)
        for book in book_doc:
            book_id = book["book_id"]
            count = book["count"]
            query = {"store_id": store_id, "book_id": book_id}
            update = {"$inc": {"stock_level": count}}
            update_result = self.conn.store_collection.update_one(query, update)
            if update_result.modified_count == 0:
                return error.error_stock_level_low(book_id) + (order_id,)

        # insert this cancelled order into new_order_cancel
        insert_order = {"order_id": order_id, "user_id": user_id, "store_id": store_id, "price": price}
        self.conn.new_order_cancel_collection.insert_one(insert_order)
        return 200, "ok"

    # 查询历史订单
    def check_hist_order(self, user_id: str):
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)

        res = []
        # 查询未付款订单
        user_query = {"user_id": user_id}
        new_order_cursor = self.conn.new_order_collection.find(user_query)
        if new_order_cursor:
            for new_order in new_order_cursor:
                details = []
                order_id = new_order.get("order_id")

                detail_cursor = {"order_id": order_id}
                new_order_detail_cursor = self.conn.new_order_detail_collection.find(detail_cursor)

                if new_order_detail_cursor:
                    for new_order_detail in new_order_detail_cursor:
                        details.append(
                            {"book_id": new_order_detail.get("book_id"), "count": new_order_detail.get("count"),
                             "price": new_order_detail.get("price")})
                else:
                    return error.error_invalid_order_id(order_id)
                res.append({"status": "not paid", "order_id": order_id, "buyer_id": new_order.get("user_id"),
                            "store_id": new_order.get("store_id"), "total_price": new_order.get("price"),
                            "details": details})

        # 查询已付款订单
        books_status_list = ["not send", "already send", "already receive"]
        new_order_paid_cursor = self.conn.new_order_paid.find(user_query)
        if new_order_paid_cursor:
            for new_order_paid in new_order_paid_cursor:
                details = []
                order_id = new_order_paid.get("order_id")
                detail_cursor = {"order_id": order_id}
                new_order_detail_cursor = self.conn.new_order_detail_collection.find(detail_cursor)
                if new_order_detail_cursor:
                    for new_order_detail in new_order_detail_cursor:
                        details.append(
                            {"book_id": new_order_detail.get("book_id"), "count": new_order_detail.get("count"),
                             "price": new_order_detail.get("price")})
                else:
                    return error.error_invalid_order_id(order_id)
                res.append({"status": "already paid", "order_id": order_id, "buyer_id": new_order_paid.get("user_id"),
                            "store_id": new_order_paid.get("store_id"), "total_price": new_order_paid.get("price"),
                            "books_status": books_status_list[new_order_paid.get("books_status")], "details": details})

        # 查询已取消订单
        new_order_cancel_cursor = self.conn.new_order_cancel_collection.find(user_query)
        if new_order_cancel_cursor:
            for new_order_cancel in new_order_cancel_cursor:
                details = []
                order_id = new_order_cancel.get("order_id")
                detail_cursor = {"order_id": order_id}
                new_order_detail_cursor = self.conn.new_order_detail_collection.find(detail_cursor)
                if new_order_detail_cursor:
                    for new_order_detail in new_order_detail_cursor:
                        details.append(
                            {"book_id": new_order_detail.get("book_id"), "count": new_order_detail.get("count"),
                             "price": new_order_detail.get("price")})
                else:
                    return error.error_invalid_order_id(order_id)

                res.append({"status": "cancelled", "order_id": order_id, "buyer_id": new_order_cancel.get("user_id"),
                            "store_id": new_order_cancel.get("store_id"), "total_price": new_order_cancel.get("price"),
                            "details": details})
        if not res:
            return 200, "ok", "No orders found "
        else:
            return 200, "ok", res

    def auto_cancel_order(self) -> (int, str):
        wait_time = 20  # 等待时间20s
        now = datetime.utcnow()  # 获取当前的UTC时间，并将其存储在now变量中
        interval = now - timedelta(seconds=wait_time)
        cursor = {"place_order_time": {"$lte": interval}}
        orders_to_cancel = self.conn.new_order_collection.find(cursor)
        if orders_to_cancel:
            for order in orders_to_cancel:
                order_id = order["order_id"]
                user_id = order["user_id"]
                store_id = order["store_id"]
                price = order["price"]
                self.conn.new_order_collection.delete_one({"order_id": order_id})
                
                order_query = {"order_id": order_id}
                book_doc = self.conn.new_order_detail_collection.find(order_query)
                for book in book_doc:
                    book_id = book["book_id"]
                    count = book["count"]
                    query = {"store_id": store_id, "book_id": book_id}
                    update = {"$inc": {"stock_level": count}}
                    update_result = self.conn.store_collection.update_one(query, update)
                    if update_result.modified_count == 0:
                        return error.error_stock_level_low(book_id) + (order_id,)
                    
                canceled_order = {"order_id": order_id, "user_id": user_id,"store_id": store_id, "price": price}
                
                self.conn.new_order_cancel_collection.insert_one(canceled_order)
        return 200, "ok"



    #测试auto_cancel_order的函数
    def is_order_cancelled(self, order_id: str) -> (int, str):
        order = self.conn.new_order_cancel_collection.find_one({"order_id": order_id})
        if order is None:
            return error.error_auto_cancel_fail(order_id)  # 超时前已付款
        else:
            return 200, "ok"


# Create a scheduler
sched = BackgroundScheduler()

# Add the job to the scheduler
sched.add_job(Buyer().auto_cancel_order, 'interval', id='5_second_job', seconds=5)

# Start the scheduler
sched.start()
