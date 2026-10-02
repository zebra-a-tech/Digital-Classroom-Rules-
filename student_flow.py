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


def get_student(student_id):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cur.fetchone()
    conn.close()

    return student


def get_selected_subjects(student_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT subject
        FROM student_subjects
        WHERE student_id = ?
        AND active = 1
        ORDER BY subject
    """, (student_id,))

    subjects = [row["subject"] for row in cur.fetchall()]

    conn.close()

    return subjects


def get_current_subject(student_id):

    student = get_student(student_id)

    if not student:
        return None

    try:
        current = student["current_subject"]
    except Exception:
        current = None

    subjects = get_selected_subjects(student_id)

    if current in subjects:
        return current

    if subjects:
        return subjects[0]

    return None


def register_student_flow(app):

    # -------------------------------------------------
    # STUDENT LEARNING CENTRE
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/subject")
    def student_subject(student_id):

        student = get_student(student_id)

        if not student:
            return "Student not found.", 404

        subjects = get_selected_subjects(student_id)
        current = get_current_subject(student_id)

        if not current:
            return redirect(
                url_for(
                    "student_home",
                    student_id=student_id
                )
            )

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{{ current }} Learning Centre</title>

<style>

body {
    margin: 0;
    padding: 15px;
    background: #f4f7fb;
    font-family: Arial, sans-serif;
}

.container {
    max-width: 720px;
    margin: auto;
}

.header {
    background: linear-gradient(
        135deg,
        #123c69,
        #1f6f8b
    );

    color: white;
    padding: 24px;

    border-radius: 18px;

    margin-bottom: 15px;
}

.card {
    background: white;

    padding: 18px;

    border-radius: 16px;

    margin-bottom: 15px;

    box-shadow:
        0 3px 12px rgba(0,0,0,0.08);
}

.current {
    background: #e8f7ed;

    border: 2px solid #16803a;

    padding: 16px;

    border-radius: 14px;

    margin-bottom: 15px;
}

.action {
    display: block;

    padding: 16px;

    margin: 10px 0;

    border-radius: 12px;

    text-decoration: none;

    text-align: center;

    font-weight: bold;

    color: white;
}

.trial {
    background: #16803a;
}

.paid {
    background: #123c69;
}

.homework {
    background: #7a4b00;
}

.tutor {
    background: #6a3dad;
}

.progress {
    background: #176b87;
}

.back {
    background: #555;
}

.subject {
    display: block;

    padding: 13px;

    margin: 7px 0;

    background: #f4f7fb;

    border-radius: 10px;

    text-decoration: none;

    color: #123c69;
}

.selected {
    background: #e8f7ed;

    border: 2px solid #16803a;
}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>🎓 {{ current }}</h1>

<p>
Welcome {{ student["name"] }} 👋
</p>

<p>
<strong>Digital Classroom Rules</strong>
</p>

<p>
Your personal {{ current }} learning centre
</p>

</div>


<div class="current">

<h2>🎯 Current Subject</h2>

<h3>{{ current }}</h3>

<p>
Everything below is now focused on
<strong>{{ current }}</strong>.
</p>

</div>


<div class="card">

<h2>🚀 Start Learning</h2>

<p>
Choose how you want to learn today.
</p>

<a class="action trial"
href="/student/{{ student['id'] }}/trial?subject={{ current }}">
🎁 FREE 30-Minute Trial
</a>

<a class="action paid"
href="/student/{{ student['id'] }}/paid?subject={{ current }}">
💵 $1 — 1-Hour Lesson
</a>

</div>


<div class="card">

<h2>📚 {{ current }} Learning Tools</h2>

<a class="action homework"
href="/student/{{ student['id'] }}/homework?subject={{ current }}">
📝 {{ current }} Homework
</a>

<a class="action tutor"
href="/student/{{ student['id'] }}/tutor?subject={{ current }}">
🧑‍🏫 {{ current }} Tutor
</a>

<a class="action progress"
href="/student/{{ student['id'] }}/progress?subject={{ current }}">
📊 {{ current }} Progress
</a>

</div>


<div class="card">

<h2>🔄 Switch Subject</h2>

<p>
Your selected subjects:
</p>

{% for subject in subjects %}

<a
class="subject {% if subject == current %}selected{% endif %}"
href="/student/{{ student['id'] }}/set-current?subject={{ subject }}"
>

{% if subject == current %}
🎯
{% endif %}

{{ subject }}

</a>

{% endfor %}

</div>


<div class="card">

<a class="action back"
href="/student/{{ student['id'] }}/home">
← Back to Student Portal
</a>

</div>

</div>

</body>
</html>
""",
            student=student,
            current=current,
            subjects=subjects
        )


    # -------------------------------------------------
    # SET CURRENT SUBJECT
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/set-current")
    def set_current(student_id):

        subject = request.args.get("subject", "").strip()

        if subject not in SUBJECTS:
            return "Invalid subject.", 400

        selected = get_selected_subjects(student_id)

        if subject not in selected:
            return redirect(
                url_for(
                    "student_home",
                    student_id=student_id
                )
            )

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            UPDATE students
            SET current_subject = ?
            WHERE id = ?
        """, (subject, student_id))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "student_subject",
                student_id=student_id
            )
        )


    # -------------------------------------------------
    # STUDENT FREE TRIAL PAGE
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/trial")
    def student_trial(student_id):

        student = get_student(student_id)

        subject = request.args.get("subject", "").strip()

        if not student:
            return "Student not found.", 404

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Free Trial</title>

<style>

body {
    font-family: Arial;
    background: #f4f7fb;
    padding: 15px;
}

.box {
    max-width: 600px;
    margin: auto;

    background: white;

    padding: 25px;

    border-radius: 18px;

    text-align: center;

    box-shadow: 0 3px 12px rgba(0,0,0,.08);
}

.start {
    display: block;

    background: #16803a;

    color: white;

    padding: 15px;

    border-radius: 12px;

    text-decoration: none;

    margin-top: 15px;
}

.back {
    display: block;

    margin-top: 10px;

    padding: 12px;

    text-decoration: none;
}

</style>

</head>

<body>

<div class="box">

<h1>🎁 FREE TRIAL</h1>

<h2>{{ subject }}</h2>

<p>
Hello {{ student["name"] }} 👋
</p>

<h3>30-MINUTE FREE TRIAL</h3>

<p>
You are about to start your free
{{ subject }} learning session.
</p>

<p>
Your tutor will guide you through the lesson,
practice questions and exam preparation.
</p>

<a class="start"
href="/session/{{ student['id'] }}?type=trial&subject={{ subject }}">
▶ START 30-MINUTE TRIAL
</a>

<a class="back"
href="/student/{{ student['id'] }}/subject">
← Back
</a>

</div>

</body>
</html>
""",
            student=student,
            subject=subject
        )


    # -------------------------------------------------
    # STUDENT PAID LESSON PAGE
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/paid")
    def student_paid(student_id):

        student = get_student(student_id)

        subject = request.args.get("subject", "").strip()

        if not student:
            return "Student not found.", 404

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>1 Hour Lesson</title>

