import sqlite3
from datetime import datetime, timedelta
from flask import request, redirect, url_for, render_template_string

DB = "digital_classroom.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def setup_session_database():

    conn = db()
    cur = conn.cursor()

    cur.execute("""
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
    """)

    conn.commit()
    conn.close()


def register_session_routes(app):

    setup_session_database()

    @app.route("/session/<int:student_id>")
    def start_session(student_id):

        subject = request.args.get("subject", "Maths")
        session_type = request.args.get("type", "trial").lower()

        if session_type not in ["trial", "paid"]:
            session_type = "trial"

        duration_minutes = 30 if session_type == "trial" else 60

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM students
            WHERE id = ?
        """, (student_id,))

        student = cur.fetchone()

        if not student:
            conn.close()
            return "Student not found", 404

        # ========================================================
        # MASTER PAID SESSION
        # ========================================================
        # Paid lessons MUST use paid_sessions.expires_at.
        # Never create a second learning_sessions timer.
        # ========================================================

        if session_type == "paid":
            # ====================================================
            # MASTER PAID SESSION
            # NEVER create a second Tutor timer.
            # ====================================================
            try:
                from paid_access import active_paid_session

                paid = active_paid_session(student_id)

                if paid:
                    # Send the student to the master paid lesson.
                    return redirect(
                        f"/student/{student_id}/session/0"
                    )

                return redirect(
                    f"/student/{student_id}/pay"
                )

            except Exception:
                return redirect(
                    f"/student/{student_id}/pay"
                )

        # Only allow the FREE trial once.
        if session_type == "trial":

            if student["free_trial_used"]:
                conn.close()

                return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Free Trial</title>
<style>
body {
    font-family: Arial;
    background: #f4f7fb;
    padding: 20px;
}
.card {
    max-width: 650px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}
a {
    display: block;
    padding: 14px;
    margin-top: 15px;
    background: #17365d;
    color: white;
    text-decoration: none;
    border-radius: 10px;
}
</style>
</head>
<body>
<div class="card">

<h1>🆓 FREE TRIAL</h1>

<p>
Hi {{ student["name"] }} ❤️
</p>

<p>
Your 30-minute free trial has already been used.
</p>

<p>
You can continue learning with a paid
<strong>1-hour session for $1 USD.</strong>
</p>

<a href="{{ url_for(
    'start_session',
    student_id=student_id,
    subject=subject,
    type='paid'
) }}">
Start 1-Hour Session — $1
</a>

</div>
</body>
</html>
                """,
                student=student,
                student_id=student_id,
                subject=subject
                )

        started = datetime.now()
        expires = started + timedelta(minutes=duration_minutes)

        cur.execute("""
            INSERT INTO learning_sessions
            (
                student_id,
                session_type,
                subject,
                started_at,
                expires_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            student_id,
            session_type,
            subject,
            started.isoformat(),
            expires.isoformat()
        ))

        session_id = cur.lastrowid

        if session_type == "trial":
            cur.execute("""
                UPDATE students
                SET free_trial_used = 1
                WHERE id = ?
            """, (student_id,))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "active_session",
                session_id=session_id
            )
        )


    @app.route("/session/active/<int:session_id>")
    def active_session(session_id):

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                learning_sessions.*,
                students.name
            FROM learning_sessions
            JOIN students
            ON students.id = learning_sessions.student_id
            WHERE learning_sessions.id = ?
        """, (session_id,))

        session = cur.fetchone()

        conn.close()

        if not session:
            return "Session not found", 404

        expires = datetime.fromisoformat(
            session["expires_at"]
        )

        remaining = int(
            (expires - datetime.now()).total_seconds()
        )

        if remaining <= 0:

            conn = db()
            cur = conn.cursor()

            cur.execute("""
                UPDATE learning_sessions
                SET completed = 1
                WHERE id = ?
            """, (session_id,))

            conn.commit()
            conn.close()

            return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Session Complete</title>
<style>
body {
    font-family: Arial;
    background: #f4f7fb;
    padding: 20px;
}
.card {
    max-width: 650px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}
</style>
</head>
<body>
<div class="card">

<h1>🎉 Session Complete!</h1>

<p>
Well done, {{ session["name"] }} ❤️
</p>

{% if session["session_type"] == "trial" %}

<p>
Your <strong>30-minute FREE trial</strong> has finished.
</p>

<p>
Ready to continue learning?
</p>

<h2>$1 USD = 1 Hour</h2>

{% else %}

<p>
Your <strong>1-hour paid lesson</strong> has finished.
</p>

<p>
Excellent work. Keep building your knowledge! 🔥
</p>

{% endif %}

</div>
</body>
</html>
            """,
            session=session
            )

        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning Session</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    margin: 0;
    padding: 20px;
}

.card {
    max-width: 750px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,.08);
}

.timer {
    text-align: center;
    font-size: 38px;
    font-weight: bold;
    padding: 20px;
    background: #eef4ff;
    border-radius: 15px;
}

.badge {
    display: inline-block;
    padding: 8px 12px;
    border-radius: 20px;
    background: #17365d;
    color: white;
}

a {
    display: block;
    padding: 14px;
    margin-top: 20px;
    background: #17365d;
    color: white;
    text-decoration: none;
    border-radius: 10px;
    text-align: center;
}
</style>

<script>
let seconds = {{ remaining }};

function updateTimer() {

    if (seconds <= 0) {
        window.location.href =
            "{{ url_for(
                'active_session',
                session_id=session['id']
            ) }}";
        return;
    }

    let minutes = Math.floor(seconds / 60);
    let secs = seconds % 60;

    document.getElementById("timer").innerText =
        String(minutes).padStart(2, "0") +
        ":" +
        String(secs).padStart(2, "0");

    seconds--;
}

setInterval(updateTimer, 1000);
</script>

</head>

<body>

<div class="card">

<h1>📚 Learning Session</h1>

<p>
Welcome {{ session["name"] }} ❤️
</p>

<span class="badge">
{% if session["session_type"] == "trial" %}
FREE 30-MINUTE TRIAL
{% else %}
$1 — 1-HOUR SESSION
{% endif %}
</span>

<h2>Subject: {{ session["subject"] }}</h2>

<div class="timer" id="timer">
Loading...
</div>

<h2>🧑‍🏫 Your Tutor</h2>

<p>
Your tutor is ready to teach, explain difficult topics,
give examples, ask questions and help you prepare for exams.
</p>

<a href="{{ url_for(
    'tutor_page',
    student_id=session['student_id']
) }}">
🧑‍🏫 Open My Tutor
</a>

<a href="{{ url_for(
    'multi_homework',
    student_id=session['student_id'],
    subject=session['subject']
) }}">
📝 Practice Homework
</a>

</div>

</body>
</html>
        """,
        session=session,
        remaining=remaining
        )
