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
## 2. 项目的 doc 文件夹下面的 .md 文件描述

### 2.1 用户权限接口，如注册、登录、登出、注销

#### Register


#### Login

#### Log out

#### Unregister

