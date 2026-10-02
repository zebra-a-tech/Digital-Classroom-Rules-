from paid_access import register_paid_access
from flask import Flask, request, redirect, url_for
import sqlite3
import random
from datetime import datetime
from marking_flow import register_marking_flow


app = Flask(__name__)
register_marking_flow(app)


DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
TUTORS = [
    "Tariro", "Tendai", "Nyasha", "Tatenda", "Rudo",
    "Blessing", "Brian", "Grace", "Michael", "Sarah"
]


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT,
            lesson_topic TEXT,
            lesson_goal TEXT,
            completed INTEGER DEFAULT 0,
            started_at TEXT,
            completed_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.execute("""
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
            completed_at TEXT,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )
    """)

    conn.commit()
    conn.close()


setup_database()


def lesson_topic(subject):

    subject = (subject or "").lower()

    topics = {
        "maths": "Numbers, Operations and Problem Solving",
        "mathematics": "Numbers, Operations and Problem Solving",
        "english": "Reading, Vocabulary and Sentence Construction",
        "science": "Living Things and Their Environment",
        "social studies": "People, Communities and Society",
        "geography": "Maps, Places and the Environment",
        "history": "Understanding the Past",
        "biology": "Cells, Living Organisms and Life Processes",
        "chemistry": "Matter, Elements and Chemical Reactions",
        "physics": "Forces, Energy and Motion",
        "economics": "Basic Economic Concepts",
        "accounting": "Introduction to Accounting"
    }

    return topics.get(
        subject,
        f"{subject.title()} Fundamentals"
    )


def create_homework(subject, grade):

    subject_lower = (subject or "").lower()

    if subject_lower in ["maths", "mathematics"]:

        return (
            "What is 25 + 17?",
            "42"
        )

    if subject_lower == "english":

        return (
            "Complete the sentence: The boy _____ to school every day.",
            "goes"
        )

    if subject_lower == "science":

        return (
            "What gas do humans need to breathe in order to live?",
            "oxygen"
        )

    if subject_lower == "biology":

        return (
            "What is the basic unit of life?",
            "cell"
        )

    if subject_lower == "chemistry":

        return (
            "What is the chemical symbol for oxygen?",
            "O"
        )

    if subject_lower == "physics":

        return (
            "What force pulls objects toward the Earth?",
            "gravity"
        )

    if subject_lower == "geography":

        return (
            "What instrument is commonly used to find direction?",
            "compass"
        )

    if subject_lower == "history":

        return (
            "What do historians study?",
            "the past"
        )

    if subject_lower == "economics":

        return (
            "What do we call the money received from working?",
            "income"
        )

    if subject_lower == "accounting":

        return (
            "What is the basic accounting equation?",
            "assets = liabilities + capital"
        )

    return (
        f"Explain one important thing you learned about {subject}.",
        ""
    )



# ============================================================
# FOUNDER STUDENT PROFILE
# ============================================================

@app.route("/student/<int:student_id>")
def founder_student_profile(student_id):

    conn = get_db()

    student = conn.execute("""
        SELECT *
        FROM students
        WHERE id=?
    """, (student_id,)).fetchone()

    conn.close()

    if not student:
        return "Student not found", 404

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Student Profile</title>

<style>
body {{
    font-family: Arial, sans-serif;
    background:#f4f6f8;
    padding:20px;
}}

.card {{
    background:white;
    padding:20px;
    border-radius:12px;
    max-width:600px;
    margin:auto;
    box-shadow:0 2px 10px rgba(0,0,0,.08);
}}

h1 {{
    margin-top:0;
}}

.row {{
    padding:10px 0;
    border-bottom:1px solid #eee;
}}

.back {{
    display:inline-block;
    margin-top:20px;
    padding:12px 18px;
    background:#222;
    color:white;
    text-decoration:none;
    border-radius:8px;
}}
</style>
</head>

<body>

<div class="card">

<h1>👨‍🎓 Student Profile</h1>

