from flask import render_template_string, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import re

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
SUBJECTS = [
    "Maths", "English", "Science", "Social Studies",
    "Geography", "History", "Biology", "Chemistry",
    "Physics", "Economics", "Accounting"
]

TOPIC_KEYWORDS = {
    "fractions": ("Maths", "Fractions"),
    "fraction": ("Maths", "Fractions"),
    "decimal": ("Maths", "Decimals"),
    "decimals": ("Maths", "Decimals"),
    "percentage": ("Maths", "Percentages"),
    "percentages": ("Maths", "Percentages"),
    "percent": ("Maths", "Percentages"),
    "algebra": ("Maths", "Algebra"),
    "equation": ("Maths", "Equations"),
    "equations": ("Maths", "Equations"),
    "multiplication": ("Maths", "Multiplication"),
    "multiply": ("Maths", "Multiplication"),
    "division": ("Maths", "Division"),
    "divide": ("Maths", "Division"),
    "geometry": ("Maths", "Geometry"),
    "grammar": ("English", "Grammar"),
    "tense": ("English", "Tenses"),
    "tenses": ("English", "Tenses"),
    "sentence": ("English", "Sentence Construction"),
    "sentences": ("English", "Sentence Construction"),
    "vocabulary": ("English", "Vocabulary"),
    "photosynthesis": ("Biology", "Photosynthesis"),
    "cell": ("Biology", "Cells"),
    "cells": ("Biology", "Cells"),
    "respiration": ("Biology", "Respiration"),
    "human body": ("Biology", "Human Body"),
    "atom": ("Chemistry", "Atoms"),
    "atoms": ("Chemistry", "Atoms"),
    "element": ("Chemistry", "Elements"),
    "elements": ("Chemistry", "Elements"),
    "chemical symbol": ("Chemistry", "Chemical Symbols"),
    "electricity": ("Physics", "Electricity"),
    "motion": ("Physics", "Motion"),
    "energy": ("Physics", "Energy"),
    "forces": ("Physics", "Forces"),
    "force": ("Physics", "Forces"),
}

