import sqlite3

DATABASE = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
def connect():
    return sqlite3.connect(DATABASE)

def create_database():
    db = connect()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        school TEXT,
        location TEXT,
        grade_form TEXT,
        subject TEXT,
        exam_board TEXT,
        tutor TEXT,
        registered_at TEXT DEFAULT CURRENT_TIMESTAMP,
        free_trial_used INTEGER DEFAULT 0,
        paid_lessons INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0
    )
    """)

    db.commit()
    db.close()

    print("Digital Classroom Rules database ready.")

if __name__ == "__main__":
    create_database()
