"""
Offline WhatsApp logic test.

Simulates incoming WhatsApp messages by calling route_message()
directly. No Meta credentials, no network.
"""

import whatsapp_webhook as wh
import sqlite3

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
def ensure_test_link(phone, student_id):
    con = sqlite3.connect(DB)
    exists = con.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='whatsapp_users'"
    ).fetchone()
    if not exists:
        con.execute("""
            CREATE TABLE whatsapp_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE,
                student_id INTEGER,
                name TEXT,
                is_registered INTEGER DEFAULT 1,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
    con.execute("""
        INSERT INTO whatsapp_users (phone_number, student_id, is_registered)
        VALUES (?, ?, 1)
        ON CONFLICT(phone_number) DO UPDATE
            SET student_id=excluded.student_id, is_registered=1
    """, (phone, student_id))
    con.commit()
    con.close()

print("=" * 60)
print("OFFLINE WHATSAPP TEST — no Meta, no network")
print("=" * 60)

TEST_PHONE = "+263777000333"
ensure_test_link(TEST_PHONE, 3)   # Mike: Grade 5, subject = Accounting

cases = [
    ("hi",                            "menu"),
    ("help",                          "help"),
    ("progress",                      "progress"),
    ("What is 3,475 + 2,618?",        "off-subject math — guard should apply"),
    ("What is a noun?",               "off-subject English — guard should apply"),
    ("I don't understand fractions",  "topic request — bridge should answer"),
]

for msg, label in cases:
    print()
    print(f"IN  [{label}]: {msg!r}")
    try:
        out = wh.route_message(TEST_PHONE, msg) or ""
        preview = out[:200].replace("\n", " ")
        print(f"OUT: {preview}")
    except Exception as e:
        import traceback
        print(f"ERR: {type(e).__name__}: {e}")
        traceback.print_exc()

print()
print("=" * 60)
print("DONE")
print("=" * 60)
