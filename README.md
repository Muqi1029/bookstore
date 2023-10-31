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

### 2.2 buyer
> 买家用户接口，如充值、下单、付款
#### 充值
`user_collection`

```python
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
        return 530, "{}".format(str(e))

    return 200, "ok
```

#### 下单
db: 
- `user` 是否存在
- `store`
- `new_order_detail`: 每个订单包含的包含的详细信息，如价格
- `new_order`: buyer_id+store_id+order_id

1. insert new_order_detail


#### 付款

db:
- argument: 
  - buyer and order id

1. 订单合法检查 + 拿store_id
2. 买家合法检查 + 拿balance
3. `user_store`: 根据store_id 找seller
4. buyer - cost, seller + cost
5. insert to `new_order_paid`, delete from `new_order`
6. 


#### 创建店铺、填加书籍信息及描述、增加库存


### 2.3 seller

60%
<hr />

### 2.4 发货 & 收货
#### 发货：
`send_books`

- argument: 
  - user_id
  - order_id
- logic:
  1. 根据`new_order_paid`检查是否付款
  2. `store`: - number
  3. `new_order_paid`更新订单状态

#### 收货：
1.  


-- -- 
### 2.5 搜索图书

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


### 2.6 订单状态，订单查询和取消定单
#### 用户查询自已的历史订单 
- db:
  - `new_order_paid`
  - `new_order_cancel`
  - `new_order`
- argument
  - user_id
- logistic:
  1. 未付款订单：根据user_id去`new_order`中找对应的order_id, 根据order_id去`new_order_detail`找到对应的订单详细信息并返回
  2. #TODO



-- -- 
#### 买家主动取消订单:

- db : 
  - new_order_paid: 已支付订单数据库
  - new_order: 下单（未付款）数据库
  - new_order_detail: 订单详情数据库
  - store: 书店数据库
- arguments: 
  - user_id
  - order_id
- logistic: 
  1. 根据new_order查询是否已经付款，
     1. 若未付款，直接根据order_id将该订单从`new_order`中删去
     2. 若已付款，根据订单id去`new_order_paid`找到详细订单信息，给卖家减钱，给买家加钱，将该订单从`new_order_paid`中删除
  2. 根据order_id从`new_order_detail`获取订单的详细信息，给对应商店加库存
  3. 将该取消的订单插入到`new_order_cancel`

-- -- 
#### 超时自动取消订单
- db:
  - new_order_cancel
- argument:
  - none
- logic:
  - 查询现在的时间 - interval, 从`new_order`中删除时间小于等于这个时间点的订单


任务调度器：
```python
# Create a scheduler
sched = BackgroundScheduler()

# Add the job to the scheduler
sched.add_job(Buyer().auto_cancel_order, 'interval', id='5_second_job', seconds=5)

# Start the scheduler
sched.start()
```






db:

+ store_collection
+ new_order_detail_collection
+ new_order_collection

argument:

+ user_id
+ store_id
+ id_and_cont

### 2.2 payment

db:

+ new_order_collection
+ user_collection
+ user_store_collection
+ new_order_collection
+ new_order_paid

argument:

+ user_id
+ password
+ order_id

### 2.3add_funds

db:

+ user_collection

argument:

+ user_id
+ password
+ add_value

#### 2.4 add_book

db:

+ store_collection

argument:

+ user_id
+ store_id
+ book_id
+ book_json_str
+ stock_level

#### 2.5 add_stock_level

db:

+ store_collection

argument:

+ user_id
+ store_id
+ book_id
+ add_stock_level

#### 2.6 create_store

db:

+ user_store_collection

argument:

+ user_id
+ store_id

#### 3.0 send_books

db:

+ new_order_paid
+ user_store_collection

argument:

+ user_id
+ order_id

#### 3.1. receive_books

db:

+ new_order_paid

argument:

+ user_id
+ order_id

#### 3.2 cancel_order

db:

+ new_order_collection
+ new_order_detail_collection
+ store_collection
+ new_order_paid
+ user_store_collection
+ new_order_cancel_collection

argument:

+ user_id
+ order_id

#### 3.3 check_hist_order

db:

+ new_order_collection
+ new_order_detail_collection
+ new_order_paid
+ new_order_cancel_collection

argument:

+ user_id

#### 3.4 auto_cancel_order&is_order_cancelled

db:

+ new_order_collection
+ new_order_detail_collection
+ store_collection
+ new_order_cancel_collection

argument:

+ order_id
  