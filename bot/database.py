import sqlite3
from contextlib import contextmanager
from datetime import datetime

from bot.config import DB_PATH


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT,
                service TEXT NOT NULL,
                slot_date TEXT NOT NULL,
                slot_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'confirmed',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def is_slot_taken(slot_date: str, slot_time: str) -> bool:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM bookings WHERE slot_date=? AND slot_time=? AND status='confirmed'",
            (slot_date, slot_time),
        ).fetchone()
        return row is not None


def create_booking(user_id: int, username: str, service: str, slot_date: str, slot_time: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """INSERT INTO bookings (user_id, username, service, slot_date, slot_time, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, username, service, slot_date, slot_time, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return cur.lastrowid


def get_user_bookings(user_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE user_id=? AND status='confirmed' ORDER BY slot_date, slot_time",
            (user_id,),
        ).fetchall()
        return rows


def cancel_booking(booking_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "UPDATE bookings SET status='cancelled' WHERE id=? AND user_id=?",
            (booking_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
