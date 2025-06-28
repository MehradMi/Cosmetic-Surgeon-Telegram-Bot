import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(""" 
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id TEXT,
                    bot_id TEXT,
                    registration_status TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    city TEXT,
                    user_photo TEXT,
                    celeb_name TEXT,
                    surgery_suggestions TEXT,
                    UNIQUE (telegram_id)
                )
                """)
    
    conn.commit()
    conn.close()
    
def save_user_to_db(user_data):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (telegram_id) DO UPDATE SET
                
                """)