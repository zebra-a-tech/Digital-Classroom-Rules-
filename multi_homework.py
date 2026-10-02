import sqlite3
from datetime import date, timedelta
from flask import request, redirect, url_for, render_template_string

from tutor.intelligence import detect_topic, check_answer
from tutor.adaptive import record_result, get_mastery

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(table, column, definition):
    conn = db()
    cur = conn.cursor()

    cur.execute(f"PRAGMA table_info({table})")
    columns = [row["name"] for row in cur.fetchall()]

    if column not in columns:
        cur.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
        )

    conn.commit()
    conn.close()


def setup_homework_database():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
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
            completed_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS assignment_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER NOT NULL,
            question_number INTEGER NOT NULL,
            question TEXT NOT NULL,
            correct_answer TEXT,
            student_answer TEXT,
            marks INTEGER DEFAULT 1,
            awarded_marks INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

    ensure_column(
        "assignment_questions",
        "topic",
        "TEXT"
    )

    ensure_column(
        "students",
        "last_activity_date",
        "TEXT"
    )


def questions_for(subject):
    subject = subject.lower().strip()

    banks = {

        "maths": [
            ("What is 25 + 37?", "62"),
            ("What is 9 × 7?", "63"),
            ("What is 84 ÷ 7?", "12"),
            ("What is 3/4 + 1/4?", "1"),
            ("What is 20% of 50?", "10")
        ],

        "english": [
            ("Identify the noun: The boy kicked the ball.", "boy"),
            ("What is the past tense of go?", "went"),
            ("Choose the correct word: She ___ happy. (is/are)", "is"),
            ("Write the plural of child.", "children"),
            ("What is the opposite of hot?", "cold")
        ],

        "science": [
            ("Which organ pumps blood around the body?", "heart"),
            ("What process do plants use to make food?", "photosynthesis"),
            ("Name one state of matter.", "solid"),
            ("What force pulls objects towards Earth?", "gravity"),
            ("Which gas do humans need for breathing?", "oxygen")
        ],

        "biology": [
            ("What is the basic unit of life?", "cell"),
            ("What process do plants use to make food?", "photosynthesis"),
            ("Which organ pumps blood around the body?", "heart"),
            ("Which gas is needed for aerobic respiration?", "oxygen"),
            ("What organ is mainly responsible for breathing?", "lungs")
        ],

        "chemistry": [
            ("What are the tiny particles that make up elements called?", "atoms"),
            ("What element does the symbol O represent?", "oxygen"),
            ("What element does the symbol H represent?", "hydrogen"),
            ("What is the pH of a neutral substance?", "7"),
            ("Name one state of matter.", "solid")
        ],

        "physics": [
            ("What force pulls objects towards Earth?", "gravity"),
            ("What do we call a change in position over time?", "motion"),
            ("What is the unit of force?", "newton"),
            ("What is the unit of electrical current?", "ampere"),
            ("What type of energy does a moving object have?", "kinetic")
        ],

        "geography": [
            ("What is the largest continent?", "asia"),
            ("What is the longest river in Africa?", "nile"),
            ("What is the capital of Zimbabwe?", "harare"),
            ("What do we call the study of weather?", "meteorology"),
            ("Name one type of rainfall.", "relief")
        ],

        "history": [
            ("Who was the first President of Zimbabwe?", "canaan banana"),
            ("In which year did Zimbabwe gain independence?", "1980"),
            ("What was Zimbabwe previously called?", "rhodesia"),
            ("What is a primary historical source?", "original source"),
            ("What do we call the study of past events?", "history")
        ],

        "economics": [
            ("What is the reward for labour?", "wages"),
            ("What is the reward for capital?", "interest"),
            ("What is the reward for land?", "rent"),
            ("What is the reward for entrepreneurship?", "profit"),
            ("What happens when demand increases while supply stays constant?", "price increases")
        ],

        "accounting": [
            ("What is the basic accounting equation?", "assets = capital + liabilities"),
            ("What do we call money owed by a business?", "liability"),
            ("What do we call money owned by a business?", "asset"),
            ("What is money received by a business called?", "income"),
            ("What is money spent by a business called?", "expense")
        ],

        "social studies": [
            ("What is a family?", "a group of related people"),
            ("What is a community?", "a group of people living together"),
            ("What is a citizen?", "a member of a country"),
            ("Name one human right.", "education"),
            ("What is democracy?", "government by the people")
        ]
    }

    return banks.get(subject, [
        ("Explain one important idea you have learned in this subject.", ""),
        ("Name one thing you know about this subject.", ""),
        ("Give one example related to this subject.", ""),
        ("Explain why this subject is important.", ""),
        ("Write one question you have about this subject.", "")
    ])


