from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import pandas as pd
from sqlalchemy import create_engine


conn = sqlite3.connect(
    '/home/max/Desktop/Coder School Projects/_tonga/week2/w2-webscraping-with-sql/tiki_complete_v1.db', uri=True, check_same_thread=False)

cur = conn.cursor()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tiki_complete_v1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'

db = SQLAlchemy(app)

# engine = create_engine('sqlite:///tiki_complete_v1.db')

# engine.connect()

# categories = engine.execute('SELECT * FROM categories;').fetchall()
# print(type(categories))

# cate = pd.read_sql_query('SELECT * FROM categories;', conn)
# print(type(cate))

# cat = cur.execute('SELECT * FROM categories;')
# print(type(cat))

# cat = db.Query.paginate(db)
# print(cat)

# base = automap_base()

engine = create_engine('sqlite:///tiki_complete_v1.db')

# base.prepare(engine, reflect=True)

# # categories = base.classes.categories
# # items = base.classes.items

# session = Session(engine)

class categories(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    parent_id = db.Column(db.Integer)
    last = db.Column(db.String(20))
    create_at = db.Column(db.Date)

    def __repr__(self):
        return 'ID: {}, Name: {}, URL: {}, Parent_id: {}'.format(self.id, self.name, self.url, self.parent_id)

class items(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(200), nullable=False)
    cat_id = db.Column(db.Integer)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(200), nullable=False)
    img_url = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    regular_price = db.Column(db.Integer)
    sale_tag = db.Column(db.Integer)
    final_price = db.Column(db.Integer)
    parent_id = db.Column(db.Integer)
    create_at = db.Column(db.Date)

    def __repr__(self):
        return """ID: {}, Path: {}, Cat_ID: {}, Name: {}, Brand: {}, URL: {}, IMG: {}, Reg-Price: {},
                    Sale: {}, Final-Price: {}"""\
                    .format(self.item_id, self.item_path, self.cat_id,  self.name, self.brand,
                    self.url, self.img_url, self.regular_price, self.sale_tag, self.final_price)
    

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
    id = db.Column(db.Integer, primary_key=True)

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


# cate = categories.query.filter_by(parent_id=12)
# for cat in cate:
#     print(cat)

cat_name = engine.execute(f'SELECT name FROM categories WHERE id = 2').fetchone()
print(cat_name)