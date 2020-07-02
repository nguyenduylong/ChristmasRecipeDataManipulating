import json
from bs4 import BeautifulSoup
import requests
import sqlite3
from contextlib import closing

FILE_PATH = './data/recipes.json'
DB_PATH = './database/christmas_recipes.db'
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

with closing(sqlite3.connect(DB_PATH)) as connect:
    cursor = connect.cursor()
    create_table = '''create table if not exists recipes (id int, name varchar(255),
                    image_url varchar(255), skill_level varchar(31), description text, 
                    nutrition text, ingredients text, methods text)'''

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

        # food image search
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

        # skill level info
        skill_level_div = soup.find('section', class_='recipe-details__item--skill-level')
        if skill_level_div is None:
            continue

        skill_level_span = skill_level_div.find('span', class_='recipe-details__text')
        if skill_level_span is None:
            continue

        skill_level = skill_level_span.getText()

        #nutrition info
        nutrition_ul = soup.find('ul', class_='nutrition')
        if nutrition_ul is None:
            continue

        nutrition_li_elements = nutrition_ul.findAll('li')
        if nutrition_li_elements is None or len(nutrition_li_elements) == 0:
            continue

        nutrition_infos = []
        for li_element in nutrition_li_elements:
            label_span = li_element.find('span', class_='nutrition__label')
            value_span = li_element.find('span', class_='nutrition__value')
            nutrition_infos.append(label_span.getText() + ':' + value_span.getText())
        if len(nutrition_infos) == 0:
            continue

        ingredients = "\n".join(parsed_json['Ingredients'])
        methods = "\n".join(parsed_json['Method'])
        nutrition = "\n".join(nutrition_infos)

        description = parsed_json['Description']
        if description is None:
            continue

        data = (i, parsed_json['Name'], image_src, skill_level, description, nutrition, ingredients, methods)
        inserted_data.append(data)
        i = i + 1

    insert_sql = 'insert into recipes (id, name, image_url, skill_level, description, nutrition, ingredients, methods) values (?,?,?,?,?,?,?,?)'
    cursor.executemany(insert_sql, inserted_data)
    connect.commit()



    
    