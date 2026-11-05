
import sqlite3
from datetime import datetime

DB_NAME = "legal_assistant.db"


def get_connection():
    """Create a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """Create the required database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Store chatbot conversations
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_question TEXT NOT NULL,
            bot_answer TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Store user feedback
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_chat(user_question, bot_answer):
    """Save a chatbot conversation."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_history
        (user_question, bot_answer, created_at)
        VALUES (?, ?, ?)
    """, (
        user_question,
        bot_answer,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_chat_history(limit=50):
    """Get the latest chatbot conversations."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, user_question, bot_answer, created_at
        FROM chat_history
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    records = cursor.fetchall()
    conn.close()

    return records


def save_feedback(rating, comment=""):
    """Save user feedback."""
    if not 1 <= rating <= 5:
        raise ValueError("Rating must be between 1 and 5.")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (rating, comment, created_at)
        VALUES (?, ?, ?)
    """, (
        rating,
        comment,
        datetime.now().isoformat(timespec="seconds")
    ))

    conn.commit()
    conn.close()


def get_feedback():
    """Get all saved feedback."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, rating, comment, created_at
        FROM feedback
        ORDER BY id DESC
    """)

    records = cursor.fetchall()
    conn.close()

    return records

