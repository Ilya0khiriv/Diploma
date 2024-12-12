import sqlite3


def get_db():
    try:
        conn = sqlite3.connect("users.db")
        conn.row_factory = sqlite3.Row
        return conn
    except:
        return False


def init_db():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                amount_messages_shown INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username_id INTEGER,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                
                FOREIGN KEY (username_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()
    except:
        return False


init_db()
