
import sqlite3

db_path = "../fe/data/book_lx.db"

connection = sqlite3.connect(db_path)

cursor = connection.cursor()

cursor.execute("select name fromsqlite_master where type='table';")
result = cursor.fetchall()

print(result)

connection.close()

