import sqlite3
from sqlite3 import connect

# Create a connection to the single database
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# Create the users table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        owner_id INTEGER,  
        connection_id TEXT UNIQUE
    )
''')

# Create the messages table
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


class DatabaseManager:
    # Function to save a message
    def save_message(self, connection_id, message_id, user_message_id, username, type_message, message, date):
        cursor.execute('''
                INSERT INTO messages (connection_id, message_id, user_message_id, username, type_message, message, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (connection_id, message_id, user_message_id, username, type_message, message, date))
        conn.commit()

    # Get a message by its ID
    def get_message_by_id(self, msg_id):
        cursor.execute('''
                SELECT connection_id, username, type_message, message
                FROM messages
                WHERE message_id = ?
            ''', (msg_id,))
        return cursor.fetchone()

    # Function to save the owner of a connection
    def save_owner_id(self, owner_id, connection_id):
        cursor.execute('''
                INSERT OR IGNORE INTO users (owner_id, connection_id)
                VALUES (?, ?)
            ''', (owner_id, connection_id))
        conn.commit()

    # Get owner_id by connection_id
    def get_owner_id(self, connection_id):
        cursor.execute('''
                SELECT owner_id
                FROM users
                WHERE connection_id = ?
            ''', (connection_id,))
        row = cursor.fetchone()
        return row[0] if row else None

    # Delete a message by its ID
    def delete_message_from_database(self, msg_id):
        cursor.execute('''
                DELETE FROM messages
                WHERE message_id = ?
            ''', (msg_id,))
        conn.commit()

    # Delete owner_id if the user disconnected the bot
    def delete_owner_id(self, owner_id):
        cursor.execute('''
                DELETE FROM users
                WHERE owner_id = ?
            ''', (owner_id,))
        conn.commit()

    # Function to check if such owner_id exists in the database
    def connection_id_exists(self, owner_id):
        cursor.execute('''
                SELECT connection_id
                FROM users
                WHERE owner_id = ?
                ''', (owner_id,)
                       )
        row = cursor.fetchone()
        return row is not None

    # Overwrite all messages to a new connection_id
    def rewrite_connection_id(self, new_connection_id, old_connection_id):
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

    # Function to get the old connection_id by owner_id
    def get_old_connection_id_by_owner_id(self, owner_id):
        cursor.execute('''
                SELECT connection_id
                FROM users
                WHERE owner_id = ?
            ''', (owner_id,))
        row = cursor.fetchone()
        return row[0] if row else None

