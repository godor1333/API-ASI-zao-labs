"""ПР5. Сервер аукциона на FastAPI для нагрузочного тестирования в JMeter.

Запуск:
    python -m uvicorn main:app --reload
Сервер доступен по адресу http://127.0.0.1:8000, документация — /docs.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = Path(__file__).resolve().parent / "auction.db"

app = FastAPI(title="Auction API", version="1.0")


# ---------------------------------------------------------------------------
# База данных
# ---------------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
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
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float


# ---------------------------------------------------------------------------
# Эндпоинты
# ---------------------------------------------------------------------------
@app.post("/items/", response_model=Item)
def create_item(item: Item):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO items (name, description, price)
        VALUES (?, ?, ?)
        """,
        (item.name, item.description, item.price),
    )
    conn.commit()
    item_id = cursor.lastrowid
    conn.close()
    return Item(id=item_id, name=item.name, description=item.description, price=item.price)


@app.get("/items/", response_model=List[Item])
def get_items():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    conn.close()
    return [
        Item(id=row[0], name=row[1], description=row[2], price=row[3])
        for row in rows
    ]


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(id=row[0], name=row[1], description=row[2], price=row[3])


@app.get("/health")
def health():
    return {"status": "ok"}
