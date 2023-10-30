import sqlite3
from pymongo import MongoClient

# 连接到 SQLite 数据库
sqlite_conn = sqlite3.connect('./fe/data/book_lx.db')
sqlite_cursor = sqlite_conn.cursor()

# 连接到本地 MongoDB
mongo_client = MongoClient('localhost', 27017)
mongo_db = mongo_client['bookstore']  # 创建一个数据库，可以根据需要修改数据库名称
mongo_collection = mongo_db['books']  # 创建一个集合（表）

# 查询 SQLite 数据库中的书籍信息
sqlite_cursor.execute("SELECT * FROM book")
book_records = sqlite_cursor.fetchall()

# 将书籍信息插入到 MongoDB 中
for i, record in enumerate(book_records):
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
        # 添加其他字段...
    }
    mongo_collection.insert_one(book_data)
    if i == 100:
        break

# 关闭数据库连接
sqlite_conn.close()
mongo_client.close()
