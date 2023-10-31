# <center>bookstore 实验报告</center>

## 实验成员及分工

+ 李琦

+ 刘蔚美10215501441：买家用户接口（充值、下单、付款）；卖家用户接口（创建店铺、填加书籍信息及描述、增加库存）；买家收货和卖家发货；取消订单和查看历史订单。
**本次实验由我们平均分工，合作完成，无歧义**

## 实验任务

实现一个提供网上购书功能的网站后端。网站支持书商在上面开商店，购买者可以通过网站购买。买家和卖家都可以注册自己的账号。一个卖家可以开一个或多个网上商店，买家可以为自已的账户充值，在任意商店购买图书。支持 下单->付款->发货->收货 流程。

1. 实现对应接口的功能，见项目的 doc 文件夹下面的.md 文件描述 （60%）。其中包括：
   
   1) 用户权限接口，如注册、登录、登出、注销；

   2) 买家用户接口，如充值、下单、付款；

   3) 卖家用户接口，如创建店铺、填加书籍信息及描述、增加库存；

   通过对应的功能测试，所有 test case 都 pass。

2. 为项目添加其它功能（40%）：
   
   1) 实现后续的流程：发货 -> 收货；

   2) 搜索图书：
   用户可以通过关键字搜索，参数化的搜索方式；如搜索范围包括，题目，标签，目录，内容；全站搜索或是当前店铺搜索。如果显示结果较大，需要分页（使用全文索引优化查找）；

   3) 订单状态，订单查询和取消定单：
   用户可以查自已的历史订单，用户也可以取消订单。取消定单可由买家主动地取消定单，或者买家下单后，经过一段时间超时仍未付款，定单也会自动取消。

## 实验要求

+ 1. bookstore 文件夹是该项目的 demo，采用 Flask 后端框架与 SQLite 数据库，实现了前60%功能以及对应的测试用例代码。
要求大家创建本地 MongoDB 数据库，将bookstore/fe/data/book.db中的内容以合适的形式存入本地数据库，后续所有数据读写都在本地的 MongoDB 数据库中进行。

+ 2. 在完成前60%功能的基础上，继续实现后40%功能，要有接口、后端逻辑实现、数据库操作、代码测试。对所有接口都要写 test case，通过测试并计算测试覆盖率（尽量提高测试覆盖率）。
+ 3. 尽量使用索引，对程序与数据库执行的性能有考量。
+ 4. 尽量使用 git 等版本管理工具。
+ 5. 不需要实现界面，只需通过代码测试体现功能与正确性。

## bookstore目录结构

## 实验过程

### 本地数据库bookstore和书表books的创建

管理员模式打开cmd输入如下指令启动本地数据库

~~~shell
mongod --dbpath="E:\Software_Data\MongoDB\data\testdb"
~~~

书表我们选择的是将网盘里的book_lx.db以合适的形式存入本地数据库,代码详见`fe/data/book_set.py`

首先我们需要分别连接到SQLite 数据库和本地 MongoDB，在本地创建bookstore数据库和书表

~~~python
import sqlite3
from pymongo import MongoClient

 # 连接到 SQLite 数据库
sqlite_conn = sqlite3.connect('./fe/data/book_lx.db')
sqlite_cursor = sqlite_conn.cursor()

 # 连接到本地 MongoDB
mongo_client = MongoClient('localhost', 27017)
mongo_db = mongo_client['bookstore']  # 创建一个数据库
mongo_collection = mongo_db['books']  # 创建一个集合（表）

# 查询 SQLite 数据库中的书籍信息
sqlite_cursor.execute("SELECT * FROM book")
book_records = sqlite_cursor.fetchall()
~~~

将书本内容存入数据库时我们选取的格式如下：

~~~python
for record in book_records:
    book_data = {
        "id": record[0],  
        "title": record[1],
        "author": record[2],
        "publisher": record[3],
        "original_title": record[4],
        "translator": record[5],
        "pub_year": record[6],
        "pages": record[7],
        "price": record[8],
        "currency_unit": record[9],
        "binding": record[10],
        "isbn": record[11],
        "author_intro": record[12],
        "book_intro": record[13],
        "content": record[14],
        "tags": record[15],
        "picture": record[16]

    }
    mongo_collection.insert_one(book_data)
~~~

最后关闭数据库连接

~~~python
sqlite_conn.close()
mongo_client.close()
~~~

### 本地数据库的连接与初始化

观察 `be/model` 文件夹下的各个功能函数，发现每个类的初始化都用到一条语句：

