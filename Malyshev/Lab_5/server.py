from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from contextlib import contextmanager

app = FastAPI()

# Database connection manager
@contextmanager
def get_db_connection():
    conn = sqlite3.connect('auction.db')
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

# Database setup with better error handling
def init_db():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL CHECK(price >= 0),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

init_db()

class ItemCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

    class Config:
        schema_extra = {
            "example": {
                "name": "Vintage Watch",
                "description": "A beautiful vintage timepiece",
                "price": 150.50
            }
        }

class Item(ItemCreate):
    id: int
    created_at: Optional[str] = None

    class Config:
        orm_mode = True

# Dependency for database connection
def get_db():
    with get_db_connection() as conn:
        yield conn

@app.post("/items/", response_model=Item, status_code=201)
def create_item(item: ItemCreate, conn: sqlite3.Connection = Depends(get_db)):
    try:
        if item.price < 0:
            raise HTTPException(status_code=400, detail="Price cannot be negative")

        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO items (name, description, price)
        VALUES (?, ?, ?)
        ''', (item.name, item.description, item.price))
        conn.commit()

        # Get the created item with all fields
        cursor.execute('SELECT * FROM items WHERE id = ?', (cursor.lastrowid,))
        row = cursor.fetchone()

        return dict(row)

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/items/", response_model=List[Item])
def get_items(conn: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items ORDER BY created_at DESC')
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int, conn: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return dict(row)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: ItemCreate, conn: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        cursor.execute('''
        UPDATE items SET name = ?, description = ?, price = ?
        WHERE id = ?
        ''', (item.name, item.description, item.price, item_id))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        cursor.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        row = cursor.fetchone()
        return dict(row)

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.delete("/items/{item_id}")
def delete_item(item_id: int, conn: sqlite3.Connection = Depends(get_db)):
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM items WHERE id = ?', (item_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item deleted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)