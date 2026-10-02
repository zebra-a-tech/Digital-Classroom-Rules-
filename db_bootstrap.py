"""
db_bootstrap.py — create the schema and seed the curriculum on first boot.

Reads DB path from environment (DB_PATH) if set, else "digital_classroom.db".
Safe to call on every startup:
  * If the DB file exists and has curriculum rows, does nothing.
  * If the DB file exists but is missing tables, adds them.
  * If the DB file is missing, creates it and seeds curriculum.
"""

import os
import sqlite3
import datetime


HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB = os.path.join(HERE, "digital_classroom.db")


def db_path():
    """Resolve the DB path from DB_PATH env var, else local default."""
    p = os.environ.get("DB_PATH", "").strip()
    if p:
        return p
    return DEFAULT_DB


SCHEMA = [
    # ---------- students ----------
    """
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
        streak INTEGER DEFAULT 0,
        last_activity_date TEXT,
        current_subject TEXT,
        last_study_date TEXT,
        exam_date TEXT,
        referral_code TEXT,
        student_number TEXT
    )
    """,
    # ---------- auth_users ----------
    """
    CREATE TABLE IF NOT EXISTS auth_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_number TEXT UNIQUE NOT NULL,
        email TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        grade_form TEXT,
        exam_board TEXT DEFAULT 'ZIMSEC',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
    """,
    # ---------- curriculum ----------
    """
    CREATE TABLE IF NOT EXISTS curriculum (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade_form TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        lesson_goal TEXT,
        content TEXT,
        tutor_intro TEXT,
        requires_parent_assist TEXT DEFAULT 'NO',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # ---------- student_subjects ----------
    """
    CREATE TABLE IF NOT EXISTS student_subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        added_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # ---------- learning_progress ----------
    """
    CREATE TABLE IF NOT EXISTS learning_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        attempts INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        mastery INTEGER DEFAULT 0,
        last_activity TEXT
    )
    """,
    # ---------- lessons ----------
    """
    CREATE TABLE IF NOT EXISTS lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT,
        lesson_topic TEXT,
        lesson_goal TEXT,
        completed INTEGER DEFAULT 0,
        started_at TEXT,
        completed_at TEXT,
        grade_form TEXT,
        topic TEXT,
        content TEXT,
        requires_parent_assist TEXT,
        tutor_intro TEXT
    )
    """,
    # ---------- homework ----------
    """
    CREATE TABLE IF NOT EXISTS homework (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        lesson_id INTEGER,
        subject TEXT,
        topic TEXT,
        question TEXT,
        correct_answer TEXT,
        student_answer TEXT,
        score INTEGER DEFAULT 0,
        completed INTEGER DEFAULT 0,
        created_at TEXT,
        completed_at TEXT
    )
    """,
    # ---------- assignments ----------
    """
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT,
        total_questions INTEGER DEFAULT 5,
        score INTEGER DEFAULT 0,
        percentage REAL DEFAULT 0,
        completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT,
        requires_work_upload INTEGER DEFAULT 0,
        requires_photo_upload INTEGER DEFAULT 0,
        max_photos INTEGER DEFAULT 1,
        allowed_file_types TEXT DEFAULT 'jpg,jpeg,png,webp',
        max_upload_mb INTEGER DEFAULT 10,
        calculator_allowed INTEGER DEFAULT 0,
        calculator_required INTEGER DEFAULT 0,
        required_materials TEXT,
        due_date TEXT,
        max_marks INTEGER DEFAULT 10,
        marking_scheme TEXT,
        resubmission_allowed INTEGER DEFAULT 1,
        title TEXT,
        name TEXT
    )
    """,
    # ---------- assignment_questions ----------
    """
    CREATE TABLE IF NOT EXISTS assignment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT,
        student_answer TEXT,
        marks INTEGER DEFAULT 1,
        awarded_marks INTEGER DEFAULT 0,
        topic TEXT,
        hint TEXT,
        FOREIGN KEY (assignment_id) REFERENCES assignments(id)
    )
    """,
    # ---------- assignment_submissions ----------
    """
    CREATE TABLE IF NOT EXISTS assignment_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        assignment_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'IN_PROGRESS',
        submitted_at TEXT,
        marked_at TEXT,
        score REAL,
        total_marks REAL,
        percentage REAL,
        automatic_marked INTEGER NOT NULL DEFAULT 0,
        confidence REAL,
        feedback TEXT,
        strengths TEXT,
        weaknesses TEXT,
        recommended_topics TEXT,
        manual_review_required INTEGER NOT NULL DEFAULT 0,
        manual_review_reason TEXT,
        resubmission_requested INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        typed_working TEXT,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (assignment_id) REFERENCES assignments(id)
    )
    """,
    # ---------- student_sessions ----------
    """
    CREATE TABLE IF NOT EXISTS student_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        session_type TEXT,
        started_at TEXT,
        expires_at TEXT,
        completed INTEGER DEFAULT 0,
        paused INTEGER DEFAULT 0,
        paused_at TEXT,
        total_paused_seconds INTEGER DEFAULT 0
    )
    """,
    # ---------- paid_sessions ----------
    """
    CREATE TABLE IF NOT EXISTS paid_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        payment_request_id INTEGER,
        started_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        active INTEGER DEFAULT 1,
        paused INTEGER DEFAULT 0,
        paused_at TEXT,
        total_paused_seconds INTEGER DEFAULT 0,
        subject TEXT,
        student_ref INTEGER
    )
    """,
    # ---------- payment_requests ----------
    """
    CREATE TABLE IF NOT EXISTS payment_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        amount REAL DEFAULT 1.00,
        status TEXT DEFAULT 'PENDING',
        requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
        verified_at TEXT,
        session_started TEXT,
        session_expires TEXT
    )
    """,
    # ---------- tutor_memory ----------
    """
    CREATE TABLE IF NOT EXISTS tutor_memory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        subject TEXT,
        message TEXT,
        response TEXT,
        created_at TEXT
    )
    """,
    # ---------- learning_sessions ----------
    """
    CREATE TABLE IF NOT EXISTS learning_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        session_type TEXT NOT NULL,
        subject TEXT,
        started_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # ---------- weekly_assignments ----------
    """
    CREATE TABLE IF NOT EXISTS weekly_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        week_number INTEGER NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        grade_form TEXT NOT NULL,
        total_questions INTEGER DEFAULT 15,
        score INTEGER DEFAULT 0,
        percentage REAL DEFAULT 0,
        completed INTEGER DEFAULT 0,
        generated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        completed_at TEXT
    )
    """,
    # ---------- weekly_assignment_questions ----------
    """
    CREATE TABLE IF NOT EXISTS weekly_assignment_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        assignment_id INTEGER NOT NULL,
        question_number INTEGER NOT NULL,
        question TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        student_answer TEXT,
        marks INTEGER DEFAULT 1,
        awarded_marks INTEGER DEFAULT 0,
        topic TEXT,
        difficulty TEXT DEFAULT 'medium',
        FOREIGN KEY (assignment_id) REFERENCES weekly_assignments(id)
    )
    """,
    # ---------- academic_tests / exams ----------
    """
    CREATE TABLE IF NOT EXISTS academic_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        percentage INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS academic_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        percentage INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    # ---------- whatsapp_users (for the WhatsApp bridge) ----------
    """
    CREATE TABLE IF NOT EXISTS whatsapp_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT UNIQUE,
        student_id INTEGER,
        name TEXT,
        is_registered INTEGER DEFAULT 1,
        last_seen TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
]


INDEXES = [
    "CREATE INDEX IF NOT EXISTS ix_lp_student ON learning_progress(student_id)",
    "CREATE INDEX IF NOT EXISTS ix_ss_student ON student_sessions(student_id)",
    "CREATE INDEX IF NOT EXISTS ix_pays_student ON paid_sessions(student_id)",
    "CREATE INDEX IF NOT EXISTS ix_cur_subject ON curriculum(subject)",
    "CREATE INDEX IF NOT EXISTS ix_cur_grade ON curriculum(grade_form)",
    "CREATE INDEX IF NOT EXISTS ix_ssub_student ON student_subjects(student_id)",
]


def seed_curriculum(con):
    """Load curriculum rows from curriculum_expansion.py if the table is empty.

    curriculum_expansion.py defines GRADE_FORM_BANDS / CURRICULUM / etc.
    We try several likely variable names, and insert whatever we find.
    Returns number of rows inserted.
    """
    cur = con.cursor()
    n = cur.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
    if n > 0:
        return 0

    try:
        import curriculum_expansion as ce
    except Exception as e:
        print("BOOTSTRAP: curriculum_expansion import failed:", e)
        return 0

    # Try several common shapes
    rows = []

    def collect(name):
        src = getattr(ce, name, None)
        if not src:
            return
        if isinstance(src, dict):
            for k, v in src.items():
                # key may be (subject, topic) or a string
                if isinstance(k, tuple) and len(k) == 2:
                    subject, topic = k
                else:
                    subject = str(k)
                    topic = ""
                if isinstance(v, dict):
                    for band, lesson in v.items():
                        if not isinstance(lesson, dict):
                            continue
                        rows.append((
                            band, subject, topic,
                            lesson.get("objective") or lesson.get("goal") or "",
                            lesson.get("content") or lesson.get("learn") or "",
                            lesson.get("tutor_intro") or "",
                            lesson.get("requires_parent_assist") or "NO",
                        ))

    for name in ("CURRICULUM", "CURRICULUM_EXPANSION", "CURRICULUM_BANK",
                 "LESSONS_EXPANSION", "EXPANSION"):
        collect(name)

    if not rows:
        print("BOOTSTRAP: no curriculum rows found in curriculum_expansion")
        return 0

    cur.executemany("""
        INSERT INTO curriculum
            (grade_form, subject, topic, lesson_goal, content,
             tutor_intro, requires_parent_assist)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, rows)
    con.commit()
    print(f"BOOTSTRAP: inserted {len(rows)} curriculum rows")
    return len(rows)


def ensure_db(path=None):
    """Create schema if missing. Returns the resolved path."""
    path = path or db_path()
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d, exist_ok=True)

    fresh = not os.path.exists(path)
    con = sqlite3.connect(path)
    try:
        if fresh:
            print(f"BOOTSTRAP: {path} not found — creating schema")
        for stmt in SCHEMA:
            con.execute(stmt)
        for stmt in INDEXES:
            try:
                con.execute(stmt)
            except Exception as e:
                print("BOOTSTRAP: index skipped:", e)
        con.commit()

        # Unique index on students.student_number (safe if already unique)
        try:
            con.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS ux_students_student_number
                ON students(student_number)
                WHERE student_number IS NOT NULL AND student_number != ''
            """)
            con.commit()
        except sqlite3.IntegrityError:
            print("BOOTSTRAP: students.student_number duplicates exist — skipped unique index")

        inserted = seed_curriculum(con)
        if inserted:
            print(f"BOOTSTRAP: curriculum seeded with {inserted} rows")

        total = con.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
        print(f"BOOTSTRAP: curriculum rows now = {total}")
    finally:
        con.close()
    return path


if __name__ == "__main__":
    p = ensure_db()
    print("DB ready at:", p)
