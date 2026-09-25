import sqlite3
from flask import request, redirect, url_for, render_template_string

from tutor.adaptive import record_result, get_mastery, save_tutor_session

DB = "digital_classroom.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


RECOVERY = {
    "fractions": {
        "explanation": "A fraction shows a part of a whole. The top number is the numerator and tells us how many parts we have. The bottom number is the denominator and tells us how many equal parts make the whole.",
        "question": "A chocolate bar has 4 equal pieces. You eat 1 piece. What fraction did you eat?",
        "answer": "1/4"
    },
    "algebra": {
        "explanation": "In algebra, a letter such as x represents an unknown number. We solve the equation by finding the number that makes both sides equal.",
        "question": "If x + 3 = 8, what is x?",
        "answer": "5"
    },
    "percentages": {
        "explanation": "A percentage means 'out of 100'. For example, 10% means 10 out of 100.",
        "question": "What is 10% of 100?",
        "answer": "10"
    },
    "multiplication": {
        "explanation": "Multiplication is repeated addition. For example, 5 × 4 means adding 5 four times.",
        "question": "What is 5 × 4?",
        "answer": "20"
    },
    "division": {
        "explanation": "Division means sharing equally or finding how many equal groups can be made.",
        "question": "What is 12 ÷ 3?",
        "answer": "4"
    },
    "geometry": {
        "explanation": "The area of a rectangle is found by multiplying its length by its width.",
        "question": "A rectangle is 4 cm long and 3 cm wide. What is its area?",
        "answer": "12"
    },
    "grammar": {
        "explanation": "A noun is a person, place, animal or thing. In a sentence, nouns are often the people or things doing something.",
        "question": "Find the noun in this sentence: The girl smiled.",
        "answer": "girl"
    },
    "tenses": {
        "explanation": "Tenses tell us when something happens. The past tense tells us that something already happened.",
        "question": "What is the past tense of 'walk'?",
        "answer": "walked"
    },
    "sentence construction": {
        "explanation": "A good sentence normally begins with a capital letter and ends with the correct punctuation. It should also express a complete thought.",
        "question": "Complete the sentence: The boys ___ happy.",
        "answer": "are"
    },
    "human body": {
        "explanation": "Different organs perform different jobs in the human body.",
        "question": "Which organ pumps blood around the body?",
        "answer": "heart"
    },
    "plants": {
        "explanation": "Plants make their own food using light energy. This process is called photosynthesis.",
        "question": "What process do green plants use to make their food?",
        "answer": "photosynthesis"
    },
    "forces": {
        "explanation": "A force is a push or a pull. Forces can change the movement or direction of an object.",
        "question": "What force pulls objects towards the Earth?",
        "answer": "gravity"
    },
    "matter": {
        "explanation": "Matter is anything that has mass and takes up space. Common states include solids, liquids and gases.",
        "question": "Name one state of matter.",
        "answer": "solid"
    },
    "cells": {
        "explanation": "A cell is the basic structural and functional unit of living organisms.",
        "question": "What is the basic unit of life?",
        "answer": "cell"
    },
    "photosynthesis": {
        "explanation": "Photosynthesis is the process by which green plants use light energy to make food.",
        "question": "What process allows green plants to make food?",
        "answer": "photosynthesis"
    },
    "respiration": {
        "explanation": "Respiration releases energy from food so that living organisms can carry out life processes.",
        "question": "Which gas is commonly needed for aerobic respiration?",
        "answer": "oxygen"
    },
    "chemical symbols": {
        "explanation": "Chemical symbols are short ways of representing elements. For example, O represents oxygen and H represents hydrogen.",
        "question": "What element does the symbol O represent?",
        "answer": "oxygen"
    },
    "atoms": {
        "explanation": "Everything around us is made from matter, and matter is made from tiny particles called atoms.",
        "question": "What are the tiny particles that make up elements called?",
        "answer": "atoms"
    },
    "electricity": {
        "explanation": "An electric circuit needs a complete path for electric current to flow.",
        "question": "What must a circuit have for current to flow?",
        "answer": "complete circuit"
    },
    "motion": {
        "explanation": "Motion describes a change in an object's position over time.",
        "question": "What do we call a change in position over time?",
        "answer": "motion"
    }
}


def normalise(text):
    return " ".join(str(text).strip().lower().split())


def get_recovery(topic):
    topic_clean = normalise(topic)

    if topic_clean in RECOVERY:
        return RECOVERY[topic_clean]

    for key, value in RECOVERY.items():
        if key in topic_clean or topic_clean in key:
            return value

    return {
        "explanation": (
            "Let's slow down and look at this topic carefully. "
            "The goal is not just to get the answer right, but to understand why the answer is right."
        ),
        "question": "Explain the main idea of this topic in your own words.",
        "answer": ""
    }


