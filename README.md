```shell
│  .coverage
│  .gitignore
│  app.log
│  be.db
│  README.md
│  requirements.txt
│  setup.py
│  test.sh
│
├─.idea
├─be # backend
│  │  app.py
│  │  serve.py
│  │  __init__.py
│  │
│  ├─model # The concise logic used in handling request
│  │  │  buyer.py
│  │  │  db_conn.py # used to connect db
│  │  │  error.py
│  │  │  seller.py
│  │  │  store.py # initialize database
│  │  │  user.py
│  │  │  __init__.py
│  │
│  ├─view # 后端访问接口
│  │  │  auth.py
│  │  │  buyer.py
│  │  │  seller.py
│  │  │  __init__.py
├─data
├─doc
│      auth.md
│      buyer.md
│      seller.md
│
├─fe # frontend
│  │  conf.py
│  │  conftest.py
│  │  __init__.py
│  │
│  ├─access # here are the files used to send http requests
│  │  │  auth.py
│  │  │  book.py
│  │  │  buyer.py
│  │  │  new_buyer.py
│  │  │  new_seller.py
│  │  │  search.py
│  │  │  seller.py
│  │  │  __init__.py
│  │
│  ├─bench
│  │  │  bench.md
│  │  │  run.py
│  │  │  session.py
│  │  │  workload.py
│  │  │  __init__.py
│  │
│  ├─data
│  │      book.db
│  │      book_lx.db
│  │      book_set.py
│  │      scraper.py
│  │
│  ├─test # test code using pytest
│  │  │  gen_book_data.py
│  │  │  test.md
│  │  │  test_add_book.py
│  │  │  test_add_funds.py
│  │  │  test_add_stock_level.py
│  │  │  test_auto_cancel_order.py
│  │  │  test_bench.py
│  │  │  test_cancel_order.py
│  │  │  test_check_hist_order.py
│  │  │  test_create_store.py
│  │  │  test_login.py
│  │  │  test_new_order.py
│  │  │  test_password.py
│  │  │  test_payment.py
│  │  │  test_receive_books.py
│  │  │  test_register.py
│  │  │  test_search.py
│  │  │  test_send_books.py
├─htmlcov # visualized results of coverage
└─script
        test.sh
```

Start local mongodb server
```shell
mongod --dbpath="Path/Of/MongoDB_DATA/"
```