LESSONS = {
    ("Maths","Fractions"): (
        "Fractions represent parts of a whole.",
        "The top number is the numerator and the bottom number is the denominator.",
        "If a pizza is divided into 4 equal pieces and you take 3 pieces, you have 3/4.",
        "What fraction represents 2 parts out of 5 equal parts?",
        ["2/5"]
    ),
    ("Maths","Decimals"): (
        "Decimals represent parts of a whole using place value.",
        "For example, 0.5 means five tenths and is equal to 1/2.",
        "0.25 = 25/100 = 1/4.",
        "What is 0.5 written as a fraction?",
        ["1/2","1 / 2"]
    ),
    ("Maths","Percentages"): (
        "A percentage means a number out of 100.",
        "25% means 25 out of 100.",
        "50% = 50/100 = 1/2.",
        "What is 25% written as a fraction?",
        ["1/4","1 / 4"]
    ),
    ("Maths","Algebra"): (
        "Algebra uses letters to represent unknown numbers.",
        "The letter x can stand for a number we do not yet know.",
        "If x + 3 = 8, then x = 5.",
        "If x + 4 = 10, what is x?",
        ["6","six"]
    ),
    ("Maths","Equations"): (
        "An equation states that two expressions are equal.",
        "To solve an equation, we work out the unknown value while keeping both sides balanced.",
        "x + 5 = 12, therefore x = 7.",
        "If x + 7 = 15, what is x?",
        ["8","eight"]
    ),
    ("Maths","Multiplication"): (
        "Multiplication is repeated addition.",
        "6 × 4 means six groups of four.",
        "6 × 4 = 24.",
        "What is 6 × 4?",
        ["24","twenty four","twenty-four"]
    ),
    ("Maths","Division"): (
        "Division means sharing or grouping equally.",
        "20 ÷ 5 means sharing 20 into 5 equal groups.",
        "20 ÷ 5 = 4.",
        "What is 20 ÷ 5?",
        ["4","four"]
    ),
    ("Maths","Geometry"): (
        "Geometry is the study of shapes, space and measurement.",
        "A triangle has three sides.",
        "A square has four equal sides and four right angles.",
        "How many sides does a triangle have?",
        ["3","three"]
    ),
    ("English","Grammar"): (
        "Grammar gives us rules for constructing correct sentences.",
        "The subject and verb must agree.",
        "We say 'He goes to school', not 'He go to school'.",
        "Choose the correct sentence: He go to school OR He goes to school.",
        ["he goes to school"]
    ),
    ("English","Tenses"): (
        "Tenses show when an action happens.",
        "Past describes something already done, present describes now, and future describes what will happen.",
        "Past: I walked. Present: I walk. Future: I will walk.",
        "Change 'I walk to school' into the past tense.",
        ["i walked to school"]
    ),
    ("English","Sentence Construction"): (
        "A sentence expresses a complete idea.",
        "A sentence normally begins with a capital letter and ends with suitable punctuation.",
        "The girl walks to school.",
        "Write a sentence using the words girl, school and walks.",
        []
    ),
    ("English","Vocabulary"): (
        "Vocabulary is the collection of words we understand and use.",
        "Synonyms are words with similar meanings.",
        "A synonym for happy is joyful.",
        "Give one synonym for big.",
        ["large","huge","enormous","giant"]
    ),
    ("Biology","Photosynthesis"): (
        "Photosynthesis is how green plants make food.",
        "Plants use light energy, carbon dioxide and water to make food.",
        "Leaves contain chlorophyll which helps absorb light.",
        "Which gas do plants take in during photosynthesis?",
        ["carbon dioxide","co2"]
    ),
    ("Biology","Cells"): (
        "Cells are the basic units of living organisms.",
        "Plants and animals are made from cells.",
        "A microscope can be used to observe cells.",
        "What is the basic unit of life?",
        ["cell","a cell"]
    ),
    ("Biology","Respiration"): (
        "Respiration releases energy from food.",
        "Aerobic respiration uses oxygen.",
        "Cells release energy from glucose during respiration.",
        "Which gas is used in aerobic respiration?",
        ["oxygen","o2"]
    ),
    ("Biology","Human Body"): (
        "The human body contains organs with specialised functions.",
        "The heart pumps blood and the lungs help us breathe.",
        "The digestive system breaks down food.",
        "Which organ pumps blood around the body?",
        ["heart"]
    ),
    ("Chemistry","Atoms"): (
        "Atoms are the basic units of elements.",
        "Atoms contain smaller particles including protons, neutrons and electrons.",
        "Iron is made from iron atoms.",
        "What is the basic unit of an element?",
        ["atom","an atom"]
    ),
    ("Chemistry","Elements"): (
        "An element is a pure substance made from one type of atom.",
        "Each element has its own chemical symbol.",
        "Gold is an element.",
        "Is oxygen an element?",
        ["yes"]
    ),
    ("Chemistry","Chemical Symbols"): (
        "Chemical symbols are short ways of representing elements.",
        "H represents hydrogen and O represents oxygen.",
        "Na represents sodium.",
        "What is the chemical symbol for oxygen?",
        ["o","O"]
    ),
    ("Physics","Electricity"): (
        "Electric current flows through a complete circuit.",
        "A simple circuit can contain a cell, wires and a bulb.",
        "An open circuit stops current from flowing.",
        "What must a circuit have for current to flow?",
        ["complete circuit","a complete circuit","closed circuit","a closed circuit"]
    ),
    ("Physics","Motion"): (
        "Motion occurs when an object's position changes.",
        "We describe motion relative to a reference point.",
        "A moving car changes position relative to the road.",
        "What does it mean when an object is in motion?",
        ["its position changes","position changes"]
    ),
    ("Physics","Energy"): (
        "Energy is the ability to do work or cause change.",
        "Energy can exist as heat, light, electrical, chemical, kinetic and potential energy.",
        "A battery stores chemical energy.",
        "Name one form of energy.",
        ["heat","light","electrical","chemical","sound","kinetic","potential"]
    )
}

TESTS = {
    "Maths": [
        ("What is 6 × 4?", ["24"]),
        ("What is 20 ÷ 5?", ["4"]),
        ("What fraction represents 2 out of 5?", ["2/5"]),
        ("If x + 4 = 10, what is x?", ["6"]),
        ("How many sides does a triangle have?", ["3"])
    ],
    "English": [
        ("Choose the correct form: He ___ to school.", ["goes"]),
        ("Give a synonym for big.", ["large","huge","enormous"]),
        ("Change 'I walk' to past tense.", ["i walked"]),
        ("What is the noun in 'The teacher writes'?", ["teacher"]),
        ("What should a sentence begin with?", ["capital letter","a capital letter"])
    ],
    "Science": [
        ("Which organ pumps blood?", ["heart"]),
        ("Name one state of matter.", ["solid","liquid","gas"]),
        ("Is pushing a box a push or pull?", ["push"]),
        ("What gas do plants take in?", ["carbon dioxide","co2"]),
        ("Name one source of energy.", ["sun","sunlight","solar"])
    ],
    "Biology": [
        ("What is the basic unit of life?", ["cell"]),
        ("Which gas is used in photosynthesis?", ["carbon dioxide","co2"]),
        ("Which gas is used in aerobic respiration?", ["oxygen","o2"]),
        ("Which organ pumps blood?", ["heart"]),
        ("Name one part of a plant cell.", ["nucleus","cell wall","chloroplast","vacuole","cytoplasm"])
    ],
    "Chemistry": [
        ("What is the basic unit of an element?", ["atom"]),
        ("What is the symbol for oxygen?", ["o"]),
        ("Is gold an element?", ["yes"]),
        ("Name one state of matter.", ["solid","liquid","gas"]),
        ("What particle has a negative charge?", ["electron"])
    ],
    "Physics": [
        ("Name one form of energy.", ["heat","light","sound","electrical","chemical"]),
        ("What is a push or pull called?", ["force"]),
        ("What must a circuit have for current to flow?", ["complete circuit","closed circuit"]),
        ("What is motion?", ["change in position","a change in position"]),
        ("Name one source of light.", ["sun","bulb","lamp"])
    ]
}

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def setup():
    c = conn()

    c.execute("""
    CREATE TABLE IF NOT EXISTS tutor_learning (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        topic TEXT,
        attempts INTEGER DEFAULT 0,
        correct INTEGER DEFAULT 0,
        mastery INTEGER DEFAULT 0,
        last_activity TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS academic_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        activity_type TEXT,
        subject TEXT,
        topic TEXT,
        question TEXT,
        answer TEXT,
        correct INTEGER,
        marks INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS academic_tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        percentage INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS academic_exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER DEFAULT 0,
        total INTEGER DEFAULT 0,
        percentage INTEGER DEFAULT 0,
        completed_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
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
    """)

    c.commit()
    c.close()

