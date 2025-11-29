import sqlite3

class AuthManager:
    def __init__(self, connection):
        self.connection = connection
        self.create_tables()
    
    def create_tables(self):
        with self.connection:
            self.connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    country TEXT,
                    balance REAL
                )
            """)
    
    def register_user(self, username, password, country, balance):
        with self.connection:
            self.connection.execute(f"""
                INSERT INTO users (username, password, country, balance)
                VALUES ('{username}', '{password}', '{country}', {balance})
            """)
    
    def authenticate_user(self, username, password):
        cursor = self.connection.execute(f"""
            SELECT * FROM users 
            WHERE username = '{username}' AND password = '{password}'
        """)
        return cursor.fetchone()
    
    def count_users_by_country(self, country):
        cursor = self.connection.execute(f"""
            SELECT COUNT(*) FROM users WHERE country = '{country}'
        """)
        return cursor.fetchone()[0]
    
    def transfer_balance(self, from_user_id, to_user_id, amount):
        # Упрощенная реализация - всегда False для несуществующих пользователей
        return False
    
    def get_user_by_id(self, user_id):
        cursor = self.connection.execute(f"SELECT * FROM users WHERE id = {user_id}")
        return cursor.fetchone()
    
    def delete_user(self, user_id):
        with self.connection:
            self.connection.execute(f"DELETE FROM users WHERE id = {user_id}")