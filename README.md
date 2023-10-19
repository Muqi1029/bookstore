```shell
│  app.log
│  be.db
│  README.md
│  requirements.txt
│  setup.py
│
├─be
│  │  app.py
│  │  serve.py
│  │  __init__.py
│  │
│  ├─model # The concrete logic used in handling request
│  │  │  buyer.py
│  │  │  db_conn.py # used to connect db
│  │  │  error.py
│  │  │  seller.py
│  │  │  store.py  # initialize database
│  │  │  user.py  # user 
│  │  │  __init__.py
│  │
│  ├─view # 后端访问接口
│  │  │  auth.py
│  │  │  buyer.py
│  │  │  seller.py
│  │  │  __init__.py
|
├─data
├─doc
│      auth.md
│      buyer.md
│      seller.md
│
├─fe
│  │  conf.py # info about question, e.g. url etc.
│  │  conftest.py
│  │  __init__.py
│  │
│  ├─access # send url to backend
│  │  │  auth.py
│  │  │  book.py
│  │  │  buyer.py
│  │  │  new_buyer.py
│  │  │  new_seller.py
│  │  │  seller.py
│  │  │  __init__.py
│  ├─bench
│  │  │  bench.md
│  │  │  run.py
│  │  │  session.py
│  │  │  workload.py
│  │  │  __init__.py
│  ├─data
│  │      book.db
│  │      book_lx.db
│  │      scraper.py
│  │
│  ├─test # final authentic test
│  │  │  gen_book_data.py
│  │  │  test.md
│  │  │  test_add_book.py
│  │  │  test_add_funds.py
│  │  │  test_add_stock_level.py
│  │  │  test_bench.py
│  │  │  test_create_store.py
│  │  │  test_login.py
│  │  │  test_new_order.py
│  │  │  test_password.py
│  │  │  test_payment.py
│  │  │  test_register.py
├─script
│      .coverage
│      test.sh
│
└─test # my own test
    │  con_db_test.py
    │  mongo_test.py
```


## 1. Start local mongodb server


```shell
mongod --dbpath="D:\software_data\MongoDB\data\testdb"
```

## 2. MongoDB database establishment
```python
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


database_instance = None


def init_database(db_url):
    global database_instance
    database_instance = Store(db_url)


def get_db_conn():
    global database_instance
    return database_instance

```

## 3. 项目的 doc 文件夹下面的 .md 文件描述

### 2.1 用户权限接口，如注册、登录、登出、注销

#### Register
```python
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
```

#### Login
`/be/model/user`
```python
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
    except sqlite.Error as e:
        return 528, "{}".format(str(e)), ""
    except BaseException as e:
        return 530, "{}".format(str(e)), ""
    return 200, "ok", token
```

#### Log out
```python
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

    # except sqlite.Error as e:
    #     return 528, "{}".format(str(e))
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
```

#### Unregister
`/be/model/user`
```python
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
```
