from auth.database import get_db


def create_user(username: str, password: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, amount_messages_shown) VALUES (?, ?, ?)",
                           (username, password, 5))
            conn.commit()
        except Exception as e:
            return None
        return cursor.lastrowid
    except:
        return False


def get_user_info(username: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount_messages_shown FROM users WHERE username = ?", (username,))

        data = cursor.fetchone()
        if data:
            return int(data[0]), int(data[1])
        else:
            return None, None
    except:
        return False

def get_conversation(username_id: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM conversations WHERE username_id = ?", (username_id,))
        return cursor.fetchall()
    except:
        return False


def update_conversation(username_id, user_message, ai_response):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO conversations (username_id, user_message, ai_response) VALUES (?, ?, ?)",
                       (username_id, user_message, ai_response))
        conn.commit()
    except:
        return False


def update_amount(amount: int, id: int):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET amount_messages_shown = ? WHERE id = ?", (amount, id))
        conn.commit()
    except:
        return False


def get_user_by_username(username: str):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cursor.fetchone()
    except:
        return False