~~~python
def __init__(self):
        db_conn.DBConn.__init__(self)
~~~

到 `be/model/db_conn.py` 文件中查看

~~~python
def __init__(self):
        self.conn = store.get_db_conn()
~~~

进一步追踪到`be/model/store.py`，get_db_conn()这个函数是用于连接数据库并初始化，创建程序与数据库之间的对话。后续功能实现语句中的 self.conn 就充当一般查询语句中的 session 的功能。

~~~python
def get_db_conn():
    db_url = 'mongodb://localhost:27017/'
    global database_instance 
    database_instance = Store(db_url)
    return database_instance
~~~

在该函数内部我们主要调用了类store

~~~python
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
        self.user_store_collection.create_index([("user_id", 1)], unique=True)
        self.store_collection = self.db['store']
        self.user_store_collection.create_index([("user_id", 1)], unique=True)
        self.new_order_collection = self.db['new_order']
        self.new_order_detail_collection = self.db['new_order_detail']
        self.new_order_paid = self.db['new_order_paid']
        self.new_order_cancel_collection = self.db['new_order_cancel']
~~~

在此介绍一下我们数据库中除了书表books以外的其它表。

+ user_collection
+ store_collection
+ user_store_collection
+ new_order_collection
+ new_order_detail_collection
+ new_order_paid
+ new_order_cancel_collection

### 前60%

#### 买家下单（new_order）`be/model/buyer.py`

+ 判断 user_id 是否存在，不存在则返回错误类型error_non_exist_user_id，执行码 511。
+ 判断 store_id 是否存在，不存在则返回错误类型error_non_exist_store_id，执行码 513。
+ 生成一个由user_id、store_id 和基于时间戳生成的唯一标识码组合而成的 uid，后续将作为order_id 用于唯一标识订单。
+ 根据订单信息（book_id和store_id）在store_collection表中查找商户中是否存在对应书籍和足够的库存。如果没找到想要买的书，返回错误类型 error_non_exist_book_id，执行码 515。若库存不够，返回错误类型 error_stock_level_low，执行码 517。
+ 若满足订单查询条件且该书籍拥有足够的库存，则更新店里书籍数目，即减库存
+ 在 new_order_detail_collection 表中插入订单的详细信息，包括order_id、book_id、购买价格 price、购买数量 count，同时计算总价格total_price，为 id_and_count 数组中每本书的单价和购买数量的乘积加和。
+ 通过datetime.utcnow() 生成当前 UTC 时间，为后面的自动取消订单做准备。在 new_order_collection 表中插入订单信息，包括order_id、store_id、买家user_id、下单时间place_order_time、订单总价 price。
+ 操作正确且满足下单成功的逻辑则返回执行码 200、执行信息 'ok' 和order_id。若出现数据库操作失败则报执行码 528 和相应的错误信息。

~~~python
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
~~~

#### 买家付款（payment）`be/model/buyer.py`

+ 用 order_id 查询在 new_order_collection 表中是否存在符合订单号的待付订单，不存在则返回错误类型 error_invalid_order_id，执行码 518。存在的话，获取buyer_id、store_id和total_price。
+ 若存在对应订单，但查询得到的该订单下单者 buyer_id 不等于预付款的用户也就是传入的 user_id，报身份权限错误，执行码 401，授权失败。
+ 通过 user_id 确认预付款用户有权限操作后，获取用户余额与用户密码。
+ 若buyer_id在user_collection中不存在，返回错误类型 error_non_exist_user_id，执行码 511。若密码不正确，报身份权限错误，执行码 401；密码正确则接下去判断。
+ 根据 store_id 在user_store_collection中查询书店所属卖家。若没找到则证明 store_id 有误，返回错误类型 error_non_exist_store_id，执行码 513。
+ 找到卖家的seller_id后，确定卖家在用户表里存在，即证明卖家是真实存在可与买家进行交易的。
+ 确定买家用户余额balance大于待付价格total_price，则能够成功付款
+ 根据buyer_id在 user_collection 中给买家减少余额，若更新失败返回错误类型 error_not_sufficient_funds，执行码 519；根据seller_id 在 user_collection 表中给卖家增加余额，若更新失败返回错误类型 error_non_exist_user_id，执行码 511。
+ 付款后，将该订单移至 new_order_paid 表，将 books_status 初始化为 0，表示未发货；从未付款订单表 new_order_collection 中删除对应订单信息。操作正确且满足付款成功的逻辑则返回执行码 200 和执行信息 'ok'。若出现数据库操作失败则报执行码 528 和相应的错误信息。

