import json
from bs4 import BeautifulSoup
import requests
import sqlite3
from contextlib import closing

FILE_PATH = './data/recipes.json'
DB_PATH = './database/christmas_recipe.db'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

with closing(sqlite3.connect(DB_PATH)) as connect:
    cursor = connect.cursor()
    create_table = '''create table if not exists recipes (id int, name varchar(255),
                    image_url varchar(255), description text, 
                    ingredients text, methods text)'''

    cursor.execute(create_table)
    connect.commit()

    i = 1
    data_rows = open(FILE_PATH).read().strip().splitlines()
    inserted_data = []
    for data_row in data_rows:
        parsed_json = json.loads(data_row)
        food_url = parsed_json['url']
        page = requests.get(food_url, headers=HEADERS)
        soup = BeautifulSoup(page.content, 'html.parser')
        # recipe media header element
        media_div = soup.find('div', class_='recipe-header__media')
        if media_div is None:
            continue
        # search image tag in media recipe header 
        image_src = 'https:' + media_div.find('img')['src']
        extension_position = image_src.find('.jpg')
        # check if url has image file
        if extension_position == -1:
            continue
        image_src = image_src[0: extension_position + 4]

        ingredients = "\n".join(parsed_json['Ingredients'])
        method = "\n".join(parsed_json['Method'])
        data = (i, parsed_json['Name'], image_src, parsed_json['Description'], ingredients, method)
        i = i + 1
        inserted_data.append(data)

    insert_sql = 'insert into recipes (id, name, image_url, description, ingredients, methods) values (?,?,?,?,?,?)'
    cursor.executemany(insert_sql, inserted_data)
    connect.commit()



    
    