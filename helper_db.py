import sqlite3
import os


def create_users_table():
    conn = None
    try:
        if not os.path.exists("registration_data.db"):
            conn = sqlite3.connect("registration_data.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    name TEXT,
                    surname TEXT,
                    registration_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при создании таблицы: {e}")
    finally:
        if conn:
            conn.close()


# Функция для сохранения данных о пользователе
def save_user_data(user_id, username, name, surname):
    conn = sqlite3.connect("registration_data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (user_id, username, name, surname) VALUES (?, ?, ?, ?)",
        (user_id, username, name, surname),
    )
    conn.commit()
    conn.close()


def user_exists(user_id):
    conn = sqlite3.connect("registration_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None