<style>

body {
    font-family: Arial;
    background: #f4f7fb;
    padding: 15px;
}

.box {
    max-width: 600px;
    margin: auto;

    background: white;

    padding: 25px;

    border-radius: 18px;

    text-align: center;

    box-shadow: 0 3px 12px rgba(0,0,0,.08);
}

.pay {
    background: #123c69;

    color: white;

    padding: 15px;

    border-radius: 12px;

    text-decoration: none;

    display: block;

    margin-top: 15px;
}

</style>

</head>

<body>

<div class="box">

<h1>💵 1-HOUR LESSON</h1>

<h2>{{ subject }}</h2>

<h2>$1 USD</h2>

<p>
One complete 60-minute {{ subject }}
learning session.
</p>

<p>
Your lesson includes teaching,
practice and exam-focused work.
</p>

<a class="pay"
href="/session/{{ student['id'] }}?type=paid&subject={{ subject }}">
▶ CONTINUE TO 1-HOUR SESSION
</a>

</div>

</body>
</html>
""",
            student=student,
            subject=subject
        )


    # -------------------------------------------------
    # STUDENT TUTOR
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/tutor")
    def student_tutor(student_id):

        student = get_student(student_id)

        subject = request.args.get("subject", "").strip()

        if not student:
            return "Student not found.", 404

        if subject not in get_selected_subjects(student_id):
            return redirect(
                url_for(
                    "student_home",
                    student_id=student_id
                )
            )

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{{ subject }} Tutor</title>

<style>

body {
    font-family: Arial;
    background: #f4f7fb;
    padding: 15px;
}

.box {
    max-width: 700px;
    margin: auto;

    background: white;

    padding: 20px;

    border-radius: 18px;
}

textarea {
    width: 100%;

    min-height: 130px;

    box-sizing: border-box;

    padding: 12px;

    border-radius: 10px;

    border: 1px solid #ccc;
}

button {
    width: 100%;

    margin-top: 10px;

    padding: 14px;

    border: 0;

    border-radius: 10px;

    background: #6a3dad;

    color: white;

    font-weight: bold;
}

.back {
    display: block;

    text-align: center;

    margin-top: 15px;
}

</style>

</head>

<body>

<div class="box">

<h1>🧑‍🏫 {{ subject }} Tutor</h1>

<p>
Hello {{ student["name"] }} 👋
</p>

<p>
Ask your tutor anything about
<strong>{{ subject }}</strong>.
</p>

<form method="GET"
action="/tutor/{{ student['id'] }}">

<input type="hidden"
name="subject"
value="{{ subject }}">

<textarea
name="message"
placeholder="Type your {{ subject }} question here..."
></textarea>

<button type="submit">
ASK {{ subject.upper() }} TUTOR
</button>

</form>

<a class="back"
href="/student/{{ student['id'] }}/subject">
← Back to {{ subject }} Learning Centre
</a>

</div>

</body>
</html>
""",
            student=student,
            subject=subject
        )


    # -------------------------------------------------
    # STUDENT HOMEWORK
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/homework")
    def student_homework(student_id):

        student = get_student(student_id)

        subject = request.args.get("subject", "").strip()

        if not student:
            return "Student not found.", 404

        if subject not in get_selected_subjects(student_id):
            return redirect(
                url_for(
                    "student_home",
                    student_id=student_id
                )
            )

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{{ subject }} Homework</title>

