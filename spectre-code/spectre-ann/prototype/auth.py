# auth.py
import sqlite3
from passlib.hash import bcrypt

def create_users_table():
    conn = sqlite3.connect('/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/database/predictions.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def add_user(username, password):
    conn = sqlite3.connect('/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/database/predictions.db')
    c = conn.cursor()
    hashed_password = bcrypt.hash(password)
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()

def verify_password(username, password):
    conn = sqlite3.connect('/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/database/predictions.db')
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    stored_password = c.fetchone()
    conn.close()
    if stored_password:
        return bcrypt.verify(password, stored_password[0])
    else:
        return False

def user_exists(username):
    conn = sqlite3.connect('/home/aryn/spectre-dev/spectre-code/spectre-ann/prototype/database/predictions.db')
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone()
    conn.close()
    return exists is not None
