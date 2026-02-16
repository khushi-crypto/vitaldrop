import sqlite3

DB_NAME = "vitaldrop.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Add donated column
try:
    cur.execute("ALTER TABLE donors ADD COLUMN donated INTEGER DEFAULT 0")
except Exception:
    pass

# Add donated_at column
try:
    cur.execute("ALTER TABLE donors ADD COLUMN donated_at TEXT")
except Exception:
    pass

conn.commit()
conn.close()
print("Migration done ✅")