~~~python
def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            order_query = {"order_id": order_id}
            # 1. find order
            order_doc = self.conn.new_order_collection.find_one(order_query)
            if order_doc is None:
                return error.error_invalid_order_id(order_id)

            #order_id = order_doc["order_id"]
            buyer_id = order_doc["user_id"]
            store_id = order_doc["store_id"]
            total_price = order_doc["price"]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            user_query = {"user_id": buyer_id}

            # 2. find buyer user
            user_doc = self.conn.user_collection.find_one(user_query)
            if user_doc is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = user_doc.get("balance", 0)
            if password != user_doc.get("password", ""):
                return error.error_authorization_fail()

            # 3. find store
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
~~~

#### 买家充值（add_funds）`be/model/buyer.py`

+ 根据 user_id 获取用户密码与用户输入密码对比。没查到对应用户或密码错误报身份权限错误error_authorization_fail，执行码 401，授权失败
+ 若密码正确，在 user_collection 中更新用户余额。操作正确且满足充值成功的逻辑则返回执行码 200 和执行信息 'ok'。若出现数据库操作失败则报执行码 528 和相应的错误信息证明充值失败。

~~~python
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

        return 200, "ok"
~~~

#### 商家添加书籍(add_book)`be/model/seller.py`

+ 检查 user_id 、 store_id。不存在则分别报错卖家用户不存在和书店不存在，执行码 511、513。
+ 检查 book_id ，存在报错 error_exist_book_id，执行码 516，表示书籍已在该书店存在无法添加；若不存在，就将 store_id、book_id、书籍信息 book_info 和初始库存量 stock_level 插入 store 表。操作正确且满足添加书籍成功的逻辑则返回执行码 200 和执行信息 'ok'。若出现数据库操作失败则报执行码 528 和相应的错误信息证明添加失败。

~~~python
def add_book(self,user_id: str,store_id: str,book_id: str,book_json_str: str,stock_level: int,):
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
~~~

#### 商家添加书籍库存(add_stock_level)`be/model/seller.py`

+ 检查 user_id、store_id 和 book_id 是否已存在，不存在分别报错卖家用户不存在、书店不存在和书籍不存在，执行码 511、513，515。
+ 根据 store_id 和 book_id 更新对应书店 store_collection 中书籍库存。操作正确且满足添加书籍库存成功的逻辑则返回执行码 200 和执行信息 'ok'。若出现数据库操作失败则报执行码 528 和相应的错误信息证明添加库存失败。

~~~python
def add_stock_level(self, user_id: str, store_id: str,book_id: str, add_stock_level: int):
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
~~~

#### 创建商铺(create_store)`be/model/seller.py`

+ 检查 user_id 是否已存在，不存在返回用户不存在的报错，执行码 511；检查 store_id 是否已存在，存在返回书店已存在的报错，执行码 514，书店已存在意味着不能再用该 store_id 创建新书店了。
+ 用户存在且 store_id 不存在时，插入 user_id 和新建书店 store_id 至 user_store_collection，代表着该用户开了一家 id 为 store_id 的新书店。操作正确且满足创建书店成功的逻辑则返回执行码 200 和执行信息 'ok'。若出现数据库操作失败则报执行码 528 和相应的错误信息证明创建失败。

~~~python
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
~~~

### 后40%

#### 卖家发货（send_books ）`be/model/seller.py`

+ 根据 order_id 在已付款订单 new_order_paid 表中查询对应的订单状态和书店 store_id。没找到则返回错误类型 error_invalid_order_id，执行码 518，订单号不正确不能发货。
+ 通过书店 id 获取其拥有者 seller_id，比较其与输入的卖家 id 是否对应，不对应则返回权限错误，执行码 401。
+ 权限无误后，检查订单状态是否为未发货，不是则返回错误类型 error_books_duplicate_sent，执行码 522。
+ 若符合条件，则更新订单状态为已发货，即将物流状态码更新为 1，返回执行码 200 和执行信息 'ok'。
  
error_books_duplicate_sent是我为后40%的功能增加的(`be/model/error.py`)

~~~python
def error_books_duplicate_sent():
    return 522, error_code[522]
~~~

~~~python
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
~~~