<style>

body {
    font-family: Arial;

    background: #f4f7fb;

    padding: 15px;
}

.box {
    max-width: 650px;

    margin: auto;

    background: white;

    padding: 22px;

    border-radius: 18px;
}

.start {
    display: block;

    background: #7a4b00;

    color: white;

    padding: 15px;

    border-radius: 12px;

    text-align: center;

    text-decoration: none;

    margin-top: 15px;
}

.back {
    display: block;

    text-align: center;

    margin-top: 15px;
}

</style>

</head>

<body>

<div class="box">

<h1>📝 {{ subject }} Homework</h1>

<p>
Hello {{ student["name"] }}.
</p>

<p>
Your homework will be based on
<strong>{{ subject }}</strong>.
</p>

<p>
You will receive multiple questions,
submit your answers and receive your score.
</p>

<a class="start"
href="/homework/{{ student['id'] }}?subject={{ subject }}">
▶ START {{ subject.upper() }} HOMEWORK
</a>

<a class="back"
href="/student/{{ student['id'] }}/subject">
← Back to Learning Centre
</a>

</div>

</body>
</html>
""",
            student=student,
            subject=subject
        )


    # -------------------------------------------------
    # STUDENT PROGRESS
    # -------------------------------------------------

    @app.route("/student/<int:student_id>/progress")
    def student_progress(student_id):

        student = get_student(student_id)

        subject = request.args.get("subject", "").strip()

        if not student:
            return "Student not found.", 404

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                topic,
                attempts,
                correct,
                mastery
            FROM learning_topics
            WHERE student_id = ?
            AND subject = ?
            ORDER BY mastery ASC
        """, (student_id, subject))

        topics = cur.fetchall()

        conn.close()

        return render_template_string("""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>{{ subject }} Progress</title>

<style>

body {
    font-family: Arial;

    background: #f4f7fb;

    padding: 15px;
}

.box {
    max-width: 700px;

    margin: auto;
}

.card {
    background: white;

    padding: 18px;

    border-radius: 16px;

    margin-bottom: 12px;
}

.topic {
    background: #f4f7fb;

    padding: 12px;

    border-radius: 10px;

    margin-top: 8px;
}

.back {
    display: block;

    background: #123c69;

    color: white;

    text-align: center;

    padding: 13px;

    border-radius: 10px;

    text-decoration: none;
}

</style>

</head>

<body>

<div class="box">

<div class="card">

<h1>📊 {{ subject }} Progress</h1>

<p>
Learner: <strong>{{ student["name"] }}</strong>
</p>

</div>

<div class="card">

<h2>🧠 Topic Mastery</h2>

{% if topics %}

{% for topic in topics %}

<div class="topic">

<strong>{{ topic["topic"] }}</strong>

<br>

Attempts:
{{ topic["attempts"] or 0 }}

<br>

Correct:
{{ topic["correct"] or 0 }}

<br>

Mastery:
<strong>
{{ "%.0f"|format(topic["mastery"] or 0) }}%
</strong>

</div>

{% endfor %}

{% else %}

<p>
No progress has been recorded yet.
Complete lessons and homework to build
your {{ subject }} progress.
</p>

{% endif %}

</div>

<a class="back"
href="/student/{{ student['id'] }}/subject">
← Back to {{ subject }} Learning Centre
</a>

</div>

</body>
</html>
""",
            student=student,
            subject=subject,
            topics=topics
        )


print("Student-only learning flow loaded successfully.")
