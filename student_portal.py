import sqlite3
from flask import render_template_string, redirect, url_for, request

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
SUBJECTS = [
    "Maths",
    "English",
    "Science",
    "Social Studies",
    "Geography",
    "History",
    "Biology",
    "Chemistry",
    "Physics",
    "Economics",
    "Accounting"
]


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def setup_portal_tables():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add current_subject to students if it doesn't exist
    columns = [
        row["name"]
        for row in cur.execute("PRAGMA table_info(students)").fetchall()
    ]

    if "current_subject" not in columns:
        cur.execute(
            "ALTER TABLE students ADD COLUMN current_subject TEXT"
        )

    conn.commit()
    conn.close()


def register_student_portal(app):

    setup_portal_tables()

    @app.route("/student/<int:student_id>/home")
    def student_home(student_id):

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )
        student = cur.fetchone()

        if not student:
            conn.close()
            return "Student not found.", 404

        cur.execute("""
            SELECT subject
            FROM student_subjects
            WHERE student_id = ? AND active = 1
            ORDER BY subject
        """, (student_id,))

        selected_subjects = [
            row["subject"] for row in cur.fetchall()
        ]

        cur.execute("""
            SELECT subject, topic, mastery
            FROM learning_topics
            WHERE student_id = ?
            ORDER BY mastery ASC
            LIMIT 5
        """, (student_id,))

        weak_topics = cur.fetchall()

        current_subject = student["current_subject"]

        conn.close()

        # Make sure current subject is still selected
        if current_subject not in selected_subjects:
            current_subject = None

        subject_cards = ""

        for subject in SUBJECTS:

            selected = subject in selected_subjects

            if selected:
                button = f"""
                <a class="selected"
                   href="/student/{student_id}/select-subject?subject={subject}">
                   ✓ Selected
                </a>
                """
            else:
                button = f"""
                <a
                   href="/student/{student_id}/select-subject?subject={subject}">
                   Choose
                </a>
                """

            subject_cards += f"""
            <div class="subject">
                <div>
                    <strong>{subject}</strong>
                    <br>
                    <small>
                        {"Currently selected" if selected else "Add this subject"}
                    </small>
                </div>
                {button}
            </div>
            """

        if selected_subjects:

            selected_text = ", ".join(selected_subjects)

            if current_subject:
                current_box = f"""
                <div class="current">
                    🎯 <strong>Current subject:</strong>
                    {current_subject}

                    <a href="/session/{student_id}?type=trial&subject={current_subject}">
                        Start Learning
                    </a>
                </div>
                """
            else:
                current_box = """
                <div class="notice">
                    Choose a subject below to make it your current subject.
                </div>
                """

        else:

            selected_text = "None selected yet."

            current_box = """
            <div class="notice">
                👆 Please select at least one subject below.
            </div>
            """

        weak_html = ""

        if weak_topics:

            for row in weak_topics:

                mastery = row["mastery"] or 0

                weak_html += f"""
                <div class="weak">
                    <strong>{row["subject"]}</strong>
                    — {row["topic"]}

                    <br>

                    <small>
                        Mastery: {mastery:.0f}%
                    </small>
                </div>
                """

        else:

            weak_html = """
            <div class="weak">
                Your learning weaknesses will appear here as you complete
                lessons and homework.
            </div>
            """

        html = f"""
        <!DOCTYPE html>

        <html>

        <head>

            <meta name="viewport"
                  content="width=device-width, initial-scale=1">

            <title>Digital Classroom Student Portal</title>

            <style>

                body {{
                    font-family: Arial, sans-serif;
                    background: #f4f7fb;
                    margin: 0;
                    padding: 15px;
                }}

                .container {{
                    max-width: 720px;
                    margin: auto;
                }}

                .header {{
                    background: linear-gradient(
                        135deg,
                        #123c69,
                        #1f6f8b
                    );

                    color: white;
                    padding: 24px;
                    border-radius: 18px;
                    margin-bottom: 15px;
                }}

                .header h1 {{
                    margin-top: 0;
                }}

                .card {{
                    background: white;
                    padding: 18px;
                    border-radius: 16px;
                    margin-bottom: 15px;

                    box-shadow:
                        0 3px 12px rgba(0,0,0,0.08);
                }}

                .subject {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    gap: 10px;

                    background: #f7f9fc;

                    padding: 14px;

                    border-radius: 12px;

                    margin: 8px 0;
                }}

                .subject a {{
                    background: #123c69;
                    color: white;

                    text-decoration: none;

                    padding: 9px 13px;

                    border-radius: 9px;

                    font-size: 13px;
                }}

                .subject a.selected {{
                    background: #16803a;
                }}

                .current {{
                    background: #e8f7ed;

                    border-radius: 12px;

                    padding: 15px;

                    margin-top: 15px;
                }}

                .current a {{
                    display: block;

                    background: #16803a;

                    color: white;

                    text-decoration: none;

                    text-align: center;

                    padding: 12px;

                    border-radius: 10px;

                    margin-top: 12px;
                }}

                .notice {{
                    background: #fff8df;

                    padding: 14px;

                    border-radius: 10px;

                    margin-top: 15px;
                }}

                .weak {{
                    background: #fff8e6;

                    padding: 12px;

                    border-radius: 10px;

                    margin: 8px 0;
                }}

                .stats {{
                    display: grid;

                    grid-template-columns:
                    repeat(3, 1fr);

                    gap: 8px;
                }}

                .stat {{
                    background: #f4f7fb;

                    padding: 12px;

                    text-align: center;

                    border-radius: 12px;
                }}

                .stat strong {{
                    display: block;

                    font-size: 20px;
                }}

                .buttons a {{
                    display: block;

                    text-align: center;

                    background: #123c69;

                    color: white;

                    text-decoration: none;

                    padding: 12px;

                    border-radius: 10px;

                    margin-top: 8px;
                }}

            </style>

        </head>

        <body>

        <div class="container">

            <div class="header">

                <h1>
                    Welcome, {student["name"]} 👋
                </h1>

                <p>
                    <strong>Digital Classroom Rules</strong>
                </p>

                <p>
                    Your personal learning centre
                </p>

                <p>
                    🧑‍🏫 Tutor:
                    <strong>{student["tutor"] or "Your tutor"}</strong>
                </p>

            </div>


            <div class="card">

                <h2>📊 Your Learning Profile</h2>

                <div class="stats">

                    <div class="stat">

                        <strong>
                            {student["grade_form"] or "-"}
                        </strong>

                        Grade/Form

                    </div>


                    <div class="stat">

                        <strong>
                            {student["streak"] or 0}
                        </strong>

                        🔥 Streak

                    </div>


                    <div class="stat">

                        <strong>
                            {student["paid_lessons"] or 0}
                        </strong>

                        Lessons

                    </div>

                </div>

            </div>


            <div class="card">

                <h2>📚 What do you want to study?</h2>

                <p>
                    You can choose <strong>one or multiple subjects</strong>.
                </p>

                <p>
                    <strong>Your subjects:</strong><br>
                    {selected_text}
                </p>

                {current_box}

            </div>


            <div class="card">

                <h2>📖 Select Your Subjects</h2>

                {subject_cards}

            </div>


            <div class="card">

                <h2>🧠 Topics To Improve</h2>

                {weak_html}

            </div>


            <div class="card buttons">

                <h2>🚀 Learning Centre</h2>

                <a href="/tutor/{student_id}">
                    🧑‍🏫 Ask Your Tutor
                </a>

                <a href="/homework/{student_id}">
                    📝 Homework
                </a>

                <a href="/student/{student_id}">
                    👤 My Profile
                </a>

                <a href="/lesson/{student_id}">
                    📖 Lesson Engine
                </a>

            </div>

        </div>

        </body>

        </html>
        """

        return render_template_string(html)


    @app.route("/student/<int:student_id>/select-subject")
    def select_subject(student_id):

        subject = request.args.get("subject", "").strip()

        if subject not in SUBJECTS:
            return "Invalid subject.", 400

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT id FROM students WHERE id = ?",
            (student_id,)
        )

        if not cur.fetchone():
            conn.close()
            return "Student not found.", 404

        cur.execute("""
            SELECT id, active
            FROM student_subjects
            WHERE student_id = ? AND subject = ?
        """, (student_id, subject))

        existing = cur.fetchone()

        if existing:

            if existing["active"] == 1:

                # Remove subject
                cur.execute("""
                    UPDATE student_subjects
                    SET active = 0
                    WHERE id = ?
                """, (existing["id"],))

                # If it was current subject, clear it
                cur.execute("""
                    UPDATE students
                    SET current_subject = NULL
                    WHERE id = ? AND current_subject = ?
                """, (student_id, subject))

            else:

                # Reactivate subject
                cur.execute("""
                    UPDATE student_subjects
                    SET active = 1
                    WHERE id = ?
                """, (existing["id"],))

        else:

            cur.execute("""
                INSERT INTO student_subjects
                (student_id, subject, active)
                VALUES (?, ?, 1)
            """, (student_id, subject))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "student_home",
                student_id=student_id
            )
        )


    @app.route("/student/<int:student_id>/current-subject")
    def set_current_subject(student_id):

        subject = request.args.get("subject", "").strip()

        if subject not in SUBJECTS:
            return "Invalid subject.", 400

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT id
            FROM student_subjects
            WHERE student_id = ?
              AND subject = ?
              AND active = 1
        """, (student_id, subject))

        if not cur.fetchone():
            conn.close()

            return redirect(
                url_for(
                    "student_home",
                    student_id=student_id
                )
            )

        cur.execute("""
            UPDATE students
            SET current_subject = ?
            WHERE id = ?
        """, (subject, student_id))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "student_home",
                student_id=student_id
            )
        )


print("Student Portal Phase 2 loaded successfully.")
