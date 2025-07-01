import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()
    cur.execute(""" 
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id INTEGER,
                    bot_id TEXT,
                    registration_status TEXT,
                    gender TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    phone TEXT,
                    city TEXT,
                    user_photo TEXT,
                    user_target_photo TEXT,
                    similar_celebrities TEXT,
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
                INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (telegram_id) DO UPDATE SET
                registration_status = excluded.registration_status,
                gender = excluded.gender,
                first_name = excluded.first_name,
                last_name = excluded.last_name,
                phone = excluded.phone,
                city = excluded.city,
                user_photo = excluded.user_photo,
                user_target_photo = excluded.user_target_photo,
                similar_celebrities = excluded.similar_celebrities,
                celeb_name = excluded.celeb_name,
                surgery_suggestions = excluded.surgery_suggestions 
                """, (            
                        user_data.get('telegram_id'),
                        user_data.get('bot_id'),
                        user_data.get('registration_status'),
                        user_data.get('gender'),
                        user_data.get('first_name'),
                        user_data.get('last_name'),
                        user_data.get('phone'),
                        user_data.get('city'),
                        user_data.get('user_photo'),
                        user_data.get('user_target_photo'),
                        user_data.get('similar_celebrities'),
                        user_data.get('celeb_name'),
                        user_data.get('surgery_suggestions')
                ))

    conn.commit()
    conn.close()