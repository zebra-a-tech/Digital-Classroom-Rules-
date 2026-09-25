import sqlite3
from datetime import datetime

DB = "digital_classroom.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_adaptive_tables():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS learning_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            mastery REAL DEFAULT 0,
            last_activity TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutor_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT,
            topic TEXT,
            learner_message TEXT,
            tutor_response TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def record_result(student_id, subject, topic, correct):
    ensure_adaptive_tables()

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, attempts, correct
        FROM learning_topics
        WHERE student_id = ?
        AND subject = ?
        AND topic = ?
    """, (student_id, subject, topic))

    row = cur.fetchone()

    if row:
        attempts = row["attempts"] + 1
        correct_count = row["correct"] + (1 if correct else 0)
        mastery = round((correct_count / attempts) * 100, 1)

        cur.execute("""
            UPDATE learning_topics
            SET attempts = ?,
                correct = ?,
                mastery = ?,
                last_activity = ?
            WHERE id = ?
        """, (
            attempts,
            correct_count,
            mastery,
            datetime.now().isoformat(timespec="seconds"),
            row["id"]
        ))
    else:
        attempts = 1
        correct_count = 1 if correct else 0
        mastery = 100.0 if correct else 0.0

        cur.execute("""
            INSERT INTO learning_topics
            (
                student_id,
                subject,
                topic,
                attempts,
                correct,
                mastery,
                last_activity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            subject,
            topic,
            attempts,
            correct_count,
            mastery,
            datetime.now().isoformat(timespec="seconds")
        ))

    conn.commit()
    conn.close()

    return mastery


def get_mastery(student_id, subject, topic):
    ensure_adaptive_tables()

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM learning_topics
        WHERE student_id = ?
        AND subject = ?
        AND topic = ?
    """, (student_id, subject, topic))

    row = cur.fetchone()
    conn.close()

    if not row:
        return 0.0

    return float(row["mastery"])


def weakest_topics(student_id, subject=None):
    ensure_adaptive_tables()

    conn = db()
    cur = conn.cursor()

    if subject:
        cur.execute("""
            SELECT *
            FROM learning_topics
            WHERE student_id = ?
            AND subject = ?
            ORDER BY mastery ASC, attempts DESC
        """, (student_id, subject))
    else:
        cur.execute("""
            SELECT *
            FROM learning_topics
            WHERE student_id = ?
            ORDER BY mastery ASC, attempts DESC
        """, (student_id,))

    rows = cur.fetchall()
    conn.close()

    return rows


def save_tutor_session(student_id, subject, topic, message, response):
    ensure_adaptive_tables()

    conn = db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tutor_sessions
        (
            student_id,
            subject,
            topic,
            learner_message,
            tutor_response
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        topic,
        message,
        response
    ))

    conn.commit()
    conn.close()
