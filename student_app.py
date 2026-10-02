from flask import request, redirect, url_for, render_template_string
import sqlite3
import os
import inspect
from datetime import datetime, timedelta

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
SUBJECTS = [
    "Maths", "English", "Science", "Social Studies", "Geography",
    "History", "Biology", "Chemistry", "Physics", "Economics", "Accounting"
]

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def setup():
    conn = db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            active INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            session_type TEXT,
            started_at TEXT,
            expires_at TEXT,
            completed INTEGER DEFAULT 0
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS student_homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            question TEXT,
            correct_answer TEXT,
            student_answer TEXT,
            marks INTEGER DEFAULT 0,
            answered INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add current_subject if it does not exist
    try:
        cur.execute("ALTER TABLE students ADD COLUMN current_subject TEXT")
    except:
        pass

    conn.commit()
    conn.close()

setup()

def student(sid):
    conn = db()
    row = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    conn.close()
    return row

def selected_subjects(sid):
    conn = db()
    rows = conn.execute(
        "SELECT subject FROM student_subjects WHERE student_id=? AND active=1 ORDER BY subject",
        (sid,)
    ).fetchall()
    conn.close()
    return [r["subject"] for r in rows]

def current_subject(sid):
    conn = db()
    row = conn.execute(
        "SELECT current_subject FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    conn.close()

    if row and row["current_subject"]:
        return row["current_subject"]

    subjects = selected_subjects(sid)
    return subjects[0] if subjects else None

def page(title, body, sid=None):
    nav = ""

    if sid:
        nav = f"""
        <div class="nav">
            <a href="/student/{sid}/home">🏠 Home</a>
            <a href="/student/{sid}/subject">📚 Learning Centre</a>
            <a href="/student/{sid}/profile">👤 Profile</a>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{
    margin:0;
    font-family:Arial,sans-serif;
    background:#f4f7fb;
    color:#172033;
}}
.container {{
    max-width:850px;
    margin:auto;
    padding:18px;
}}
.card {{
    background:white;
    border-radius:18px;
    padding:22px;
    margin:15px 0;
    box-shadow:0 5px 18px rgba(0,0,0,.08);
}}
h1,h2,h3 {{ margin-top:0; }}
.hero {{
    background:linear-gradient(135deg,#172554,#2563eb);
    color:white;
    border-radius:20px;
    padding:25px;
}}
.btn {{
    display:block;
    text-decoration:none;
    padding:15px;
    border-radius:12px;
    margin:10px 0;
    background:#2563eb;
    color:white;
    text-align:center;
    font-weight:bold;
    border:0;
    width:100%;
    box-sizing:border-box;
    font-size:16px;
}}
.green {{ background:#15803d; }}
.orange {{ background:#ea580c; }}
.purple {{ background:#7c3aed; }}
.gray {{ background:#475569; }}
.red {{ background:#dc2626; }}
.subject {{
    border:2px solid #e2e8f0;
    border-radius:15px;
    padding:16px;
    margin:10px 0;
    background:white;
}}
.selected {{
    border-color:#2563eb;
    background:#eff6ff;
}}
textarea,input {{
    width:100%;
    box-sizing:border-box;
    padding:14px;
    border:1px solid #cbd5e1;
    border-radius:10px;
    margin:8px 0;
    font-size:16px;
}}
.question {{
    background:#f8fafc;
    border-radius:14px;
    padding:18px;
    margin:15px 0;
}}
.nav {{
    display:flex;
    gap:8px;
    flex-wrap:wrap;
    margin-bottom:15px;
}}
.nav a {{
    background:white;
    padding:9px 12px;
    border-radius:10px;
    text-decoration:none;
    color:#1d4ed8;
    font-weight:bold;
}}
.success {{
    background:#dcfce7;
    padding:15px;
    border-radius:12px;
}}
.warning {{
    background:#fef3c7;
    padding:15px;
    border-radius:12px;
}}
</style>
</head>
<body>
<div class="container">
{nav}
{body}
</div>
</body>
</html>
"""

def homework_bank(subject):
    banks = {
        "Maths": [
            ("What is 25 + 37?", "62"),
            ("What is 8 × 7?", "56"),
            ("What is 100 ÷ 4?", "25"),
            ("What is 15% of 200?", "30"),
            ("Solve: 2x = 10. What is x?", "5")
        ],
        "English": [
            ("Complete: The boy _____ to school every day.", "goes"),
            ("Give the plural of 'child'.", "children"),
            ("What is the opposite of 'difficult'?", "easy"),
            ("Identify the verb: 'Sarah writes neatly.'", "writes"),
            ("Give the past tense of 'go'.", "went")
        ],
        "Science": [
            ("What organ pumps blood around the body?", "heart"),
            ("What gas do humans breathe in?", "oxygen"),
            ("What is H2O commonly called?", "water"),
            ("What force pulls objects towards Earth?", "gravity"),
            ("What do plants use to make food?", "sunlight")
        ],
        "Biology": [
            ("What is the basic unit of life?", "cell"),
            ("Which organ pumps blood?", "heart"),
            ("What process do plants use to make food?", "photosynthesis"),
            ("Which gas is used in photosynthesis?", "carbon dioxide"),
            ("Where is genetic material found in a cell?", "nucleus")
        ],
        "Chemistry": [
            ("What is the chemical symbol for oxygen?", "O"),
            ("What is the chemical symbol for hydrogen?", "H"),
            ("What is the pH of a neutral substance?", "7"),
            ("What is the smallest unit of an element?", "atom"),
            ("What is H2O?", "water")
        ],
        "Physics": [
            ("What force pulls objects towards Earth?", "gravity"),
            ("What is the SI unit of force?", "newton"),
            ("What is the SI unit of energy?", "joule"),
            ("What instrument measures temperature?", "thermometer"),
            ("What is speed equal to distance divided by?", "time")
        ],
        "Geography": [
            ("What is the largest continent?", "asia"),
            ("What is the capital of Zimbabwe?", "harare"),
            ("What imaginary line divides Earth into Northern and Southern Hemispheres?", "equator"),
            ("What is a large body of salt water called?", "ocean"),
            ("What is the study of weather called?", "meteorology")
        ],
        "History": [
            ("Who was the first president of independent Zimbabwe?", "canaan banana"),
            ("In which year did Zimbabwe gain independence?", "1980"),
            ("What was Zimbabwe called before independence?", "rhodesia"),
            ("What is the study of past events called?", "history"),
            ("Which ancient civilization built pyramids at Giza?", "egyptian")
        ],
        "Economics": [
            ("What is the study of production, distribution and consumption called?", "economics"),
            ("What do we call the desire and ability to buy a product?", "demand"),
            ("What do we call the amount producers offer for sale?", "supply"),
            ("What is money paid for work called?", "wages"),
            ("What is the opposite of scarcity?", "abundance")
        ],
        "Accounting": [
            ("What is money owed by a business called?", "liability"),
            ("What the owner invests in a business is called what?", "capital"),
            ("What is money received by a business called?", "income"),
            ("What is money spent by a business called?", "expense"),
            ("What is the accounting equation?", "assets = capital + liabilities")
        ],
        "Social Studies": [
            ("What is a group of people living together in a place called?", "community"),
            ("What is the highest law of a country called?", "constitution"),
            ("What do we call the people who make laws?", "legislators"),
            ("What is the capital city of Zimbabwe?", "harare"),
            ("What is respect for one's country called?", "patriotism")
        ]
    }
    return banks.get(subject, banks["Science"])

def normalize(x):
    return " ".join(str(x or "").lower().strip().split())

def tutor_engine(sid, subject, message):
    try:
        from tutor.brain import tutor_reply

        sig = inspect.signature(tutor_reply)
        params = list(sig.parameters.keys())

        # Try to intelligently match the existing tutor function
        kwargs = {}

        for p in params:
            low = p.lower()

            if "student" in low or low in ("sid", "studentid"):
                kwargs[p] = sid
            elif "message" in low or "question" in low or "text" in low:
                kwargs[p] = message
            elif "subject" in low:
                kwargs[p] = subject

        try:
            result = tutor_reply(**kwargs)
        except:
            # Common fallback signatures
            try:
                result = tutor_reply(sid, message)
            except:
                result = tutor_reply(sid, subject, message)

        if result:
            return str(result)

    except Exception as e:
        pass

    return f"""
<b>{subject} Tutor 🧑‍🏫</b><br><br>
Good question! Let's work through it together.<br><br>
<b>Your question:</b> {message}<br><br>
Tell me exactly which part of {subject} you are finding difficult, and I will explain it step by step.
"""

def register_student_app(app):

    @app.route("/student/<int:sid>/home")
    def student_home(sid):
        s = student(sid)

        if not s:
            return "Student not found", 404

        subjects = selected_subjects(sid)
        cur = current_subject(sid)

        if not subjects:
            subject_text = "No subjects selected yet."
        else:
            subject_text = ", ".join(subjects)

        body = f"""
        <div class="hero">
            <h1>Welcome, {s['name']} 👋</h1>
            <h2>Digital Classroom Rules</h2>
            <p>Your personal learning centre</p>
            <p>🧑‍🏫 Tutor: <b>{s['tutor']}</b></p>
        </div>

        <div class="card">
            <h2>📊 Your Learning Profile</h2>
            <p><b>Grade/Form:</b> {s['grade_form'] or 'Not set'}</p>
            <p><b>🔥 Streak:</b> {s['streak'] or 0}</p>
            <p><b>📚 Lessons:</b> {s['paid_lessons'] or 0}</p>
        </div>

        <div class="card">
            <h2>📚 What do you want to study?</h2>
            <p>You can choose <b>one or multiple subjects</b>.</p>
            <p><b>Your subjects:</b> {subject_text}</p>
        </div>

        <div class="card">
            <h2>📖 Select Your Subjects</h2>
        """

        for sub in SUBJECTS:
            active = sub in subjects

            if active:
                button = f"""
                <a class="btn green"
                   href="/student/{sid}/select-subject?subject={sub}">
                   ✓ Selected — Open {sub}
                </a>
                """
            else:
                button = f"""
                <a class="btn"
                   href="/student/{sid}/select-subject?subject={sub}">
                   Choose {sub}
                </a>
                """

            body += f"""
            <div class="subject {'selected' if active else ''}">
                <b>{sub}</b>
                {button}
            </div>
            """

        body += f"""
        </div>

        <div class="card">
            <h2>🚀 Learning Centre</h2>
            <p>Current subject:
            <b>{cur or 'Choose a subject first'}</b></p>

            <a class="btn purple"
               href="/student/{sid}/subject">
               🧑‍🏫 Open My Learning Centre
            </a>

            <a class="btn gray"
               href="/student/{sid}/profile">
               👤 My Profile
            </a>
        </div>
        """

        return page("Student Home", body, sid)

    @app.route("/student/<int:sid>/select-subject")
    def select_subject(sid):
        sub = request.args.get("subject", "").strip()

        if sub not in SUBJECTS:
            return redirect(url_for("student_home", sid=sid))

        conn = db()

        exists = conn.execute(
            "SELECT id FROM student_subjects WHERE student_id=? AND subject=?",
            (sid, sub)
        ).fetchone()

        if exists:
            conn.execute(
                "UPDATE student_subjects SET active=? WHERE student_id=? AND subject=?",
                (0 if exists["id"] else 1, sid, sub)
            )

        # Simpler toggle logic
        row = conn.execute(
            "SELECT active FROM student_subjects WHERE student_id=? AND subject=?",
            (sid, sub)
        ).fetchone()

        if row:
            new_value = 0 if row["active"] else 1
            conn.execute(
                "UPDATE student_subjects SET active=? WHERE student_id=? AND subject=?",
                (new_value, sid, sub)
            )
        else:
            conn.execute(
                "INSERT INTO student_subjects(student_id,subject,active) VALUES(?,?,1)",
                (sid, sub)
            )

        # Always make the chosen subject current
        conn.execute(
            "UPDATE students SET current_subject=? WHERE id=?",
            (sub, sid)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("student_subject", sid=sid))

    @app.route("/student/<int:sid>/subject")
    def student_subject(sid):
        s = student(sid)

        if not s:
            return "Student not found", 404

        sub = current_subject(sid)

        if not sub:
            return redirect(url_for("student_home", sid=sid))

        body = f"""
        <div class="hero">
            <h1>📚 {sub} Learning Centre</h1>
            <p>Welcome {s['name']}.</p>
            <p>🧑‍🏫 Your tutor: <b>{s['tutor']}</b></p>
        </div>

        <div class="card">
            <h2>🎓 {sub}</h2>
            <p>Choose what you want to do.</p>

            <a class="btn green"
               href="/student/{sid}/trial?subject={sub}">
               🆓 FREE 30-Minute Trial
            </a>

            <a class="btn orange"
               href="/student/{sid}/paid?subject={sub}">
               💵 $1 — 1-Hour Lesson
            </a>

            <a class="btn"
               href="/student/{sid}/homework?subject={sub}">
               📝 {sub} Homework
            </a>

            <a class="btn purple"
               href="/student/{sid}/tutor?subject={sub}">
               🧑‍🏫 {sub} Tutor
            </a>

            <a class="btn gray"
               href="/student/{sid}/progress?subject={sub}">
               📊 {sub} Progress
            </a>
        </div>

        <div class="card">
            <h3>🔄 Change Subject</h3>
            """

        for x in selected_subjects(sid):
            body += f"""
            <a class="btn gray"
               href="/student/{sid}/set-current?subject={x}">
               Study {x}
            </a>
            """

        body += f"""
        </div>
        """

        return page(f"{sub} Learning Centre", body, sid)

    @app.route("/student/<int:sid>/set-current")
    def set_current(sid):
        sub = request.args.get("subject", "").strip()

        if sub in SUBJECTS:
            conn = db()
            conn.execute(
                "UPDATE students SET current_subject=? WHERE id=?",
                (sub, sid)
            )
            conn.commit()
            conn.close()

        return redirect(url_for("student_subject", sid=sid))

    @app.route("/student/<int:sid>/trial")
    def student_trial(sid):
        sub = request.args.get("subject") or current_subject(sid)

        body = f"""
        <div class="hero">
            <h1>🆓 FREE 30-Minute Trial</h1>
            <p>{sub}</p>
        </div>

        <div class="card">
            <h2>Try your first lesson FREE</h2>
            <p>You have <b>30 minutes</b> to learn with your tutor.</p>
            <p>No payment is required for the free trial.</p>

            <a class="btn green"
               href="/student/{sid}/session-start?type=trial&subject={sub}">
               ▶ START FREE 30-MINUTE TRIAL
            </a>

            <a class="btn gray"
               href="/student/{sid}/subject">
               ← Back to {sub} Learning Centre
            </a>
        </div>
        """

        return page("Free Trial", body, sid)

    @app.route("/student/<int:sid>/paid")
    def student_paid(sid):
        sub = request.args.get("subject") or current_subject(sid)

        body = f"""
        <div class="hero">
            <h1>💵 $1 — 1-Hour Lesson</h1>
            <p>{sub}</p>
        </div>

        <div class="card">
            <h2>One-hour lesson</h2>
            <p>Price: <b>$1 USD</b></p>
            <p>Subject: <b>{sub}</b></p>

            <p>Payment options:</p>
            <p>📱 EcoCash: Lucky Munyanyiwa — 0790 026 436</p>
            <p>💰 Mukuru: Lucky Munyanyiwa — +263 719 809 683</p>

            <a class="btn orange"
               href="/student/{sid}/session-start?type=paid&subject={sub}">
               ▶ START 1-HOUR LESSON
            </a>

            <a class="btn gray"
               href="/student/{sid}/subject">
               ← Back to {sub} Learning Centre
            </a>
        </div>
        """

        return page("Paid Lesson", body, sid)

    @app.route("/student/<int:sid>/session-start")
    def session_start(sid):
        s = student(sid)
        sub = request.args.get("subject") or current_subject(sid)
        typ = request.args.get("type", "trial")

        if not s or not sub:
            return redirect(url_for("student_home", sid=sid))

        # Enforce one free trial
        if typ == "trial" and s["free_trial_used"]:
            body = f"""
            <div class="card">
                <h2>🆓 Free Trial Already Used</h2>
                <p>Your 30-minute free trial has already been used.</p>
                <a class="btn orange"
                   href="/student/{sid}/paid?subject={sub}">
                   💵 Start $1 — 1-Hour Lesson
                </a>
                <a class="btn gray"
                   href="/student/{sid}/subject">
                   ← Back
                </a>
            </div>
            """
            return page("Trial Used", body, sid)

        minutes = 30 if typ == "trial" else 60
        now = datetime.now()
        expires = now + timedelta(minutes=minutes)

        conn = db()

        cur = conn.execute("""
            INSERT INTO student_sessions
            (student_id,subject,session_type,started_at,expires_at)
            VALUES (?,?,?,?,?)
        """, (
            sid,
            sub,
            typ,
            now.isoformat(),
            expires.isoformat()
        ))

        session_id = cur.lastrowid

        if typ == "trial":
            conn.execute(
                "UPDATE students SET free_trial_used=1 WHERE id=?",
                (sid,)
            )

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "student_session",
                sid=sid,
                session_id=session_id
            )
        )

    @app.route("/student/<int:sid>/session/<int:session_id>")
    def student_session(sid, session_id):
        conn = db()
        sess = conn.execute(
            "SELECT * FROM student_sessions WHERE id=? AND student_id=?",
            (session_id, sid)
        ).fetchone()
        conn.close()

        if not sess:
            return "Session not found", 404

        body = f"""
        <div class="hero">
            <h1>🧑‍🏫 {sess['subject']} Lesson</h1>
            <p>Your tutor is ready.</p>
        </div>

        <div class="card">
            <h2 id="timer">Loading timer...</h2>

            <p>
            Session type:
            <b>{'FREE 30-MINUTE TRIAL' if sess['session_type']=='trial' else '$1 — 1-HOUR LESSON'}</b>
            </p>

            <p>Subject: <b>{sess['subject']}</b></p>

            <hr>

            <h3>🎯 Lesson Goal</h3>
            <p>Learn, practise and check your understanding of {sess['subject']}.</p>

            <h3>✏️ Your Mission</h3>
            <p>Work with your tutor, ask questions and complete your practice.</p>

            <a class="btn green"
               href="/student/{sid}/session-complete/{session_id}">
               ✅ Finish Lesson
            </a>
        </div>

<script>
let end = new Date("{sess['expires_at']}").getTime();

function timer() {{
    let now = new Date().getTime();
    let distance = end - now;

    if(distance <= 0) {{
        document.getElementById("timer").innerHTML = "⏰ Session finished";
        return;
    }}

    let minutes = Math.floor(distance / 60000);
    let seconds = Math.floor((distance % 60000) / 1000);

    document.getElementById("timer").innerHTML =
        "⏱️ Time remaining: " + minutes + "m " + seconds + "s";
}}

timer();
setInterval(timer,1000);
</script>
        """

        return page("Lesson", body, sid)

    @app.route("/student/<int:sid>/session-complete/<int:session_id>")
    def session_complete(sid, session_id):
        conn = db()
        conn.execute(
            "UPDATE student_sessions SET completed=1 WHERE id=? AND student_id=?",
            (session_id, sid)
        )
        conn.commit()
        conn.close()

        body = """
        <div class="card">
            <h1>🎉 Lesson Complete!</h1>
            <p>Excellent work. Keep building your learning streak.</p>
        </div>
        """

        body += f"""
        <a class="btn purple"
           href="/student/{sid}/subject">
           📚 Back to Learning Centre
        </a>
        """

        return page("Lesson Complete", body, sid)

    @app.route("/student/<int:sid>/tutor")
    def student_tutor(sid):
        sub = request.args.get("subject") or current_subject(sid)

        response = None

        if request.method == "GET":
            pass

        body = f"""
        <div class="hero">
            <h1>🧑‍🏫 {sub} Tutor</h1>
            <p>Ask your tutor anything about {sub}.</p>
        </div>

        <div class="card">
            <form method="POST"
                  action="/student/{sid}/tutor/ask?subject={sub}">
                <label><b>Your question:</b></label>
                <textarea name="message"
                          rows="6"
                          placeholder="For example: Please explain fractions to me..."
                          required></textarea>

                <button class="btn purple" type="submit">
                    🧑‍🏫 Ask My Tutor
                </button>
            </form>
        </div>
        """

        return page(f"{sub} Tutor", body, sid)

    @app.route("/student/<int:sid>/tutor/ask", methods=["POST"])
    def student_tutor_ask(sid):
        sub = request.args.get("subject") or current_subject(sid)
        message = request.form.get("message", "").strip()

        if not message:
            return redirect(
                url_for("student_tutor", sid=sid, subject=sub)
            )

        answer = tutor_engine(sid, sub, message)

        body = f"""
        <div class="hero">
            <h1>🧑‍🏫 {sub} Tutor</h1>
            <p>Your tutor's response</p>
        </div>

        <div class="card">
            <h3>❓ You asked:</h3>
            <p>{message}</p>
        </div>

        <div class="card">
            <h3>🧑‍🏫 {student(sid)['tutor']} says:</h3>
            <div>{answer}</div>
        </div>

        <div class="card">
            <a class="btn purple"
               href="/student/{sid}/tutor?subject={sub}">
               💬 Ask Another Question
            </a>

            <a class="btn gray"
               href="/student/{sid}/subject">
               ← Back to Learning Centre
            </a>
        </div>
        """

        return page(f"{sub} Tutor", body, sid)

    @app.route("/student/<int:sid>/homework")
    def student_homework(sid):
        sub = request.args.get("subject") or current_subject(sid)

        body = f"""
        <div class="hero">
            <h1>📝 {sub} Homework</h1>
            <p>Practice what you have learned.</p>
        </div>

        <div class="card">
            <h2>🎯 Your Mission</h2>
            <p>Answer all five questions without looking for the answers.</p>

            <a class="btn"
               href="/student/{sid}/homework/start?subject={sub}">
               ▶ START {sub.upper()} HOMEWORK
            </a>

            <a class="btn gray"
               href="/student/{sid}/subject">
               ← Back to {sub} Learning Centre
            </a>
        </div>
        """

        return page(f"{sub} Homework", body, sid)

    @app.route("/student/<int:sid>/homework/start")
    def student_homework_start(sid):
        sub = request.args.get("subject") or current_subject(sid)
        questions = homework_bank(sub)

        body = f"""
        <div class="hero">
            <h1>📝 {sub} Homework</h1>
            <p>Answer every question.</p>
        </div>

        <form method="POST"
              action="/student/{sid}/homework/submit?subject={sub}">
        """

        for i, (question, answer) in enumerate(questions, 1):
            body += f"""
            <div class="question">
                <h3>Question {i}</h3>
                <p>{question}</p>

                <input type="text"
                       name="q{i}"
                       placeholder="Your answer"
                       required>
            </div>
            """

        body += f"""
            <button class="btn green" type="submit">
                ✅ SUBMIT HOMEWORK
            </button>
        </form>

        <a class="btn gray"
           href="/student/{sid}/subject">
           ← Back to Learning Centre
        </a>
        """

        return page(f"{sub} Homework", body, sid)

    @app.route("/student/<int:sid>/homework/submit", methods=["POST"])
    def student_homework_submit(sid):
        sub = request.args.get("subject") or current_subject(sid)
        questions = homework_bank(sub)

        score = 0
        results = []

        for i, (question, correct) in enumerate(questions, 1):
            answer = request.form.get(f"q{i}", "")
            good = normalize(answer) == normalize(correct)

            if good:
                score += 1

            results.append((question, answer, correct, good))

        percentage = int((score / len(questions)) * 100)

        body = f"""
        <div class="hero">
            <h1>📊 Homework Result</h1>
            <p>{sub}</p>
        </div>

        <div class="card">
            <h2>Score: {score}/{len(questions)}</h2>
            <h2>{percentage}%</h2>

            <div class="{'success' if percentage >= 50 else 'warning'}">
                {
                    'Excellent work! Keep it up! 🎉'
                    if percentage >= 80
                    else
                    'Good effort. Review the questions you missed and try again. 💪'
                    if percentage >= 50
                    else
                    'Do not give up. Let us correct these topics together. ❤️'
                }
            </div>
        </div>
        """

        for i, (question, answer, correct, good) in enumerate(results, 1):
            body += f"""
            <div class="question">
                <h3>Question {i}</h3>
                <p>{question}</p>
                <p><b>Your answer:</b> {answer}</p>
                <p><b>Correct answer:</b> {correct}</p>
                <p>{'✅ Correct' if good else '❌ Needs correction'}</p>
            </div>
            """

        body += f"""
        <a class="btn purple"
           href="/student/{sid}/tutor?subject={sub}">
           🧑‍🏫 Ask Tutor About {sub}
        </a>

        <a class="btn"
           href="/student/{sid}/homework?subject={sub}">
           📝 Try Homework Again
        </a>

        <a class="btn gray"
           href="/student/{sid}/subject">
           ← Back to Learning Centre
        </a>
        """

        return page("Homework Result", body, sid)

    @app.route("/student/<int:sid>/progress")
    def student_progress(sid):
        sub = request.args.get("subject") or current_subject(sid)

        conn = db()

        try:
            rows = conn.execute("""
                SELECT topic, mastery, attempts, correct
                FROM learning_topics
                WHERE student_id=? AND subject=?
                ORDER BY mastery ASC
            """, (sid, sub)).fetchall()
        except:
            rows = []

        conn.close()

        body = f"""
        <div class="hero">
            <h1>📊 {sub} Progress</h1>
            <p>Track your learning journey.</p>
        </div>

        <div class="card">
        """

        if rows:
            for r in rows:
                body += f"""
                <div class="question">
                    <b>{r['topic']}</b>
                    <p>Mastery: {r['mastery']}%</p>
                    <p>Attempts: {r['attempts']} | Correct: {r['correct']}</p>
                </div>
                """
        else:
            body += """
            <p>Your progress will appear here as you complete lessons and homework.</p>
            """

        body += f"""
        </div>

        <a class="btn purple"
           href="/student/{sid}/tutor?subject={sub}">
           🧑‍🏫 Study With Tutor
        </a>

        <a class="btn gray"
           href="/student/{sid}/subject">
           ← Back to Learning Centre
        </a>
        """

        return page(f"{sub} Progress", body, sid)

    @app.route("/student/<int:sid>/profile")
    def student_profile(sid):
        s = student(sid)

        if not s:
            return "Student not found", 404

        body = f"""
        <div class="hero">
            <h1>👤 My Profile</h1>
            <p>Digital Classroom Rules</p>
        </div>

        <div class="card">
            <h2>{s['name']}</h2>
            <p><b>Age:</b> {s['age']}</p>
            <p><b>School:</b> {s['school']}</p>
            <p><b>Location:</b> {s['location']}</p>
            <p><b>Grade/Form:</b> {s['grade_form']}</p>
            <p><b>Tutor:</b> {s['tutor']}</p>
            <p><b>🔥 Streak:</b> {s['streak'] or 0}</p>
            <p><b>📚 Paid lessons:</b> {s['paid_lessons'] or 0}</p>
        </div>

        <a class="btn purple"
           href="/student/{sid}/subject">
           📚 My Learning Centre
        </a>

        <a class="btn gray"
           href="/student/{sid}/home">
           🏠 Student Home
        </a>
        """

        return page("My Profile", body, sid)

    @app.route("/student/<int:sid>/lesson")
    def student_lesson(sid):
        sub = request.args.get("subject") or current_subject(sid)

        body = f"""
        <div class="hero">
            <h1>📖 {sub} Lesson</h1>
            <p>Student Lesson Centre</p>
        </div>

        <div class="card">
            <h2>🎯 Lesson Goal</h2>
            <p>Understand an important {sub} concept and practise it.</p>

            <h2>💡 Why It Matters</h2>
            <p>Strong understanding helps you answer examination questions with confidence.</p>

            <h2>✏️ Your Mission</h2>
            <p>Ask your tutor questions, study the explanation and complete your homework.</p>
        </div>

        <a class="btn purple"
           href="/student/{sid}/tutor?subject={sub}">
           🧑‍🏫 Ask {sub} Tutor
        </a>

        <a class="btn"
           href="/student/{sid}/homework?subject={sub}">
           📝 {sub} Homework
        </a>

        <a class="btn gray"
           href="/student/{sid}/subject">
           ← Back to Learning Centre
        </a>
        """

        return page(f"{sub} Lesson", body, sid)


# Make setup available to app startup
setup()
