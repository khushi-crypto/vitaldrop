import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "vitaldrop_v2.db")  # same folder me stable





def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS donors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        blood_group TEXT NOT NULL,

        recency INTEGER NOT NULL,
        frequency INTEGER NOT NULL,
        monetary INTEGER NOT NULL DEFAULT 0,
        time_months INTEGER NOT NULL DEFAULT 0,

        prediction TEXT NOT NULL,

        donated INTEGER NOT NULL DEFAULT 0,
        donated_at TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    )
    """)

    conn.commit()
    conn.close()