<div class="row"><b>Student ID:</b> {student["id"]}</div>
<div class="row"><b>Name:</b> {student["name"]}</div>
<div class="row"><b>Age:</b> {student["age"] or "Not set"}</div>
<div class="row"><b>School:</b> {student["school"] or "Not set"}</div>
<div class="row"><b>Location:</b> {student["location"] or "Not set"}</div>
<div class="row"><b>Grade/Form:</b> {student["grade_form"] or "Not set"}</div>
<div class="row"><b>Subject:</b> {student["subject"] or "Not set"}</div>
<div class="row"><b>Exam Board:</b> {student["exam_board"] or "Not set"}</div>
<div class="row"><b>Tutor:</b> {student["tutor"] or "Not assigned"}</div>
<div class="row"><b>Free Trial Used:</b> {student["free_trial_used"] or 0}</div>
<div class="row"><b>Paid Lessons:</b> {student["paid_lessons"] or 0}</div>
<div class="row"><b>Streak:</b> {student["streak"] or 0}</div>

<a class="back" href="/founder/payments">← Back to Agent Control</a>

</div>

</body>
</html>
"""

@app.route("/")
def dashboard():

    conn = get_db()

    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    total_lessons = conn.execute(
        "SELECT COALESCE(SUM(paid_lessons),0) FROM students"
    ).fetchone()[0]

    completed_homework = conn.execute(
        "SELECT COUNT(*) FROM homework WHERE completed=1"
    ).fetchone()[0]

    conn.close()

    student_html = ""

    for s in students:

        student_html += f"""
        <div class="student">

        <strong>DCR-{s['id']:05d}</strong>

        <br>

        <a href="/student/{s['id']}">
        {s['name']}
        </a>

        <br>

        Grade/Form:
        {s['grade_form'] or 'Not set'}

        <br>

        Subject:
        {s['subject'] or 'Not set'}

        <br>

        Tutor:
        {s['tutor'] or 'Not assigned'}

        <a class="profile"
        href="/student/{s['id']}">

        OPEN STUDENT PROFILE

        </a>

        </div>
        """

    return f"""
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Digital Classroom Rules</title>

<style>

body {{
font-family:Arial;
background:#f4f6f8;
margin:0;
padding:15px;
}}

.header {{
background:#111827;
color:white;
padding:20px;
border-radius:15px;
}}

.cards {{
display:grid;
grid-template-columns:1fr 1fr;
gap:10px;
margin-top:15px;
}}

.card {{
background:white;
padding:18px;
border-radius:12px;
}}

.number {{
font-size:28px;
font-weight:bold;
}}

.section {{
background:white;
padding:18px;
margin-top:15px;
border-radius:15px;
}}

.student {{
border:1px solid #ddd;
padding:12px;
margin-top:10px;
border-radius:10px;
}}

a {{
text-decoration:none;
font-weight:bold;
color:#2563eb;
}}

.profile {{
display:block;
background:#2563eb;
color:white;
padding:11px;
text-align:center;
border-radius:8px;
margin-top:10px;
}}

input,select {{
width:100%;
padding:12px;
margin:6px 0;
box-sizing:border-box;
border:1px solid #ddd;
border-radius:8px;
}}

button {{
width:100%;
padding:13px;
background:#111827;
color:white;
border:0;
border-radius:8px;
font-weight:bold;
}}

</style>

</head>

<body>

<div class="header">

<h1>Digital Classroom Rules</h1>

<p>Agent: Lucky Munyanyiwa</p>

<p>Local Learning Management System</p>

</div>


<div class="cards">

<div class="card">
Students
<div class="number">{total_students}</div>
</div>

<div class="card">
Paid Lessons
<div class="number">{total_lessons}</div>
</div>

<div class="card">
Completed Homework
<div class="number">{completed_homework}</div>
</div>

</div>


<div class="section">

<h2>Register New Student</h2>

<form method="POST"
action="/register">

<input
name="name"
placeholder="Student name"
required>

<input
name="age"
type="number"
placeholder="Age">

<input
name="school"
placeholder="School">

<input
name="location"
placeholder="Location">

<input
name="grade_form"
placeholder="Grade / Form">

<input
name="subject"
placeholder="Subject">

<select name="exam_board">

<option>ZIMSEC</option>
<option>Cambridge</option>
<option>Other</option>

</select>

<button>
REGISTER STUDENT
</button>

</form>

</div>


<div class="section">

<h2>Students</h2>

