from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

app = FastAPI()



def init_db():
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


init_db()



class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float


class ItemOut(Item):
    id: int



@app.post("/items/", response_model=ItemOut)
def create_item(item: Item):
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
        (item.name, item.description, item.price)
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return ItemOut(id=item_id, **item.model_dump())


@app.get("/items/", response_model=List[ItemOut])
def get_items():
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    rows = cursor.fetchall()
    conn.close()
    return [ItemOut(id=r[0], name=r[1], description=r[2], price=r[3]) for r in rows]


@app.get("/items/{item_id}", response_model=ItemOut)
def get_item(item_id: int):
    conn = sqlite3.connect('auction.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemOut(id=row[0], name=row[1], description=row[2], price=row[3])