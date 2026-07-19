import sqlite3

conn = sqlite3.connect("skillbridge.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
password TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS skills(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
skill TEXT,
description TEXT,
category TEXT,
experience TEXT,
FOREIGN KEY(user_id) REFERENCES users(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    skill_id INTEGER,
    status TEXT DEFAULT 'Pending'
)
""")
conn.commit()
conn.close()

print("Database updated")