def clean(x):
    return " ".join((x or "").lower().strip().replace(".", "").split())

def student(sid):
    c = conn()
    r = c.execute("SELECT * FROM students WHERE id=?", (sid,)).fetchone()
    c.close()
    return r

def detect_topic(message, current_subject=""):
    text = clean(message)

    # Long phrases first
    for phrase, result in sorted(TOPIC_KEYWORDS.items(), key=lambda x: -len(x[0])):
        if phrase in text:
            return result

    subject_aliases = {
        "math": "Maths",
        "maths": "Maths",
        "english": "English",
        "science": "Science",
        "biology": "Biology",
        "chemistry": "Chemistry",
        "physics": "Physics",
        "geography": "Geography",
        "history": "History",
        "economics": "Economics",
        "accounting": "Accounting"
    }

    for alias, subject in subject_aliases.items():
        if alias in text:
            return subject, ""

    return current_subject, ""

def get_learning(student_id, subject, topic):
    c = conn()
    r = c.execute("""
        SELECT * FROM tutor_learning
        WHERE student_id=? AND subject=? AND topic=?
    """, (student_id, subject, topic)).fetchone()
    c.close()
    return r

def record_learning(student_id, subject, topic, correct):
    if not subject or not topic:
        return

    c = conn()
    r = c.execute("""
        SELECT * FROM tutor_learning
        WHERE student_id=? AND subject=? AND topic=?
    """, (student_id, subject, topic)).fetchone()

    if r:
        attempts = r["attempts"] + 1
        right = r["correct"] + (1 if correct else 0)
        mastery = int((right / attempts) * 100)
        c.execute("""
        UPDATE tutor_learning
        SET attempts=?, correct=?, mastery=?, last_activity=?
        WHERE id=?
        """, (
            attempts, right, mastery,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            r["id"]
        ))
    else:
        c.execute("""
        INSERT INTO tutor_learning
        (student_id,subject,topic,attempts,correct,mastery,last_activity)
        VALUES (?,?,?,?,?,?,?)
        """, (
            student_id, subject, topic, 1,
            1 if correct else 0,
            100 if correct else 0,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    c.commit()
    c.close()

def answer_is_correct(subject, topic, answer):
    key = (subject, topic)
    lesson = LESSONS.get(key)

    if not lesson:
        return len(clean(answer).split()) >= 3

    expected = lesson[4]

    if not expected:
        return len(clean(answer).split()) >= 3

    return clean(answer) in [clean(x) for x in expected]

def get_student_selected_subject(sid, requested_subject=None):
    """
    Resolve the student's subject without silently forcing Maths.

    Priority:
      1. Explicit subject requested by the student/page
      2. current_subject stored on the student profile
      3. primary subject stored on the student profile
      4. first active subject in student_subjects
      5. None

    Never silently changes another subject to Maths.
    """
    requested = (requested_subject or "").strip()

    if requested:
        return requested

    s = student(sid)

    if s:
        try:
            current = (s["current_subject"] or "").strip()
        except (KeyError, IndexError):
            current = ""

        if current:
            return current

        try:
            primary = (s["subject"] or "").strip()
        except (KeyError, IndexError):
            primary = ""

        if primary:
            return primary

    try:
        c = conn()
        row = c.execute(
            """
            SELECT subject
            FROM student_subjects
            WHERE student_id=? AND active=1
            ORDER BY id
            LIMIT 1
            """,
            (sid,)
        ).fetchone()
        c.close()

        if row and row["subject"]:
            return row["subject"].strip()

    except Exception:
        pass

    return None


def tutor_response(sid, message):
    s = student(sid)
    if not s:
        return ("General", "", "Student profile not found.")

    current = get_student_selected_subject(sid)

    if not current:
        return (
            "General",
            "",
            "I don't have your current subject yet. "
            "Please choose the subject you want to study."
        )
    subject, topic = detect_topic(message, current)

    # If learner mentions a subject without topic
    if subject and not topic:
        return (
            subject,
            "",
            f"I can help you with {subject}. Tell me the topic you want to learn, "
            f"for example fractions, algebra, percentages, grammar or another topic."
        )

    if not subject:
        subject = current

    if not topic:
        return (
            subject,
            "",
            "I understand. Tell me the exact topic or question you are struggling with. "
            "For example: 'What are fractions?', 'I don't understand algebra', "
            "or 'Explain photosynthesis'."
        )

    lesson = LESSONS.get((subject, topic))

    if not lesson:
        return (
            subject,
            topic,
            f"Great question. Let's learn {topic}. "
            f"I'll guide you step by step and then give you a practice question."
        )

    return (
        subject,
        topic,
        f"""🎯 Lesson Goal
{lesson[0]}

📖 Tutor Explanation
{lesson[1]}

💡 Example
{lesson[2]}

✏️ Your Turn
{lesson[3]}

Write your answer below and I will mark it."""
    )

def render_page(title, body):
    return f"""
    <!doctype html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{title}</title>
    <style>
    body{{font-family:Arial;background:#f4f7fb;margin:0;padding:15px}}
    .box{{max-width:760px;margin:auto}}
    .header{{background:#111;color:white;padding:22px;border-radius:20px}}
    .card{{background:white;padding:20px;border-radius:18px;margin:14px 0;box-shadow:0 2px 10px #ddd}}
    textarea{{width:100%;box-sizing:border-box;min-height:110px;padding:14px;border-radius:12px;border:1px solid #bbb;font-size:17px}}
    button,.btn{{display:block;width:100%;box-sizing:border-box;padding:14px;margin-top:10px;border:0;border-radius:12px;background:#111;color:white;text-align:center;text-decoration:none;font-size:16px}}
    .green{{background:#e8f7ed;padding:15px;border-radius:12px}}
    .orange{{background:#fff4df;padding:15px;border-radius:12px}}
    .blue{{background:#e8f1ff;padding:15px;border-radius:12px}}
    </style>
    </head>
    <body><div class="box">{body}</div></body>
    </html>
    """

def register_student_academy(app):

    setup()

    # -------- SMART TUTOR --------

    @app.route("/student/<int:sid>/smart-tutor", methods=["GET"])
    def smart_tutor(sid):
        s = student(sid)
        if not s:
            return "Student not found", 404

        return render_page(
            "Smart Tutor",
            f"""
            <div class="header">
            <h1>🧑‍🏫 Smart Tutor</h1>
            <p>Hello {s['name']} 👋</p>
            <p>Ask me what you want to learn.</p>
            </div>

            <div class="card">
            <form method="post" action="/student/{sid}/smart-tutor">
            <textarea name="message"
            placeholder="Example: What are fractions?"
            required></textarea>
            <button>ASK TUTOR</button>
            </form>
            </div>

            <a class="btn" href="/student/{sid}/learning">📚 Learning Centre</a>
            <a class="btn" href="/student/{sid}/home">🏠 Student Home</a>
            """
        )

    @app.route("/student/<int:sid>/smart-tutor", methods=["POST"])
    def smart_tutor_post(sid):
        s = student(sid)
        message = request.form.get("message", "").strip()

        subject, topic, response = tutor_response(sid, message)

        return render_page(
            "Tutor",
            f"""
            <div class="header">
            <h1>🧑‍🏫 {subject} Tutor</h1>
            <p>❓ You asked:</p>
            <b>{message}</b>
            </div>

            <div class="card blue">
            <h3>🧑‍🏫 Tutor:</h3>
            <p style="white-space:pre-line">{response}</p>
            </div>

            {f'''
            <div class="card">
            <form method="post" action="/student/{sid}/smart-answer">
            <input type="hidden" name="subject" value="{subject}">
            <input type="hidden" name="topic" value="{topic}">
            <textarea name="answer" placeholder="Write your answer..." required></textarea>
            <button>SUBMIT MY ANSWER</button>
            </form>
            </div>
            ''' if topic else ""}

            <a class="btn" href="/student/{sid}/smart-tutor">💬 Ask Another Question</a>
            <a class="btn" href="/student/{sid}/learning">← Back to Learning Centre</a>
            """
        )

    @app.route("/student/<int:sid>/smart-answer", methods=["POST"])
    def smart_answer(sid):
        subject = request.form.get("subject", "")
        topic = request.form.get("topic", "")
        answer = request.form.get("answer", "")

        correct = answer_is_correct(subject, topic, answer)
        record_learning(sid, subject, topic, correct)

        c = conn()
        c.execute("""
        INSERT INTO academic_attempts
        (student_id,activity_type,subject,topic,question,answer,correct)
        VALUES (?,?,?,?,?,?,?)
        """, (
            sid, "TUTOR", subject, topic,
            LESSONS.get((subject,topic), ("","","Try again","",""))[3]
            if (subject,topic) in LESSONS else "",
            answer, 1 if correct else 0
        ))
        c.commit()
        c.close()

        if correct:
            result = """
            <div class="green">
            <h2>🎉 Correct!</h2>
            <p>Excellent work! You understood the key idea.</p>
            </div>
            """
        else:
            lesson = LESSONS.get((subject,topic))
            correction = ""
            if lesson:
                correction = f"""
                <p><b>Let's correct it:</b></p>
                <p>{lesson[1]}</p>
                <p><b>Example:</b> {lesson[2]}</p>
                <p><b>Correct answer:</b> {lesson[4][0] if lesson[4] else 'Review the explanation and try again.'}</p>
                """
            result = f"""
            <div class="orange">
            <h2>💪 Good Try!</h2>
            <p>You haven't mastered this one yet.</p>
            {correction}
            </div>
            """

        r = get_learning(sid, subject, topic)
        mastery = r["mastery"] if r else 0

        return render_page(
            "Tutor Result",
            f"""
            <div class="header">
            <h1>📊 {subject} — {topic}</h1>
            </div>
            <div class="card">
            {result}
            <h3>🧠 Topic Mastery: {mastery}%</h3>
            </div>
            <a class="btn" href="/student/{sid}/smart-tutor">🔄 Continue Learning</a>
            <a class="btn" href="/student/{sid}/learning">📚 Learning Centre</a>
            """
        )

    # -------- TESTS --------

    @app.route("/student/<int:sid>/tests")
    def student_tests(sid):
        return render_page(
            "Tests",
            f"""
            <div class="header">
            <h1>📝 Tests</h1>
            <p>Choose a subject for a 5-question test.</p>
            </div>

            <div class="card">
            {''.join(
                f'<a class="btn" href="/student/{sid}/test?subject={sub}">{sub} Test</a>'
                for sub in TESTS.keys()
            )}
            </div>

            <a class="btn" href="/student/{sid}/learning">← Learning Centre</a>
            """
        )

    @app.route("/student/<int:sid>/test")
    def start_test(sid):
        subject = get_student_selected_subject(
            sid,
            request.args.get("subject")
        )

        if not subject:
            return render_page(
                "Choose Subject",
                """
                <div class="header">
                <h1>📚 Choose a Subject</h1>
                <p>Please select the subject you want to test.</p>
                </div>
                """
            )

        questions = TESTS.get(subject)

        if not questions:
            return render_page(
                f"{subject} Test",
                f"""
                <div class="header">
                <h1>📝 {subject} Test</h1>
                <p>
                There is currently no test bank loaded for {subject}.
                Your learning curriculum is still available.
                </p>
                </div>

                <a class="btn"
                   href="/student/{sid}/learning">
                   ← Learning Centre
                </a>
                """
            )

        return render_page(
            f"{subject} Test",
            f"""
            <div class="header">
            <h1>📝 {subject} Test</h1>
            <p>Answer all questions.</p>
            </div>

            <form method="post" action="/student/{sid}/submit-test">
            <input type="hidden" name="subject" value="{subject}">

            {''.join(
                f'''
                <div class="card">
                <h3>{i+1}. {q}</h3>
                <input name="q{i}" required
                style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:1px solid #bbb">
                </div>
                '''
                for i,(q,a) in enumerate(questions)
            )}

            <button class="btn">SUBMIT TEST</button>
            </form>
            """
        )

    @app.route("/student/<int:sid>/submit-test", methods=["POST"])
    def submit_test(sid):
        subject = get_student_selected_subject(
            sid,
            request.form.get("subject")
        )

        if not subject:
            return render_page(
                "Test Error",
                """
                <div class="header">
                <h1>⚠️ Subject Required</h1>
                <p>Please choose a subject before submitting the test.</p>
                </div>
                """
            )

        questions = TESTS.get(subject)

        if not questions:
            return render_page(
                f"{subject} Test",
                f"""
                <div class="header">
                <h1>📝 {subject} Test</h1>
                <p>No test bank is currently loaded for {subject}.</p>
                </div>
                """
            )

        score = 0

        for i,(question,answers) in enumerate(questions):
            answer = request.form.get(f"q{i}", "")
            correct = clean(answer) in [clean(x) for x in answers]

            if correct:
                score += 1

            c = conn()
            c.execute("""
            INSERT INTO academic_attempts
            (student_id,activity_type,subject,topic,question,answer,correct)
            VALUES (?,?,?,?,?,?,?)
            """, (
                sid, "TEST", subject, "",
                question, answer, 1 if correct else 0
            ))
            c.commit()
            c.close()

        total = len(questions)
        percentage = int((score/total)*100)

        c = conn()
        c.execute("""
        INSERT INTO academic_tests
        (student_id,subject,score,total,percentage)
        VALUES (?,?,?,?,?)
        """, (sid,subject,score,total,percentage))
        c.commit()
        c.close()

        status = "🎉 PASS" if percentage >= 50 else "💪 KEEP PRACTISING"

        return render_page(
            "Test Result",
            f"""
            <div class="header">
            <h1>📊 Test Result</h1>
            </div>

            <div class="card">
            <h2>{subject}</h2>
            <h1>{score} / {total}</h1>
            <h2>{percentage}%</h2>
            <h2>{status}</h2>
            </div>

            <a class="btn" href="/student/{sid}/tests">📝 Another Test</a>
            <a class="btn" href="/student/{sid}/report">📊 My Weekly Report</a>
            """
        )

    # -------- EXAMS --------

    @app.route("/student/<int:sid>/exams")
    def exams(sid):
        return render_page(
            "Examinations",
            f"""
            <div class="header">
            <h1>🎓 Examinations</h1>
            <p>Prepare yourself with examination-style practice.</p>
            </div>

            <div class="card">
            <h2>Mock Examination</h2>
            <p>This examination combines questions from your selected subject.</p>

            {''.join(
                f'<a class="btn" href="/student/{sid}/exam?subject={sub}">🎓 {sub} Mock Exam</a>'
                for sub in TESTS.keys()
            )}
            </div>

            <a class="btn" href="/student/{sid}/learning">← Learning Centre</a>
            """
        )

    @app.route("/student/<int:sid>/exam")
    def exam(sid):
        subject = get_student_selected_subject(
            sid,
            request.args.get("subject")
        )

        if not subject:
            return render_page(
                "Choose Subject",
                """
                <div class="header">
                <h1>📚 Choose a Subject</h1>
                <p>Please select the subject you want to examine.</p>
                </div>
                """
            )

        questions = TESTS.get(subject)

        if not questions:
            return render_page(
                f"{subject} Examination",
                f"""
                <div class="header">
                <h1>🎓 {subject} Mock Examination</h1>
                <p>
                No examination question bank is currently loaded
                for {subject}.
                </p>
                </div>

                <a class="btn"
                   href="/student/{sid}/learning">
                   ← Learning Centre
                </a>
                """
            )

        return render_page(
            "Mock Examination",
            f"""
            <div class="header">
            <h1>🎓 {subject} Mock Examination</h1>
            <p>Work carefully. Treat this like a real examination.</p>
            </div>

            <form method="post" action="/student/{sid}/submit-exam">
            <input type="hidden" name="subject" value="{subject}">

            {''.join(
                f'''
                <div class="card">
                <h3>{i+1}. {q}</h3>
                <input name="q{i}" required
                style="width:100%;box-sizing:border-box;padding:13px;border-radius:10px;border:1px solid #bbb">
                </div>
                '''
                for i,(q,a) in enumerate(questions)
            )}

            <button class="btn">SUBMIT EXAMINATION</button>
            </form>
            """
        )

    @app.route("/student/<int:sid>/submit-exam", methods=["POST"])
    def submit_exam(sid):
        subject = get_student_selected_subject(
            sid,
            request.form.get("subject")
        )

        if not subject:
            return render_page(
                "Examination Error",
                """
                <div class="header">
                <h1>⚠️ Subject Required</h1>
                <p>Please choose a subject before submitting.</p>
                </div>
                """
            )

        questions = TESTS.get(subject)

        if not questions:
            return render_page(
                f"{subject} Examination",
                f"""
                <div class="header">
                <h1>🎓 {subject} Mock Examination</h1>
                <p>No examination question bank is currently loaded
                for {subject}.</p>
                </div>
                """
            )

        score = 0

        for i,(question,answers) in enumerate(questions):
            answer = request.form.get(f"q{i}", "")
            correct = clean(answer) in [clean(x) for x in answers]
            if correct:
                score += 1

            c = conn()
            c.execute("""
            INSERT INTO academic_attempts
            (student_id,activity_type,subject,topic,question,answer,correct)
            VALUES (?,?,?,?,?,?,?)
            """, (
                sid,"EXAM",subject,"",
                question,answer,1 if correct else 0
            ))
            c.commit()
            c.close()

        total = len(questions)
        percentage = int((score/total)*100)

        c = conn()
        c.execute("""
        INSERT INTO academic_exams
        (student_id,subject,score,total,percentage)
        VALUES (?,?,?,?,?)
        """, (sid,subject,score,total,percentage))
        c.commit()
        c.close()

        return render_page(
            "Exam Result",
            f"""
            <div class="header">
            <h1>🎓 Examination Result</h1>
            </div>

            <div class="card">
            <h2>{subject}</h2>
            <h1>{score} / {total}</h1>
            <h2>{percentage}%</h2>
            <p>{'Excellent examination performance.' if percentage >= 75 else 'Keep practising and review your weak topics.'}</p>
            </div>

            <a class="btn" href="/student/{sid}/exams">🎓 Examinations</a>
            <a class="btn" href="/student/{sid}/report">📊 Weekly Report</a>
            """
        )

    # -------- WEEKLY REPORT --------

    @app.route("/student/<int:sid>/report")
    def weekly_report(sid):
        c = conn()

        attempts = c.execute("""
        SELECT COUNT(*) n,
               SUM(correct) correct
        FROM academic_attempts
        WHERE student_id=?
        AND datetime(created_at) >= datetime('now','-7 days')
        """, (sid,)).fetchone()

        tests = c.execute("""
        SELECT COUNT(*) n, AVG(percentage) avg
        FROM academic_tests
        WHERE student_id=?
        AND datetime(completed_at) >= datetime('now','-7 days')
        """, (sid,)).fetchone()

        exams = c.execute("""
        SELECT COUNT(*) n, AVG(percentage) avg
        FROM academic_exams
        WHERE student_id=?
        AND datetime(completed_at) >= datetime('now','-7 days')
        """, (sid,)).fetchone()

        weak = c.execute("""
        SELECT subject, topic, mastery
        FROM tutor_learning
        WHERE student_id=?
        AND attempts > 0
        ORDER BY mastery ASC
        LIMIT 5
        """, (sid,)).fetchall()

        strong = c.execute("""
        SELECT subject, topic, mastery
        FROM tutor_learning
        WHERE student_id=?
        AND attempts > 0
        ORDER BY mastery DESC
        LIMIT 5
        """, (sid,)).fetchall()

        c.close()

        attempt_count = attempts["n"] or 0
        correct_count = attempts["correct"] or 0
        test_count = tests["n"] or 0
        exam_count = exams["n"] or 0

        body = f"""
        <div class="header">
        <h1>📊 Weekly Learning Report</h1>
        <p>Last 7 days</p>
        </div>

        <div class="card">
        <h2>📚 Learning Activity</h2>
        <p>Questions attempted: <b>{attempt_count}</b></p>
        <p>Correct answers: <b>{correct_count}</b></p>
        <p>Tests completed: <b>{test_count}</b></p>
        <p>Exams completed: <b>{exam_count}</b></p>
        </div>

        <div class="card">
        <h2>💪 Topics to Improve</h2>
        {''.join(f'<p>🔴 {r["subject"]} — {r["topic"]}: {r["mastery"]}%</p>' for r in weak)
        or '<p>No weak topics recorded yet. Keep learning!</p>'}
        </div>

        <div class="card">
        <h2>🏆 Strongest Topics</h2>
        {''.join(f'<p>🟢 {r["subject"]} — {r["topic"]}: {r["mastery"]}%</p>' for r in strong)
        or '<p>Complete some lessons to build your progress report.</p>'}
        </div>

        <div class="card blue">
        <h2>🎯 Tutor Recommendation</h2>
        <p>Focus your next study sessions on the topics marked in red.</p>
        <p>Practise weak topics until your mastery reaches at least 80%.</p>
        </div>

        <a class="btn" href="/student/{sid}/smart-tutor">🧑‍🏫 Ask Your Tutor</a>
        <a class="btn" href="/student/{sid}/tests">📝 Tests</a>
        <a class="btn" href="/student/{sid}/exams">🎓 Exams</a>
        <a class="btn" href="/student/{sid}/learning">📚 Learning Centre</a>
        """

        return render_page("Weekly Report", body)

    # -------- PAID LESSON REQUEST --------

    @app.route("/student/<int:sid>/request-paid")
    def request_paid(sid):
        subject = get_student_selected_subject(
            sid,
            request.args.get("subject")
        )

        if not subject:
            return render_page(
                "Choose Subject",
                """
                <div class="header">
                <h1>📚 Choose a Subject</h1>
                <p>
                Please choose the subject you want for your
                paid lesson.
                </p>
                </div>
                """
            )

        c = conn()
        existing = c.execute("""
        SELECT * FROM payment_requests
        WHERE student_id=? AND subject=? AND status IN ('PENDING','VERIFIED')
        ORDER BY id DESC LIMIT 1
        """, (sid,subject)).fetchone()
        c.close()

        if existing:
            status = existing["status"]

            if status == "VERIFIED":
                return render_page(
                    "Payment Verified",
                    f"""
                    <div class="header">
                    <h1>✅ Payment Verified</h1>
                    <p>Your {subject} 1-hour lesson is unlocked.</p>
                    </div>

                    <div class="card green">
                    <h2>💵 $1 — 1-HOUR SESSION</h2>
                    <p>The Agent has approved your payment.</p>
                    <a class="btn" href="/student/{sid}/start-paid?id={existing['id']}">
                    ▶ START 1-HOUR LESSON
                    </a>
                    </div>
                    """
                )

            return render_page(
                "Payment Pending",
                f"""
                <div class="header">
                <h1>⏳ Payment Verification</h1>
                </div>
                <div class="card orange">
                <p>Your request for a {subject} one-hour lesson is waiting for payment verification.</p>
                <p><b>Amount: $1.00</b></p>
                <p>Once the Agent approves the payment, the lesson will become available.</p>
                </div>
                <a class="btn" href="/student/{sid}/home">🏠 Student Home</a>
                """
            )

        c = conn()
        c.execute("""
        INSERT INTO payment_requests(student_id,subject,amount,status)
        VALUES (?,?,1.00,'PENDING')
        """, (sid,subject))
        c.commit()
        c.close()

        return render_page(
            "Payment Request",
            f"""
            <div class="header">
            <h1>💵 1-Hour Lesson</h1>
            </div>

            <div class="card">
            <h2>{subject}</h2>
            <h1>$1.00</h1>
            <p>1-hour tutor session.</p>
            <p>Make payment using your normal payment method and notify the Agent.</p>
            <p><b>The Agent must approve your payment before the lesson unlocks.</b></p>
            </div>

            <a class="btn" href="/student/{sid}/home">🏠 Student Home</a>
            """
        )

    @app.route("/student/<int:sid>/start-paid")
    def start_paid(sid):
        rid = request.args.get("id")

        if not rid:
            return "Verified payment ID is required.", 400

        c = conn()
        r = c.execute("""
        SELECT id, student_id, status
        FROM payment_requests
        WHERE id=? AND student_id=? AND status='VERIFIED'
        """, (rid, sid)).fetchone()
        c.close()

        if not r:
            return "Payment has not been approved by the Agent.", 403

        # Send the student into the MASTER paid-session route.
        # This is the single 60-minute timer used by the whole
        # paid learning system.
        return redirect(
            f"/student/{sid}/start-verified-paid"
        )

    @app.route("/student/<int:sid>/payment-status")
    def payment_status(sid):
        c = conn()
        rows = c.execute("""
        SELECT * FROM payment_requests
        WHERE student_id=?
        ORDER BY id DESC
        """, (sid,)).fetchall()
        c.close()

        return render_page(
            "Payment Status",
            f"""
            <div class="header">
            <h1>💳 Payment Status</h1>
            </div>

            <div class="card">
            {''.join(
                f'<p><b>{r["subject"]}</b> — {r["status"]}</p>'
                for r in rows
            ) or '<p>No payment requests yet.</p>'}
            </div>

            <a class="btn" href="/student/{sid}/home">🏠 Home</a>
            """
        )

    print("STUDENT ACADEMY: READY")


# ==========================================================
# FOUNDER PAYMENT CONTROL
# ==========================================================

def register_founder_academy(app):

    setup()

    @app.route("/founder/payments")
    def founder_payments():
        c = conn()
        rows = c.execute("""
        SELECT p.*, s.name
        FROM payment_requests p
        LEFT JOIN students s ON s.id=p.student_id
        ORDER BY p.id DESC
        """).fetchall()
        c.close()

        items = ""

        for r in rows:
            action = ""

            if r["status"] == "PENDING":
                action = f"""
                <form method="post" action="/founder/payments/{r['id']}/verify">
                <button>🔓 VERIFY & UNLOCK 1-HOUR LESSON</button>
                </form>
                """

            items += f"""
            <div class="card">
            <h3>👤 {r['name']}</h3>
            <p>Student ID: {r['student_id']}</p>
            <p>Subject: <b>{r['subject']}</b></p>
            <p>Amount: <b>${r['amount']:.2f}</b></p>
            <p>Status: <b>{r['status']}</b></p>
            <p>Requested: {r['requested_at']}</p>
            {action}
            </div>
            """

        return render_page(
            "Agent Payment Control",
            f"""
            <div class="header">
            <h1>🔐 Agent Payment Control</h1>
            <p>Verify payments before unlocking paid lessons.</p>
            </div>
            {items or '<div class="card">No payment requests.</div>'}
            <a class="btn" href="http://127.0.0.1:5000/">← Agent Dashboard</a>
            """
        )

    @app.route("/founder/payments/<int:rid>/verify", methods=["POST"])
    def founder_verify_payment(rid):
        c = conn()

        c.execute("""
        UPDATE payment_requests
        SET status='VERIFIED',
            verified_at=?
        WHERE id=?
        """, (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            rid
        ))

        c.commit()
        c.close()

        return redirect("/founder/payments")

    print("FOUNDER PAYMENT CONTROL: READY")
