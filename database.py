
import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            approved INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def is_approved(uid):
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("SELECT approved FROM users WHERE user_id=?", (uid,))
    row = cur.fetchone()
    conn.close()
    return row and row[0] == 1
