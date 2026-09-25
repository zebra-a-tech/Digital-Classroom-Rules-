import sqlite3
import re
from datetime import datetime

DB = "digital_classroom.db"

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

TUTOR_NAMES = [
    "Tariro",
    "Tendai",
    "Nyasha",
    "Tatenda",
    "Rudo",
    "Blessing",
    "Brian",
    "Grace",
    "Michael",
    "Sarah"
]


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def setup_tutor_database():

    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tutor_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT,
            message TEXT,
            response TEXT,
            created_at TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            active INTEGER DEFAULT 1,
            added_at TEXT
        )
    """)

    conn.commit()
    conn.close()


setup_tutor_database()


def normalize(text):
    return re.sub(
        r"\s+",
        " ",
        str(text).strip().lower()
    )


def get_student(student_id):

    conn = db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    return student


def get_subjects(student_id):

    conn = db()

    rows = conn.execute("""
        SELECT subject
        FROM student_subjects
        WHERE student_id=? AND active=1
        ORDER BY id
    """, (student_id,)).fetchall()

    conn.close()

    subjects = [row["subject"] for row in rows]

    if not subjects:

        student = get_student(student_id)

        if student and student["subject"]:
            subjects = [student["subject"]]

    return subjects


def save_subjects(student_id, subjects):

    conn = db()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    conn.execute("""
        UPDATE student_subjects
        SET active=0
        WHERE student_id=?
    """, (student_id,))

    for subject in subjects:

        existing = conn.execute("""
            SELECT id
            FROM student_subjects
            WHERE student_id=? AND subject=?
        """, (
            student_id,
            subject
        )).fetchone()

        if existing:

            conn.execute("""
                UPDATE student_subjects
                SET active=1
                WHERE id=?
            """, (
                existing["id"],
            ))

        else:

            conn.execute("""
                INSERT INTO student_subjects
                (
                    student_id,
                    subject,
                    active,
                    added_at
                )
                VALUES (?, ?, 1, ?)
            """, (
                student_id,
                subject,
                now
            ))

    conn.commit()
    conn.close()


def remember(student_id, subject, message, response):

    conn = db()

    conn.execute("""
        INSERT INTO tutor_memory
        (
            student_id,
            subject,
            message,
            response,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        message,
        response,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()


def tutor_context(student_id):

    student = get_student(student_id)

    if not student:
        return None

    subjects = get_subjects(student_id)

    return {
        "name": student["name"],
        "age": student["age"],
        "school": student["school"],
        "location": student["location"],
        "grade": student["grade_form"],
        "exam_board": student["exam_board"],
        "tutor": student["tutor"],
        "subjects": subjects,
        "streak": student["streak"],
        "paid_lessons": student["paid_lessons"]
    }


def welcome(student_id):

    context = tutor_context(student_id)

    if not context:
        return "I couldn't find that learner."

    name = context["name"]
    tutor = context["tutor"] or "your tutor"

    subjects = context["subjects"]

    if subjects:

        subject_text = ", ".join(subjects)

        return f"""
Hello {name}! 👋

Welcome back to Digital Classroom Rules.

I'm {tutor}, your tutor.

Your current subjects are:
📚 {subject_text}

What would you like to work on today?

You can say:

• LESSON
• HOMEWORK
• EXAM PREP
• STUDY TIPS
• PROGRESS

Or simply tell me what you don't understand.

I'm here to help you understand it step by step. ❤️
""".strip()

    return f"""
Hello {name}! 👋

Welcome to Digital Classroom Rules.

I'm {tutor}, your tutor.

Before we begin, tell me which subject or subjects you want to study.

For example:

Maths
English
Science

Or:

Maths, English and Science

You can choose more than one subject.
""".strip()


def subject_selection_message():

    return """
📚 SUBJECT SELECTION

Which subject or subjects would you like to study?

You can choose one or several:

1. Maths
2. English
3. Science
4. Social Studies
5. Geography
6. History
7. Biology
8. Chemistry
9. Physics
10. Economics
11. Accounting

Example:

Maths, English, Science

You can change your subjects later.
""".strip()


def parse_subjects(message):

    text = normalize(message)

    selected = []

    aliases = {
        "math": "Maths",
        "maths": "Maths",
        "mathematics": "Maths",

        "english": "English",

        "science": "Science",

        "social": "Social Studies",
        "social studies": "Social Studies",

        "geography": "Geography",
        "geo": "Geography",

        "history": "History",

        "biology": "Biology",
        "bio": "Biology",

        "chemistry": "Chemistry",
        "chem": "Chemistry",

        "physics": "Physics",
        "phys": "Physics",

        "economics": "Economics",
        "econ": "Economics",

        "accounting": "Accounting",
        "accounts": "Accounting"
    }

    for key, subject in aliases.items():

        if key in text and subject not in selected:
            selected.append(subject)

    return selected


def tutor_reply(student_id, message, subject=None):

    context = tutor_context(student_id)

    if not context:
        return "Please register the learner first."

    text = normalize(message)

    selected = parse_subjects(text)

    # SUBJECT SELECTION

    if selected:

        save_subjects(student_id, selected)

        response = f"""
Excellent choice, {context['name']}! 📚

I've added:

{chr(10).join("• " + s for s in selected)}

Your tutor will now use these subjects when planning your lessons and homework.

Which subject would you like to start with?
""".strip()

        remember(
            student_id,
            "Subject Selection",
            message,
            response
        )

        return response


    # ASK FOR SUBJECTS

    current_subjects = context["subjects"]

    if not current_subjects:

        response = subject_selection_message()

        remember(
            student_id,
            "Subject Selection",
            message,
            response
        )

        return response


    # HELP

    if text in ["help", "commands", "menu"]:

        response = """
📚 DIGITAL CLASSROOM TUTOR

You can say:

LESSON
→ Start a guided lesson.

HOMEWORK
→ Get practice questions.

EXAM PREP
→ Prepare for examinations.

PROGRESS
→ See your learning progress.

STUDY TIPS
→ Get useful study advice.

SUBJECTS
→ Change or add subjects.

Or simply ask me a school question.

I'm here to teach, not just give you an answer.
""".strip()

        remember(student_id, subject, message, response)

        return response


    # SUBJECTS

    if text in [
        "subjects",
        "my subjects",
        "change subjects",
        "change subject"
    ]:

        response = subject_selection_message()

        remember(
            student_id,
            "Subject Selection",
            message,
            response
        )

        return response


    # LESSON

    if "lesson" in text or text == "start":

        chosen = subject or current_subjects[0]

        response = f"""
🎓 LET'S START {chosen.upper()}

Your tutor will guide you through:

1. Lesson Goal
2. Why It Matters
3. Tutor Explanation
4. Worked Example
5. Examination Question
6. Your Mission
7. Homework

Don't worry if you don't understand something.

Ask me to explain it again in a simpler way.

Ready to learn? 💪
""".strip()

        remember(
            student_id,
            chosen,
            message,
            response
        )

        return response


    # HOMEWORK

    if "homework" in text or "practice" in text:

        chosen = subject or current_subjects[0]

        response = f"""
📝 {chosen.upper()} HOMEWORK

Your tutor is ready to give you a practice assignment.

The assignment will be marked automatically where possible.

When you're ready, start your homework from your student dashboard.

Remember:

Don't guess.

Try the question yourself first. 💪
""".strip()

        remember(
            student_id,
            chosen,
            message,
            response
        )

        return response


    # EXAM PREP

    if (
        "exam" in text
        or "revision" in text
        or "revise" in text
    ):

        chosen = subject or current_subjects[0]

        response = f"""
🎯 EXAM PREPARATION — {chosen.upper()}

We will focus on:

• Important topics
• Understanding concepts
• Exam-style questions
• Common mistakes
• Marking techniques
• Timed practice

Your goal is not simply to memorise answers.

Your goal is to understand the work well enough to answer an examination question independently.

Let's prepare properly. 📚🔥
""".strip()

        remember(
            student_id,
            chosen,
            message,
            response
        )

        return response


    # STUDY TIPS

    if (
        "study tips" in text
        or "study tip" in text
        or "how do i study" in text
    ):

        response = """
📖 SMART STUDY TIPS

1. Study a little every day.
2. Understand before memorising.
3. Write your own notes.
4. Practise examination questions.
5. Mark your mistakes.
6. Ask when you don't understand.
7. Revise difficult topics more often.
8. Take short breaks.
9. Keep your schoolwork organised.
10. Test yourself without looking at the answer.

Small daily progress becomes big progress. 🌟
""".strip()

        remember(
            student_id,
            subject,
            message,
            response
        )

        return response


    # GREETING

    if text in [
        "hi",
        "hello",
        "hey",
        "good morning",
        "good afternoon",
        "good evening"
    ]:

        response = welcome(student_id)

        remember(
            student_id,
            subject,
            message,
            response
        )

        return response


    # GENERAL SCHOOL QUESTION
    chosen = subject or current_subjects[0]

    # Cross-subject reasoning engine.
    try:
        from tutor.reasoning import reason_about_question

        reasoning_response = reason_about_question(
            chosen,
            message,
            grade=context.get("grade"),
            learner_name=context.get("name", "Learner")
        )
    except Exception:
        reasoning_response = None

    if reasoning_response:
        response = reasoning_response
    else:
        response = f"""
I understand, {context['name']}.
You're currently studying {chosen}.

I want to help you understand the work properly.
Tell me the exact question or topic you're struggling with.

For example:
"What is photosynthesis?"
"I don't understand fractions."
"Help me solve this equation."

I'll explain it step by step. 👨‍🏫📚
""".strip()

    remember(
        student_id,
        chosen,
        message,
        response
    )
    return response
