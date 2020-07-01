import sqlite3
from contextlib import closing


DB_PATH = './database/christmas_recipe.db'
with closing(sqlite3.connect(DB_PATH)) as connect:
    cursor = connect.cursor()
    select_sql = 'select count(id) as count from recipes'
    data = cursor.execute(select_sql)
    for row in data:
        print(row)