def update_streak(student_id):
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        SELECT streak, last_activity_date
        FROM students
        WHERE id = ?
    """, (student_id,))

    student = cur.fetchone()

    if not student:
        conn.close()
        return

    today = date.today()
    today_string = today.isoformat()

    last = student["last_activity_date"]
    streak = student["streak"] or 0

    if last == today_string:
        new_streak = streak
    elif last == (today - timedelta(days=1)).isoformat():
        new_streak = streak + 1
    else:
        new_streak = 1

    cur.execute("""
        UPDATE students
        SET streak = ?,
            last_activity_date = ?
        WHERE id = ?
    """, (
        new_streak,
        today_string,
        student_id
    ))

    conn.commit()
    conn.close()


def register_multi_homework_routes(app):

    setup_homework_database()

    @app.route("/homework/<int:student_id>")
    def multi_homework(student_id):

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )

        student = cur.fetchone()

        if not student:
            conn.close()
            return "Student not found", 404

        subject = request.args.get(
            "subject",
            student["subject"] or "Maths"
        )

        questions = questions_for(subject)

        cur.execute("""
            INSERT INTO assignments
            (
                student_id,
                subject,
                total_questions
            )
            VALUES (?, ?, ?)
        """, (
            student_id,
            subject,
            len(questions)
        ))

        assignment_id = cur.lastrowid

        for number, (question, answer) in enumerate(
            questions,
            start=1
        ):
            topic = detect_topic(
                subject,
                question
            )

            cur.execute("""
                INSERT INTO assignment_questions
                (
                    assignment_id,
                    question_number,
                    question,
                    correct_answer,
                    topic
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                assignment_id,
                number,
                question,
                answer,
                topic
            ))

        conn.commit()

        cur.execute("""
            SELECT *
            FROM assignment_questions
            WHERE assignment_id = ?
            ORDER BY question_number
        """, (assignment_id,))

        saved_questions = cur.fetchall()

        conn.close()

        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Homework</title>

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

.question {
    background: #f7f9fc;
    padding: 18px;
    margin: 15px 0;
    border-radius: 12px;
}

input {
    width: 100%;
    box-sizing: border-box;
    padding: 13px;
    border: 1px solid #ccc;
    border-radius: 9px;
    margin-top: 10px;
    font-size: 16px;
}

button {
    width: 100%;
    padding: 15px;
    border: none;
    border-radius: 10px;
    background: #17365d;
    color: white;
    font-size: 16px;
}

.topic {
    color: #666;
    font-size: 13px;
}
</style>
</head>

<body>

<div class="card">

<h1>📚 Homework</h1>

<p>
<strong>Learner:</strong> {{ student["name"] }}
</p>

<p>
<strong>Subject:</strong> {{ subject }}
</p>

<p>
Your tutor has prepared {{ saved_questions|length }} questions.
</p>

<form method="POST"
      action="{{ url_for('submit_multi_homework',
                         student_id=student_id) }}">

<input type="hidden"
       name="assignment_id"
       value="{{ assignment_id }}">

{% for q in saved_questions %}

<div class="question">

<h3>Question {{ q["question_number"] }}</h3>

<p>
<strong>{{ q["question"] }}</strong>
</p>

<div class="topic">
Topic detected: {{ q["topic"] }}
</div>

<input
    type="text"
    name="answer_{{ q["id"] }}"
    placeholder="Type your answer..."
>

</div>

{% endfor %}

<button type="submit">
Submit Homework
</button>

</form>

</div>

