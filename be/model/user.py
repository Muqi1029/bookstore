import jwt
import time
import logging
from be.model import error
from be.model import db_conn


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            """
            use mongodb database here
            """
            user = {
                "user_id": user_id,
                "password": password,
                "balance": 0,
                "token": token,
                "terminal": terminal,
            }
            self.conn.user_collection.insert_one(user)
        except Exception:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        find_result = self.conn.user_collection.find({"user_id": user_id})
        users = list(find_result)
        if not users:
            return error.error_authorization_fail()
        assert len(users) == 1
        db_token = users[0]['token']
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        query = {"user_id": user_id}
        user_doc = self.conn.user_collection.find_one(query)

        if user_doc is None:
            return error.error_authorization_fail()

        if user_doc["password"] != password:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            condition = {"user_id": user_id}
            update_result = self.conn.user_collection.update_one(condition, {"$set": {
                "token": token,
                "terminal": terminal
            }})
            if not update_result.acknowledged:
                return error.error_authorization_fail() + ("",)
        except BaseException as e:
            return 528, "{}".format(str(e)), ""
        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            condition = {"user_id": user_id}
            update_result = self.conn.user_collection.update_one(condition, {'$set': {
                "token": dummy_token,
                "terminal": terminal
            }})
            if not update_result.acknowledged:
                return error.error_authorization_fail()

        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message

            deleted_result = self.conn.user_collection.delete_one({"user_id": user_id, "password": password})
            if deleted_result.deleted_count == 1:
                return 200, "ok"
            else:
                return error.error_authorization_fail()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        # return 200, "ok"

    def change_password(
            self, user_id: str, old_password: str, new_password: str
    ) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            query = {"user_id": user_id,"password": old_password}
            update_data = {
                "$set": {
                    "password": new_password,
                    "token": token,
                    "terminal": terminal
                }
            }
            result = self.conn.user_collection.update_one(query, update_data)

            if result.matched_count == 0:
                return error.error_authorization_fail()

        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

