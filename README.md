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
│  │  │  user.py  # user: register, login
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
│  ├─test # final authentic my_test
│  │  │  gen_book_data.py
│  │  │  my_test.md
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
│      my_test.sh
│
└─test # my own my_test
    │  con_db_test.py
    │  mongo_test.py
```

## 1. Start local mongodb server

```shell
mongod --dbpath="D:\softwareData\MongoDB\data\testdb"
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

- argument: 
  - user_id
  - password
- db:
  - user_collection
- logic: 根据当前时间和用户id生成用户登录的token，用户数据直接插入到`self.conn.user_connection`中

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
- argument: 
  - user_id
  - password
  - terminal
- db:
  - user_collection
- logic: 先根据user_id 查到对应的用户密码，检查登录的密码与用户密码是否相同，若不相同直接返回错误信息，相同后更新用户的token和terminal信息

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
    except BaseException as e:
        return 530, "{}".format(str(e)), ""
    return 200, "ok", token
```

#### Log out
- argument:
  - user_id
  - token
- logic:
  - 先检查用户的token是否正确，正确后更新用户的token
- db:
  - user_collection

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
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"
```

#### Unregister

- argument:
  - user_id
  - password
- db:
  - user_collection
- logic: 检查用户密码是否正确，然后将该条用户直接删除

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

### 2.2 买家用户接口，如充值、下单、付款

#### 充值

db:

- `user_collection`:更新用户余额

argument:

- user_id
- password
- add_value

#### 下单

db:

- `user` :是否存在
- `store`:商店里是否有该书
- `new_order_detail`: 每个订单包含的包含的详细信息，如单价
- `new_order`: 未付款订单的相关信息

argument:

- user_id
- store_id
- id_and_count

#### 付款

db:

- `new_order_collection`:该订单是否存在
- `user_collection`：用户是否存在、权限是否正确，获取余额
- `user_store_collection`：商店是否存在，卖家是否存在
- `new_order_collection`：从未付款订单中删除
- `new_order_paid`：加入已付款订单

argument:

- user_id
- password
- order_id

### 2.3 卖家用户接口：创建店铺、填加书籍信息及描述、增加库存

#### add_book

db:

- `store_collection`:给商店加新书

argument:

- user_id
- store_id
- book_id
- book_json_str
- stock_level

#### add_stock_level

db:

- `store_collection`：给商店的书加库存

argument:

- user_id
- store_id
- book_id
- add_stock_level

#### create_store

db:

- `user_store_collection`:创建商店

argument:

- user_id
- store_id

### 2.4 卖家发货和买家收货

#### send_books

db:

- `new_order_paid`：订单是否已付款
- `user_store_collection`：卖家是否有发货权限

argument:

- user_id
- order_id

#### receive_books

db:

- `new_order_paid`：订单是否存在

argument:

- user_id
- order_id

### 2.5 买家主动取消订单，查询订单，搜索图书，自动取消订单

#### cancel_order

db:

- `new_order_collection`：取消未付款订单之订单是否存在
- `new_order_detail_collection`：获取待取消订单的详细信息，如book_id、count
- `store_collection`：将该订单取消以后原卖家库存增加
- `new_order_paid`：已付款订单之订单是否存在
- `user_store_collection`：商店是否存在，获取卖家id
- `new_order_cancel_collection`：加入已取消订单表
- `user_collection`：卖家和买家余额更新

argument:

- user_id
- order_id

#### 3.3 check_hist_order

db:

- `new_order_collection`：查询未付款订单
- `new_order_detail_collection`：查询订单详细信息
- `new_order_paid`：查询已付款订单
- `new_order_cancel_collection`：查询已取消订单

argument:

- user_id

#### auto_cancel_order&is_order_cancelled

db:

- `new_order_collection`：查询未付款订单中的超时订单
- `new_order_detail_collection`：获取该订单书籍的详细信息，如book_id，count
- `store_collection`：自动取消订单以后给卖家增库存
- `new_order_cancel_collection`：加入已取消订单

argument:

- order_id

-- -- 

#### 搜索图书

- db:
    - store
    - books
- arguments:
    - keyword
    - page(optional, default 1)
    - store_id(optional, default None)
- logic:
    1. 在books中的content, tags, book_intro, title建立全文索引优化查找
    2. 根据可能传入的page和store_id做相对应的查找
