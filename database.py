import sqlite3
import os
from pathlib import Path
from pydantic import BaseModel, EmailStr
import bcrypt  # direct bcrypt import (no passlib)
from datetime import datetime, timedelta
import jwt
from typing import Optional
from dotenv import load_dotenv

# Load .env from this file's own directory — don't rely on auto-detection,
# which can fail inside uvicorn --reload's spawned subprocess.
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY is missing. Set it in your .env file "
        "(e.g. SECRET_KEY=some-long-random-string)."
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


def get_db_connection():
    conn = sqlite3.connect("user.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            conversation_id TEXT NOT NULL DEFAULT 'default',
            sender TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_email) REFERENCES users(email)
        )
    ''')

    # Migration: older databases created before conversation_id existed
    # won't have the column — add it if it's missing.
    cursor.execute("PRAGMA table_info(chat_messages)")
    existing_columns = {row["name"] for row in cursor.fetchall()}
    if "conversation_id" not in existing_columns:
        cursor.execute(
            "ALTER TABLE chat_messages ADD COLUMN conversation_id TEXT NOT NULL DEFAULT 'default'"
        )

    conn.commit()
    conn.close()


# ==================== PYDANTIC SCHEMAS ====================
class AuthSchema(BaseModel):
    name: Optional[str] = None
    email: EmailStr
    password: str


class ChatMessageSchema(BaseModel):
    message: str
    conversation_id: str = "default"


# ==================== PASSWORD HASHING (bcrypt) ====================
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# ==================== JWT ====================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None


# ==================== USER QUERIES ====================
def get_user_by_email(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def create_user(name: str, email: str, password: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
        (name, email, hash_password(password)),
    )
    conn.commit()
    conn.close()


# ==================== CHAT HISTORY ====================
def save_chat_message(user_email: str, sender: str, message: str, conversation_id: str = "default"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chat_messages (user_email, conversation_id, sender, message) VALUES (?, ?, ?, ?)",
        (user_email, conversation_id, sender, message),
    )
    conn.commit()
    conn.close()


def get_user_chat_history(user_email: str, conversation_id: str = "default"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT sender, message, timestamp FROM chat_messages "
        "WHERE user_email = ? AND conversation_id = ? ORDER BY id ASC",
        (user_email, conversation_id),
    )
    history = cursor.fetchall()
    conn.close()
    return [
        {"sender": row["sender"], "message": row["message"], "timestamp": row["timestamp"]}
        for row in history
    ]


def get_user_conversations(user_email: str):
    """List this user's past conversations, most recently active first.

    Each entry's "title" is the first user message in that conversation
    (truncated), so the sidebar can show something meaningful.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            conversation_id,
            MAX(timestamp) AS last_activity,
            (
                SELECT message FROM chat_messages m2
                WHERE m2.user_email = m1.user_email
                  AND m2.conversation_id = m1.conversation_id
                  AND m2.sender = 'user'
                ORDER BY m2.id ASC LIMIT 1
            ) AS first_message
        FROM chat_messages m1
        WHERE user_email = ?
        GROUP BY conversation_id
        ORDER BY last_activity DESC
        """,
        (user_email,),
    )
    rows = cursor.fetchall()
    conn.close()

    conversations = []
    for row in rows:
        title = (row["first_message"] or "New consultation").strip()
        if len(title) > 48:
            title = title[:48].rstrip() + "…"
        conversations.append(
            {
                "conversation_id": row["conversation_id"],
                "title": title,
                "last_activity": row["last_activity"],
            }
        )
    return conversations