对应的测试用例包括四种情况：发货正常情况、订单号 order_id 不存在、权限错误 user_id 与 store 的 user_id 不对应、订单已发货不可重复发货。在测试之前需要进行初始化：创建卖家、买家和书籍购买清单并计算价格，给买家充值，产生新订单，付款。详见`fe/test/test_send_books.py`

#### 买家收货（receive_books）'be/model/buyer.py'

+ 根据 order_id 在 new_order_paid 中查询对应的订单状态paid_status 和buyer_id。没找到则返回错误类型 error_invalid_order_id，执行码 518，订单号不正确无法修改状态。
+ 找到对应订单后，检查输入的用户 user_id 与下单用户是否一致，不是同一个人的话返回权限错误，执行码 401，没有资格修改物流状态。
+ 检查订单状态是否为已发货，若物流状态为未发货，返回错误类型 error_books_not_sent，执行码 520；若物流状态为已收货，返回错误类型 error_books_duplicate_receive，执行码 521。
+ 若物流状态正好为已发货未收货，则更新订单状态为已收货，即将books_status更新为 2，返回执行码 200 和执行信息 'ok'。

error_books_not_sent和error_books_duplicate_receive是我为后40%的功能增加的(`be/model/error.py`)

~~~python
def error_books_not_sent():
    return 520, error_code[520]

def error_books_duplicate_receive():
    return 521, error_code[521]
~~~

~~~python
def receive_books(self, user_id: str, order_id: str) -> (int, str):
        try : 
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
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
~~~

对应的测试用例包括五种情况：收货正常情况、订单号 order_id 不存在、权限错误 user_id 与 buyer_id 不对应、订单未发货不可能收货、订单已收货不可重复收货。在测试之前需要进行初始化：创建卖家、买家和书籍购买清单并计算价格，给买家充值，产生新订单，付款。详见`fe/test/test_receive_books.py`

#### 买家主动取消订单（cancel_order ）`be/model/buyer.py`

分为两种情况：买家取消未付款订单和买家取消已付款订单。对于已付款订单默认卖家都是允许退款的。

+ 未付款订单的取消，根据 order_id 在未付款订单 new_order_collection 中获取 buyer_id、store_id、订单价格 price。如果用户输入 id 与该订单买家 id 不匹配，返回权限错误，执行码 401，不支持非本人取消订单。确定为本人操作后，根据 order_id 直接从未付款订单 new_order_collection 中删除。然后给对应的商店加上之前被买掉的库存，若更新失败，返回error_stock_level_low，执行码517。
+ 已付款订单的取消。根据 order_id 在已付款订单 new_order_paid 表中进行查询，若未查到返回不是合法订单，执行码518。若找到，获取buyer_id、store_id、订单价格 price。如果用户输入 id 与该订单买家 id 不匹配，返回权限错误，执行码 401，同样不支持非本人取消订单。确定为本人操作后，根据 store_id 在 user_store_collection 中进行查询，若未找到返回error_non_exist_store_id，即商店不存在，执行码513。若找到，获取卖家seller_id。在 user_collection 表中更新买家和卖家余额。之后从已付款订单 new_order_paid 表中删除取消的订单表项，若删除错误，返回不是合法订单，执行码518。给对应的商店加上之前被买掉的库存，若更新失败，返回error_stock_level_low，执行码517。
+ 最后将订单信息加入 new_order_cancel 表中，方便以后对历史订单查询。

~~~python
def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
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
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
~~~

对应的测试用例包括八种情况：已付款订单的取消、未付款订单的取消、已付款订单号 order_id 不存在、未付款订单号 order_id 不存在、取消已付款订单权限错误、取消未付款订单权限错误、已付款订单不可重复取消、未付款订单不可重复取消。在测试之前需要进行初始化：创建卖家、买家和书籍购买清单并计算价格，给买家充值。详见`fe/test/test_cancel_order.py`

#### 历史订单查询（check_hist_order ）`be/model/buyer.py`

分为三种情况：查询未付款订单、查询已付款订单和查询已取消订单。

