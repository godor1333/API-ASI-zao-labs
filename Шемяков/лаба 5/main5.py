from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
app = FastAPI()
# Database setup
def init_db():
conn = sqlite3.connect('auction.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
description TEXT,
price REAL NOT NULL
)
''')
conn.commit()
conn.close()
init_db()
class Item(BaseModel):
name: str
description: str = None
price: float
@app.post("/items/", response_model=Item)
def create_item(item: Item):
conn = sqlite3.connect('auction.db')
cursor = conn.cursor()
cursor.execute('''
INSERT INTO items (name, description, price)
VALUES (?, ?, ?)
''', (item.name, item.description, item.price))
conn.commit()
conn.close()
return item
@app.get("/items/", response_model=List[Item])
def get_items():
conn = sqlite3.connect('auction.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM items')
rows = cursor.fetchall()
conn.close()
return [Item(id=row[0], name=row[1], description=row[2], price=row[3]) for row in rows]
@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
conn = sqlite3.connect('auction.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
row = cursor.fetchone()
conn.close()
if row is None:
raise HTTPException(status_code=404, detail="Item not found")
return Item(id=row[0], name=row[1], description=row[2], price=row[3])