</body>
</html>
        """,
        student=student,
        subject=subject,
        saved_questions=saved_questions,
        assignment_id=assignment_id,
        student_id=student_id
        )


    @app.route(
        "/homework/<int:student_id>/submit-multi",
        methods=["POST"]
    )
    def submit_multi_homework(student_id):

        assignment_id = request.form.get("assignment_id")

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM assignments
            WHERE id = ?
            AND student_id = ?
        """, (
            assignment_id,
            student_id
        ))

        assignment = cur.fetchone()

        if not assignment:
            conn.close()
            return "Assignment not found", 404

        cur.execute("""
            SELECT *
            FROM assignment_questions
            WHERE assignment_id = ?
            ORDER BY question_number
        """, (assignment_id,))

        questions = cur.fetchall()

        score = 0
        wrong_topics = []

        for q in questions:

            answer = request.form.get(
                f"answer_{q['id']}",
                ""
            ).strip()

            correct_answer = q["correct_answer"] or ""

            if correct_answer:
                correct = check_answer(
                    answer,
                    correct_answer
                )
            else:
                correct = False

            awarded = 1 if correct else 0

            score += awarded

            cur.execute("""
                UPDATE assignment_questions
                SET student_answer = ?,
                    awarded_marks = ?
                WHERE id = ?
            """, (
                answer,
                awarded,
                q["id"]
            ))

            topic = q["topic"] or "general"

            if correct_answer:
                mastery = record_result(
                    student_id,
                    assignment["subject"],
                    topic,
                    correct
                )

                if not correct:
                    wrong_topics.append({
                        "topic": topic,
                        "mastery": mastery,
                        "question_id": q["id"]
                    })

        total = len(questions)

        percentage = (
            round((score / total) * 100, 1)
            if total else 0
        )

        cur.execute("""
            UPDATE assignments
            SET score = ?,
                percentage = ?,
                completed = 1,
                completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            score,
            percentage,
            assignment_id
        ))

        conn.commit()
        conn.close()

        update_streak(student_id)

        return redirect(
            url_for(
                "multi_homework_result",
                student_id=student_id,
                assignment_id=assignment_id
            )
        )


    @app.route(
        "/homework/<int:student_id>/result/<int:assignment_id>"
    )
    def multi_homework_result(
        student_id,
        assignment_id
    ):

        conn = db()
        cur = conn.cursor()

        cur.execute("""
            SELECT *
            FROM assignments
            WHERE id = ?
            AND student_id = ?
        """, (
            assignment_id,
            student_id
        ))

        assignment = cur.fetchone()

        if not assignment:
            conn.close()
            return "Assignment not found", 404

        cur.execute("""
            SELECT *
            FROM assignment_questions
            WHERE assignment_id = ?
            ORDER BY question_number
        """, (assignment_id,))

        questions = cur.fetchall()

        cur.execute("""
            SELECT name, streak
            FROM students
            WHERE id = ?
        """, (student_id,))

        student = cur.fetchone()

        conn.close()

        wrong = [
            q for q in questions
            if q["awarded_marks"] == 0
            and q["correct_answer"]
        ]

        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Homework Result</title>

<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    margin: 0;
    padding: 20px;
}

.card {
    max-width: 800px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,.08);
}

.score {
    text-align: center;
    padding: 20px;
    background: #eef4ff;
    border-radius: 15px;
}

.question {
    padding: 18px;
    margin-top: 15px;
    border-radius: 12px;
    background: #f8f8f8;
}

.correct {
    border-left: 5px solid #27ae60;
}

.wrong {
    border-left: 5px solid #e67e22;
}

.recovery {
    display: block;
    margin-top: 12px;
    padding: 12px;
    background: #17365d;
    color: white;
    text-decoration: none;
    border-radius: 9px;
    text-align: center;
}

.back {
    display: block;
    margin-top: 20px;
    padding: 14px;
    background: #444;
    color: white;
    text-decoration: none;
    border-radius: 9px;
    text-align: center;
}
</style>
</head>

<body>

<div class="card">

<h1>📊 Homework Result</h1>

<div class="score">

<h2>
{{ assignment["score"] }}
/
{{ assignment["total_questions"] }}
</h2>

<h3>
{{ assignment["percentage"] }}%
</h3>

<p>
🔥 Current streak: {{ student["streak"] }}
</p>

</div>

{% if wrong %}

<h2>🧠 Tutor Recovery</h2>

<p>
Your tutor found {{ wrong|length }} area(s) that need more practice.
That's not failure — it's exactly how your tutor learns what to teach next.
</p>

{% endif %}

{% for q in questions %}

<div class="question
{% if q["awarded_marks"] == 1 %}
correct
{% else %}
wrong
{% endif %}
">

<h3>
Question {{ q["question_number"] }}
</h3>

<p>
<strong>{{ q["question"] }}</strong>
</p>

<p>
<strong>Your answer:</strong>
{{ q["student_answer"] or "No answer" }}
</p>

<p>
<strong>Correct answer:</strong>
{{ q["correct_answer"] }}
</p>

{% if q["awarded_marks"] == 1 %}

<p>✅ Correct!</p>

{% else %}

<p>🧠 Let's improve this topic.</p>

<a class="recovery"
href="{{ url_for(
    'tutor_recovery',
    student_id=student_id,
    subject=assignment['subject'],
    topic=q['topic'],
    question_id=q['id']
) }}">
🧠 Correct This Topic
</a>

{% endif %}

</div>

{% endfor %}

<a class="back"
href="{{ url_for('tutor_page', student_id=student_id) }}">
🧑‍🏫 Go To My Tutor
</a>

</div>

</body>
</html>
        """,
        assignment=assignment,
        questions=questions,
        wrong=wrong,
        student=student,
        student_id=student_id
        )