def register_recovery_routes(app):

    @app.route("/tutor/<int:student_id>/recovery")
    def tutor_recovery(student_id):
        subject = request.args.get("subject", "General")
        topic = request.args.get("topic", "General")
        question_id = request.args.get("question_id", "")

        conn = db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )
        student = cur.fetchone()

        conn.close()

        if not student:
            return "Student not found", 404

        lesson = get_recovery(topic)
        mastery = get_mastery(student_id, subject, topic)

        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tutor Correction</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    margin: 0;
    padding: 20px;
}
.card {
    max-width: 700px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 4px 15px rgba(0,0,0,.08);
}
h1 { color: #17365d; }
.topic {
    background: #eef4ff;
    padding: 15px;
    border-radius: 12px;
}
.question {
    background: #fff8df;
    padding: 18px;
    border-radius: 12px;
    margin-top: 18px;
}
input {
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    box-sizing: border-box;
    border: 1px solid #ccc;
    border-radius: 10px;
    font-size: 16px;
}
button {
    width: 100%;
    padding: 15px;
    margin-top: 15px;
    border: none;
    border-radius: 10px;
    background: #17365d;
    color: white;
    font-size: 16px;
}
.small {
    color: #666;
}
</style>
</head>

<body>
<div class="card">

<h1>🧠 Tutor Correction Lesson</h1>

<p>
Hi {{ student["name"] }} ❤️
</p>

<div class="topic">
<strong>Subject:</strong> {{ subject }}<br>
<strong>Topic:</strong> {{ topic }}<br>
<strong>Current mastery:</strong> {{ mastery }}%
</div>

<h2>Let's fix this together.</h2>

<p>
Don't worry about getting the previous question wrong.
Every mistake gives your tutor information about what needs more practice.
</p>

<h3>📚 Learn it</h3>

<p>{{ lesson["explanation"] }}</p>

<div class="question">
<h3>🎯 Your Turn</h3>
<p><strong>{{ lesson["question"] }}</strong></p>

<form method="POST"
      action="{{ url_for('tutor_recovery_answer', student_id=student_id) }}">

<input type="hidden" name="subject" value="{{ subject }}">
<input type="hidden" name="topic" value="{{ topic }}">
<input type="hidden" name="question_id" value="{{ question_id }}">

<input
    type="text"
    name="answer"
    placeholder="Type your answer here..."
    required
>

<button type="submit">
Check My Answer
</button>

</form>
</div>

<p class="small">
Your tutor will use this answer to update your mastery of this topic.
</p>

</div>
</body>
</html>
        """,
        student=student,
        student_id=student_id,
        subject=subject,
        topic=topic,
        mastery=mastery,
        lesson=lesson,
        question_id=question_id
        )


    @app.route("/tutor/<int:student_id>/recovery-answer", methods=["POST"])
    def tutor_recovery_answer(student_id):

        subject = request.form.get("subject", "General")
        topic = request.form.get("topic", "General")
        answer = request.form.get("answer", "").strip()

        lesson = get_recovery(topic)

        correct_answer = normalise(lesson.get("answer", ""))
        given_answer = normalise(answer)

        if correct_answer:
            correct = (
                given_answer == correct_answer
                or correct_answer in given_answer
                or given_answer in correct_answer
            )
        else:
            correct = len(given_answer) >= 3

        mastery = record_result(
            student_id,
            subject,
            topic,
            correct
        )

        if correct:
            response = (
                "Excellent! You understood the correction. "
                "Your mastery of this topic has improved."
            )

            save_tutor_session(
                student_id,
                subject,
                topic,
                answer,
                response
            )

            message = f"""
            <div class="success">
            🎉 <strong>Excellent work!</strong><br><br>
            You got the correction right.<br><br>
            <strong>Your mastery is now {mastery}%.</strong>
            </div>
            """
        else:
            response = (
                "The learner still needs support with this topic. "
                "The tutor should explain it again using a simpler example."
            )

            save_tutor_session(
                student_id,
                subject,
                topic,
                answer,
                response
            )

            message = f"""
            <div class="retry">
            👍 <strong>Not quite yet — and that's okay.</strong><br><br>
            Let's keep working on it. Your current mastery is
            <strong>{mastery}%</strong>.
            </div>
            """

        return render_template_string("""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Tutor Feedback</title>
<style>
body {
    font-family: Arial, sans-serif;
    background: #f4f7fb;
    padding: 20px;
}
.card {
    max-width: 650px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
}
.success, .retry {
    padding: 20px;
    border-radius: 12px;
    margin: 20px 0;
}
.success { background: #e8f8ed; }
.retry { background: #fff4d6; }
a {
    display: block;
    text-align: center;
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

<h1>🧑‍🏫 Tutor Feedback</h1>

{{ message|safe }}

<a href="{{ url_for('tutor_recovery',
    student_id=student_id,
    subject=subject,
    topic=topic) }}">
Continue Practice
</a>

<a href="{{ url_for('tutor_page',
    student_id=student_id) }}">
Back to Tutor
</a>

</div>
</body>
</html>
        """,
        message=message,
        student_id=student_id,
        subject=subject,
        topic=topic
        )