{student_html}

</div>

</body>

</html>
"""


@app.route("/register", methods=["POST"])
def register():

    name = request.form.get("name")
    age = request.form.get("age")
    school = request.form.get("school")
    location = request.form.get("location")
    grade_form = request.form.get("grade_form")
    subject = request.form.get("subject")
    exam_board = request.form.get("exam_board")

    conn = get_db()

    cursor = conn.execute("""
        INSERT INTO students
        (
        name,
        age,
        school,
        location,
        grade_form,
        subject,
        exam_board
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age if age else None,
        school,
        location,
        grade_form,
        subject,
        exam_board
    ))

    student_id = cursor.lastrowid

    tutor = random.choice(TUTORS)

    conn.execute(
        "UPDATE students SET tutor=? WHERE id=?",
        (tutor, student_id)
    )

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "student_profile",
            student_id=student_id
        )
    )


@app.route("/lesson/<int:student_id>")
def lesson(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    if not student:

        conn.close()

        return "Student not found"

    subject = student["subject"] or "General Studies"

    topic = lesson_topic(subject)

    goal = (
        "Understand today's topic, "
        "practise the skill and apply it "
        "to an examination-style question."
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor = conn.execute("""
        INSERT INTO lessons
        (
        student_id,
        subject,
        lesson_topic,
        lesson_goal,
        started_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        topic,
        goal,
        now
    ))

    lesson_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Lesson</title>

<style>

body {{
font-family:Arial;
background:#f4f6f8;
padding:15px;
}}

.header {{
background:#111827;
color:white;
padding:20px;
border-radius:15px;
}}

.lesson {{
background:white;
padding:20px;
margin-top:15px;
border-radius:15px;
}}

.box {{
background:#f3f4f6;
padding:15px;
border-radius:10px;
margin-top:12px;
}}

button {{
width:100%;
padding:15px;
background:#111827;
color:white;
border:0;
border-radius:9px;
font-weight:bold;
margin-top:10px;
}}

a {{
display:block;
text-align:center;
margin-top:15px;
}}

</style>

</head>

<body>

<div class="header">

<h1>📚 Today's Lesson</h1>

<p>{student['name']}</p>

<p>
{student['grade_form'] or ''}
•
{subject}
</p>

<p>
👨‍🏫 Tutor:
{student['tutor'] or 'Tutor'}
</p>

</div>


<div class="lesson">

<h2>{topic}</h2>

<div class="box">

<strong>🎯 Lesson Goal</strong>

<p>{goal}</p>

</div>

<div class="box">

<strong>🚀 Your Mission</strong>

<p>
Study the explanation, practise the skill,
then complete your homework independently.
</p>

</div>

<div class="box">

<strong>💡 Why It Matters</strong>

<p>
Understanding the method helps you answer
real examination questions confidently.
</p>

</div>

<div class="box">

<strong>📖 Tutor Explanation</strong>

<p>
Your tutor will explain the topic step by step,
then guide you through examples.
</p>

</div>

<div class="box">

<strong>📝 Examination Practice</strong>

<p>
Attempt a question related to:
<b>{topic}</b>
</p>

</div>


<form method="POST"
action="/lesson/{student_id}/complete">

<input
type="hidden"
name="lesson_id"
value="{lesson_id}">

<button>
✅ COMPLETE LESSON
</button>

</form>

<a href="/student/{student_id}">
⬅ Back to Profile
</a>

</div>

</body>

</html>
"""


@app.route(
    "/lesson/<int:student_id>/complete",
    methods=["POST"]
)
def complete_lesson(student_id):

    lesson_id = request.form.get("lesson_id")

    conn = get_db()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute("""
        UPDATE lessons
        SET completed=1,
            completed_at=?
        WHERE id=? AND student_id=?
    """, (
        now,
        lesson_id,
        student_id
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "homework",
            student_id=student_id
        )
    )


@app.route("/homework/<int:student_id>")
def homework(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    if not student:

        conn.close()

        return "Student not found"

    subject = student["subject"] or "General Studies"

    question, answer = create_homework(
        subject,
        student["grade_form"]
    )

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor = conn.execute("""
        INSERT INTO homework
        (
        student_id,
        subject,
        topic,
        question,
        correct_answer,
        created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        lesson_topic(subject),
        question,
        answer,
        now
    ))

    homework_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Homework</title>

<style>

body {{
font-family:Arial;
background:#f4f6f8;
padding:15px;
}}

.header {{
background:#111827;
color:white;
padding:20px;
border-radius:15px;
}}

.homework {{
background:white;
padding:20px;
margin-top:15px;
border-radius:15px;
}}

.question {{
font-size:19px;
font-weight:bold;
margin-top:20px;
}}

textarea {{
width:100%;
height:130px;
padding:12px;
box-sizing:border-box;
border:1px solid #ddd;
border-radius:8px;
margin-top:10px;
font-size:16px;
}}

button {{
width:100%;
padding:15px;
background:#111827;
color:white;
border:0;
border-radius:9px;
font-weight:bold;
margin-top:12px;
}}

a {{
display:block;
text-align:center;
margin-top:15px;
}}

</style>

</head>

<body>

<div class="header">

<h1>📝 Homework</h1>

<p>{student['name']}</p>

<p>{subject}</p>

</div>


<div class="homework">

<h2>Your Mission</h2>

<p>
Complete the question without looking
for the answer.
</p>

<div class="question">

{question}

</div>


<form method="POST"
action="/homework/{student_id}/submit">

<input
type="hidden"
name="homework_id"
value="{homework_id}">

<textarea
name="student_answer"
placeholder="Write your answer here..."
required></textarea>

<button>
SUBMIT HOMEWORK
</button>

</form>

<a href="/student/{student_id}">
⬅ Back to Profile
</a>

</div>

</body>

</html>
"""


@app.route(
    "/homework/<int:student_id>/submit",
    methods=["POST"]
)
def submit_homework(student_id):

    homework_id = request.form.get(
        "homework_id"
    )

    student_answer = (
        request.form.get("student_answer")
        or ""
    ).strip()

    conn = get_db()

    homework = conn.execute("""
        SELECT * FROM homework
        WHERE id=? AND student_id=?
    """, (
        homework_id,
        student_id
    )).fetchone()

    if not homework:

        conn.close()

        return "Homework not found"

    correct = (
        homework["correct_answer"]
        or ""
    ).strip().lower()

    given = student_answer.lower()

    if correct and given == correct:

        score = 100

    elif correct and (
        correct in given or
        given in correct
    ):

        score = 50

    elif not correct:

        score = 0

    else:

        score = 0


    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute("""
        UPDATE homework

        SET student_answer=?,
            score=?,
            completed=1,
            completed_at=?

        WHERE id=?
        AND student_id=?
    """, (
        student_answer,
        score,
        now,
        homework_id,
        student_id
    ))

    conn.commit()
    conn.close()

    return redirect(
        url_for(
            "homework_result",
            student_id=student_id,
            homework_id=homework_id
        )
    )


@app.route("/homework/<int:student_id>/result/<int:homework_id>")
def homework_result(student_id, homework_id):

    conn = get_db()

    hw = conn.execute("""
        SELECT *
        FROM homework
        WHERE id=? AND student_id=?
    """, (
        homework_id,
        student_id
    )).fetchone()

    conn.close()

    if not hw:

        return "Homework not found"

    score = hw["score"]

    if score == 100:

        message = "Excellent work! 🌟"

    elif score == 50:

        message = "Good attempt. Let's improve it! 💪"

    else:

        message = "Keep practising. Your tutor will help you. 📚"


    return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Homework Result</title>

<style>

body {{
font-family:Arial;
background:#f4f6f8;
padding:15px;
}}

.result {{
background:white;
padding:25px;
border-radius:15px;
text-align:center;
}}

.score {{
font-size:55px;
font-weight:bold;
}}

.box {{
background:#f3f4f6;
padding:15px;
margin-top:15px;
border-radius:10px;
text-align:left;
}}

a {{
display:block;
margin-top:20px;
}}

</style>

</head>

<body>

<div class="result">

<h1>📊 Homework Result</h1>

<h2>{message}</h2>

<div class="score">
{score}%
</div>

<div class="box">

<strong>Question</strong>

<p>
{hw['question']}
</p>

</div>

<div class="box">

<strong>Your Answer</strong>

<p>
{hw['student_answer']}
</p>

</div>

<div class="box">

<strong>Correct Answer</strong>

<p>
{hw['correct_answer'] or
'Your tutor will review this answer.'}
</p>

</div>

<a href="/progress/{student_id}">
📈 VIEW PROGRESS
</a>

<a href="/student/{student_id}">
⬅ BACK TO PROFILE
</a>

</div>

</body>

</html>
"""


@app.route("/progress/<int:student_id>")
def progress(student_id):

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    homework = conn.execute("""
        SELECT *
        FROM homework
        WHERE student_id=?
        ORDER BY id DESC
    """, (
        student_id,
    )).fetchall()

    lessons = conn.execute("""
        SELECT *
        FROM lessons
        WHERE student_id=?
        ORDER BY id DESC
    """, (
        student_id,
    )).fetchall()

    conn.close()

    lesson_count = len(lessons)

    completed_lessons = sum(
        1 for l in lessons
        if l["completed"]
    )

    completed_homework = sum(
        1 for h in homework
        if h["completed"]
    )

    average = 0

    marked = [
        h["score"]
        for h in homework
        if h["completed"]
    ]

    if marked:
        average = round(
            sum(marked) / len(marked)
        )

    homework_html = ""

    for h in homework:

        status = (
            f"{h['score']}%"
            if h["completed"]
            else "Not submitted"
        )

        homework_html += f"""
        <div class="item">

        <strong>
        {h['topic']}
        </strong>

        <br>

        {h['question']}

        <br><br>

        Result:
        <strong>{status}</strong>

        </div>
        """

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Progress</title>

<style>

body {{
font-family:Arial;
background:#f4f6f8;
padding:15px;
}}

.card {{
background:white;
padding:18px;
border-radius:15px;
margin-bottom:12px;
}}

.big {{
font-size:35px;
font-weight:bold;
}}

.item {{
background:white;
padding:15px;
border-radius:10px;
margin-top:10px;
}}

a {{
display:block;
margin-top:15px;
}}

</style>

</head>

<body>

<h1>📈 Learning Progress</h1>

<p>
{student['name']} —
DCR-{student_id:05d}
</p>


<div class="card">

<div>Lessons Started</div>

<div class="big">
{lesson_count}
</div>

</div>


<div class="card">

<div>Lessons Completed</div>

<div class="big">
{completed_lessons}
</div>

</div>


<div class="card">

<div>Homework Completed</div>

<div class="big">
{completed_homework}
</div>

</div>


<div class="card">

<div>Homework Average</div>

<div class="big">
{average}%
</div>

</div>


<h2>Homework History</h2>

{homework_html or
"<p>No homework submitted yet.</p>"}


<a href="/student/{student_id}">
⬅ BACK TO PROFILE
</a>

</body>

</html>
"""


@app.route("/exam/<int:student_id>")
def exam(student_id):

    return f"""
    <h1>🎯 Exam Countdown</h1>

    <p>
    Student ID:
    DCR-{student_id:05d}
    </p>

    <p>
    Exam countdown system coming next.
    </p>

    <a href="/student/{student_id}">
    ⬅ Back
    </a>
    """


from tutor.routes import register_intelligence_routes
register_intelligence_routes(app)

from multi_homework import register_multi_homework_routes
register_multi_homework_routes(app)

from tutor.recovery import register_recovery_routes
register_recovery_routes(app)

from tutor.session import register_session_routes
register_session_routes(app)




from student_app import register_student_app
register_student_app(app)


# ==============================
# FOUNDER PAYMENT CONTROL
# ==============================
from student_academy import register_founder_academy
register_founder_academy(app)

# ============================================================
# PAID ACCESS MUST LOAD BEFORE FLASK STARTS
# ============================================================
register_paid_access(app)

if __name__ == "__main__":

    print("DIGITAL CLASSROOM RULES")
    print("Local engine: ONLINE")
    print("Student Profile System: READY")
    print("Lesson Engine: READY")
    print("Homework + Marking: READY")
    print("Running on http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000
    )


# ============================================================
# PAID ACCESS / PAYMENT VERIFICATION
# ============================================================