+ 先检查用户 id 是否存在，存在才能进行订单查询，不存在则报权限错误，执行码511。若存在生成一个列表res用于存储查询到的信息。
+ 查询未付款订单，根据 user_id 在未付款订单 new_order_collection 中筛选记录，然后根据查询得到的每个订单号 order_id 对new_order_detail_collection 表查询对应订单详细信息，获取该订单买的所有书籍的 book_id、购买该书籍数量 count 和单价 price 的信息，并将它们合并为一个字典类型。然后将这笔订单设置订单状态为 not paid'，加上订单号 order_id、买家 buyer_id、书店 store_id、订单总价 total_price、订单详情 details（刚才生成的字典类型数据）插入 res 字典类型。
+ 查询已付款订单，设置一个books_status_list包含三种books_status:未发货，已发货，已收货，用于后续记录。根据 user_id 在已付款订单 new_order_paid 中筛选记录，然后根据查询得到的每个订单号 order_id 对new_order_detail_collection 表查询对应订单详细信息，获取该订单买的所有书籍的 book_id、购买该书籍数量 count 和单价 price 的信息，并将它们合并为一个字典类型。然后将这笔订单设置订单状态为 already paid'，加上订单号 order_id、买家 buyer_id、书店 store_id、订单总价 total_price、书籍物流状态books_status，订单详情 details（刚才生成的字典类型数据）插入 res 字典类型。
+ 查询已取消订单表，操作与查询未付款订单一致，唯一的区别是，一开始在 new_order_cancel_collection 表中查询，最终的订单状态设置为'cancelled'。
+ 最终得到的 res 就是用户希望查到的所有历史订单，将它和执行码 200、执行消息 'ok' 一起返回。如果 res 长度为 0，即用户无购买记录，则返回执行码 200、执行消息 'ok' 和一个空值。

~~~python
def check_hist_order(self, user_id: str):
        try:

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
        except BaseException as e:
            return 528, "{}".format(str(e))
        if not res:
            return 200, "ok", "No orders found "
        else:
            return 200, "ok", res
~~~

对应的测试用例包括三种情况：历史订单正常查询情况、user_id 不存在导致的权限错误、用户无购买记录。在测试之前需要进行初始化：创建买家。详见`fe/test/test_check_hist_order.py`

#### 定单自动取消（auto_cancel_order）和检查订单是否取消（is_order_cancelled）`be/model/buyer.py`

+ 设置为 20 秒后取消订单，获取当前的UTC时间，设置查询条件为订单下单时间早于当前时间-20。在 new_order_collection 表中检查所有未付款订单，未查询到任何订单即没有未付款订单，说明已付款或已被买家自行取消，则无需自动取消，直接返回执行码 200 和执行消息 'ok'。
+ 若查到则从 new_order_collection 中删除该订单，即实现自动取消、依次自动取消订单，即将到期未付款订单从 new_order 中删除，删除失败返回错误类型 error_invalid_order_id。
+ 给对应的商店加上之前被买掉的库存，若更新失败，返回error_stock_level_low，执行码517。
+ 最后，将自动取消的订单信息也加入 new_order_cancel_collection 表中，方便以后对历史订单查询。

~~~python
def auto_cancel_order(self) -> (int, str):
        try:
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
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"
~~~

这里用到了 python 定时器库 apscheduler，需要在命令行输入 `pip install apscheduler` 下载。为了实现定时器到期自动取消订单的效果，在文件 be/model/buyer.py 最后插入下面的语句，从而能够创建一个调度器，将一个买家自动取消订单的定时任务加入调度器，开启调度器。

~~~python
sched = BackgroundScheduler()
sched.add_job(Buyer().auto_cancel_order, 'interval', id='5_second_job', seconds=5)
sched.start()
~~~

为测试自动取消订单还需要函数is_order_cancelled，判断订单是否自动取消的原因。

+ 根据 order_id 查询已取消的订单中是否有与该订单号相匹配的，若没找到则证明在超时前已付款无法再对订单自动取消，返回错误类型 error_auto_cancel_fail，执行码 524
+ 找到说明订单已成功取消（要么超时前已经由用户取消要么到时间自动取消，取决于测试时的线程休眠时间），则返回执行码 200 和执行消息 'ok'。
  
error_auto_cancel_fail是我为后40%的功能增加的(`be/model/error.py`)

~~~python
def error_auto_cancel_fail(order_id):
    return 524, error_code[524].format(order_id)
~~~

~~~shell
def is_order_cancelled(self, order_id: str) -> (int, str):

        order = self.conn.new_order_cancel_collection.find_one({"order_id": order_id})

        if order == None:
            return error.error_auto_cancel_fail(order_id)#超时前已付款
        else:
            return 200, "ok"
~~~

对应的测试用例包括三种情况：订单超时正常自动取消情况、在自动取消前订单已经被买家取消、在自动取消前订单已付款。在测试之前需要进行初始化：创建买家和书籍购买清单并计算价格，给买家充值。详见`fe/test/test_check_hist_order.py`
