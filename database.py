import sqlite3
from sqlite3 import connect

# Создание подключения к единой БД
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,  
        connection_id TEXT UNIQUE
    )
''')

# Создание таблицы сообщений
cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        connection_id TEXT,
        message_id INTEGER,  
        user_message_id INTEGER,
        username TEXT,
        type_message INTEGER,
        message TEXT,
        date TEXT
    )
''')

conn.commit()


# Функция сохранения сообщения
def save_message(connection_id, message_id, user_message_id, username, type_message, message, date):
    cursor.execute('''
        INSERT INTO messages (connection_id, message_id, user_message_id, username, type_message, message, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (connection_id, message_id, user_message_id, username, type_message, message, date))
    conn.commit()


# Функция сохранения владельца подключения
def save_owner_id(owner_id, connection_id):
    cursor.execute('''
        INSERT OR IGNORE INTO users (owner_id, connection_id)
        VALUES (?, ?)
    ''', (owner_id, connection_id))
    conn.commit()


# Функция проверки есть ли такой owner_id в базе
def connection_id_exists(owner_id: str) -> bool:
    cursor.execute('''
        SELECT connection_id 
        FROM users 
        WHERE owner_id = ?
        ''', (owner_id,)
                   )
    row = cursor.fetchone()
    return row is not None


# Функция запроса старого connection_id пользователя
def get_old_connection_id_by_owner_id(owner_id: int) -> str | None:
    cursor.execute('''
        SELECT connection_id 
        FROM users
        WHERE owner_id = ?
    ''', (owner_id,))
    row = cursor.fetchone()
    return row[0] if row else None


# Перезапись всех сообщений на новый connection_id
def rewrite_connection_id(old_connection_id, new_connection_id):
    cursor.execute('''
        UPDATE messages 
        SET connection_id = ? 
        WHERE connection_id = ?
        ''', (new_connection_id, old_connection_id,))

    cursor.execute('''
            UPDATE users 
            SET connection_id = ? 
            WHERE connection_id = ?
            ''', (new_connection_id, old_connection_id,))

    conn.commit()


# Получить сообщение по его ID
def get_message_by_id(msg_id):
    cursor.execute('''
        SELECT connection_id, username,type_message, message
        FROM messages 
        WHERE message_id = ?
    ''', (msg_id,))
    return cursor.fetchone()


# Получить owner_id по connection_id
def get_owner_id(connection_id):
    cursor.execute('''
        SELECT owner_id 
        FROM users 
        WHERE connection_id = ?
    ''', (connection_id,))
    row = cursor.fetchone()
    return row[0] if row else None


# Удалить сообщение по его ID
def delete_message_from_database(message_id):
    cursor.execute('''
        DELETE FROM messages
        WHERE message_id = ?
    ''', (message_id,))
    conn.commit()


# Удалить owner_id если чесловек отключил бота
def delete_owner_id(owner_id):
    cursor.execute('''
        DELETE FROM users
        WHERE owner_id = ?
    ''', (owner_id,))
    conn.commit()
