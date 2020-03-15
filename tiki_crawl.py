from bs4 import BeautifulSoup
import requests
import sqlite3
from collections import deque
import time
import pandas as pd

base_url = 'https://tiki.vn'

# conn = sqlite.connect('tiki2.db')
# tiki2.db has full category
# conn = sqlite3.connect('tiki2_copy.db')
# tiki2_copy.db has full category and 60k items

conn = sqlite3.connect('tiki3.db')
cur = conn.cursor()

# cur.execute('DROP TABLE categories;')


def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT,
            parent_id INT,
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        print('CREATED TABLE categories.')
    except Exception as err:
        print('ERROR BY CREATE TABLE: ', err)


def create_items_table():
    query = """
        CREATE TABLE IF NOT EXISTS items2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            cat_id INT,
            name VARCHAR(255),
            brand VARCHAR(80),
            url TEXT,
            img_url TEXT,
            regular_price INT,
            sale_tag TEXT,
            final_price INT,
            parent_id INT,
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
        print('CREATED TABLE items.')
    except Exception as err:
        print('ERROR BY CREATE TABLE: ', err)


def select_all():
    return cur.execute('SELECT * FROM categories;').fetchall()


def delete_all():
    return cur.execute('DELETE FROM categories;')


class Category:
    def __init__(self, cat_id, name, url, parent_id):
        self.cat_id = cat_id
        self.name = name
        self.url = url
        self.parent_id = parent_id

    def __repr__(self):
        return 'ID: {}, Name: {}, URL: {}, Parent_id: {}'.format(self.cat_id, self.name, self.url, self.parent_id)

    def save_into_db(self):
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            print(f'SAVED {self.name} INTO categories')
        except Exception as err:
            print('ERROR BY INSERT: ', err)


class Items:
    def __init__(self, item_id, item_path, cat_id, name, brand, img_url, url, regular_price, sale_tag='', final_price=''):
        self.item_id = item_id
        self.item_path = item_path
        self.cat_id = cat_id
        self.name = name
        self.brand = brand
        self.url = url
        self.img_url = img_url
        self.regular_price = regular_price
        self.sale_tag = sale_tag
        self.final_price = final_price

    def __repr__(self):
        return """ID: {}, Path: {}, Cat_ID: {}, Name: {}, Brand: {}, URL: {}, IMG: {}, Reg-Price: {},
                    Sale: {}, Final-Price: {}""".format(self.item_id, self.item_path, self.cat_id,  self.name, self.brand,
                                                        self.url, self.img_url, self.regular_price, self.sale_tag, self.final_price)

    def save_into_db(self):
        query = """ INSERT INTO items2 (path, cat_id, name, brand, url, img_url, regular_price, sale_tag, final_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
        val = (self.item_path, self.cat_id, self.name, self.brand, self.url, self.img_url,
               self.regular_price, self.sale_tag, self.final_price)

        try:
            cur.execute(query, val)
            self.item_id = cur.lastrowid
            # print(f'INSERT {self.name} INTO TABLE items2')
        except Exception as err:
            print('ERROR BY INSERT ITEMS: ', err)


def get_url(url):
    time.sleep(1)
    try:
        response = requests.get(url).text
        response = BeautifulSoup(response, 'html.parser')
        return response
    except Exception as err:
        print('ERROR BY REQUEST: ', err)


def get_main_categories(save_db=False):
    soup = get_url(base_url)

    result = []
    for a in soup.find_all('a', {'class': 'MenuItem__MenuLink-tii3xq-1 efuIbv'}):
        cat_id = None
        name = a.find('span', {'class': 'text'}).text
        url = a['href']
        parent_id = None
        print(cat_id, name, url, parent_id)
        cat = Category(cat_id, name, url, parent_id)
        if save_db:
            cat.save_into_db()
            print(f'SAVE MAIN CATEGORIES {name} INTO TABLE categories.')
        result.append(cat)
    return result


def get_sub_categories(category, save_db=False):
    name = category.name
    url = category.url
    result = []

    try:
        soup = get_url(url)
        div_container = soup.find_all(
            'div', {'class': 'list-group-item is-child'})
        for div in div_container:
            sub_id = None
            sub_name = div.a.text.strip()
            sub_url = base_url + div.a['href']
            sub_parent_id = category.cat_id

            sub = Category(sub_id, sub_name, sub_url, sub_parent_id)
            if save_db:
                sub.save_into_db()
                print(f'SAVE SUB CATEGORIES {sub_name} INTO TABLE categories.')
            result.append(sub)
    except Exception as err:
        print('ERROR BY GET SUB CATEGORY: ', err)

    return result


def get_all_categories(main_categories):
    de = deque(main_categories)
    count = 0

    while de:
        parent_cat = de.popleft()
        sub_cats = get_sub_categories(parent_cat, save_db=True)
        de.extend(sub_cats)
        count += 1

        if count % 10 == 0:
            print(count, 'times')


"""
url for items in category 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner&page=2'
"""


def OLD_get_items_from_category(save_db=False):

    """ query to get all the categories which dont have any child category
        SELECT c1.id, c1.name, c1.parent_id, c1.url FROM categories c1 LEFT OUTER JOIN categories c2
                ON c1.id = c2.parent_id
                WHERE c2.parent_id IS NULL
                LIMIT 1 OFFSET 11
    """
    # for i in range(16):
    #     name = pd.read_sql_query(
    #         f'SELECT name FROM categories LIMIT 1 OFFSET {i}', conn).values[0][0]
    #     cat_url = pd.read_sql_query(
    #         f'SELECT url FROM categories LIMIT 1 OFFSET {i}', conn).values[0][0]
    #     # cat_id = pd.read_sql_query(
    #     #     f'SELECT id FROM categories LIMIT 1 OFFSET {i}', conn).values[0][0]
    #     cat_id = i + 1
    #     print(cat_id)
    #     """ pandas return DataFrame, use DataFrame.values to return list of list value in that DataFrame
    #         url: https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner&page=2
    #     """
    #     for i in range(100):
    #         url = cat_url + f'&page={i+1}'
    #         print(url)
    #         soup = get_url(url)

    #         result = []
    #         """ item: div 'product-item' > div 'content'
    #                 img: img 'product-imgage'
    #                 title: p 'title'
    #                 price: span 'price-regular'
    #                 sale-tag: span 'sale-tag'
    #                 final-price: span 'final-price'
    #             """
    #         div_container = soup.find_all('div', {'class': 'product-item'})
    #         item_path = div_container['data-category']
    #         if div_container:
    #             for div in div_container:
    #             # it = {'item_id':'','name':'', 'brand':'', 'url':'', 'img_url':'', 'price':'', 'sale-tag':'', 'final-price':''}
    #                 item_id = None
    #                 item_name = div.a['title']
    #                 brand = div['data-brand']
    #                 item_url = div.a['href']
    #                 img_url = div.img['src']
    #                 regular_price = div.find('span', {'class': 'price-regular'}).text
    #                 sale_tag = div.find('span', {'class': 'final-price'}).text[-5:-1]
    #                 final_price = div.find('span', {'class': 'final-price'}).text[:-5].strip()

    #                 item = Items(item_id, item_path, cat_id, item_name, brand, item_url,
    #                                 img_url, regular_price, sale_tag, final_price)
    #                 if save_db:
    #                     item.save_into_db()
    #                     print(f'SAVE {item_name} INTO DTB')
    #                 result.append(item)
    #         else:
    #             break

def get_items_from_category(save_db=False):
    """ query to get all the categories which dont have any child category
    """
    query_result = pd.read_sql_query("""SELECT c1.id, c1.name, c1.parent_id, c1.url
                                            FROM categories c1 LEFT OUTER JOIN categories c2
                                            ON c1.id = c2.parent_id
                                            WHERE c2.parent_id IS NULL
                                            LIMIT 1400 OFFSET 1300""", conn)
    for i in query_result.itertuples():
        name = i.name[:-10].strip()
        cat_url = i.url
        cat_id = i.id
        quantity = i.name[-10:].strip()
        
        for i in range(100):
            url = cat_url + f'&page={i+1}'
            print(url)
            soup = get_url(url)
            
            result = []
            """ item: div 'product-item' > div 'content'
                    img: img 'product-imgage'
                    title: p 'title'
                    price: span 'price-regular'
                    sale-tag: span 'sale-tag'
                    final-price: span 'final-price'
                """
            try:
                div_container = soup.find_all('div', {'class': 'product-item'})
            except Exception as err:
                print('ERROR BY DIV FINDALL: ', err)
            if div_container:
                for div in div_container:
                # it = {'item_id':'','name':'', 'brand':'', 'url':'', 'img_url':'', 'price':'', 'sale-tag':'', 'final-price':''}
                    item_id = None
                    item_path = div['data-category']
                    item_name = div.a['title']
                    brand = div['data-brand']
                    item_url = div.a['href']
                    img_url = div.img['src']
                    regular_price = div.find('span', {'class': 'price-regular'}).text
                    sale_tag = div.find('span', {'class': 'final-price'}).text[-5:-1]
                    final_price = div.find('span', {'class': 'final-price'}).text[:-5].strip()

                    item = Items(item_id, item_path, cat_id, item_name, brand, item_url,
                                    img_url, regular_price, sale_tag, final_price)
                    if save_db:
                        item.save_into_db()
                        print(f'SAVE {item_name} INTO DTB')
                    result.append(item)
            else:
                break

# cur.execute("DROP TABLE categories;")
# create_categories_table()
# main_categories = get_main_categories(save_db=True)
# conn.commit()

# get_all_categories(main_categories)
# conn.commit()


# create_items_table()
# cur.execute("DROP TABLE items;")
get_items_from_category(save_db=True)
conn.commit()
