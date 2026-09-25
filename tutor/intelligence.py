import sqlite3
import re
from datetime import datetime

DB = "digital_classroom.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def setup_intelligence():

    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS learning_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            level TEXT,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            mastery INTEGER DEFAULT 0,
            last_activity TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tutor_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT,
            topic TEXT,
            learner_message TEXT,
            tutor_response TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


setup_intelligence()


# -------------------------------------------------
# LEVEL DETECTION
# -------------------------------------------------

def get_level(grade_form):

    text = str(grade_form or "").lower()

    numbers = re.findall(r"\d+", text)

    number = int(numbers[0]) if numbers else 1

    if "grade" in text:

        return "primary"

    if "form" in text:

        if number <= 3:
            return "junior_secondary"

        return "senior_secondary"

    return "primary"


# -------------------------------------------------
# TOPIC DETECTION
# -------------------------------------------------

TOPICS = {

    "maths": {
        "fractions": [
            "fraction",
            "fractions",
            "numerator",
            "denominator"
        ],
        "algebra": [
            "algebra",
            "equation",
            "equations",
            "solve for x",
            "unknown"
        ],
        "percentages": [
            "percentage",
            "percent",
            "%"
        ],
        "multiplication": [
            "multiply",
            "multiplication",
            "times"
        ],
        "division": [
            "divide",
            "division"
        ],
        "geometry": [
            "area",
            "perimeter",
            "triangle",
            "rectangle",
            "circle",
            "angle"
        ]
    },

    "english": {
        "grammar": [
            "grammar",
            "noun",
            "verb",
            "adjective",
            "adverb",
            "pronoun"
        ],
        "tenses": [
            "tense",
            "past tense",
            "present tense",
            "future tense"
        ],
        "sentence_construction": [
            "sentence",
            "sentence construction"
        ],
        "comprehension": [
            "comprehension",
            "passage"
        ]
    },

    "science": {
        "human_body": [
            "human body",
            "heart",
            "lungs",
            "blood",
            "digest"
        ],
        "plants": [
            "plant",
            "plants",
            "photosynthesis"
        ],
        "forces": [
            "force",
            "gravity",
            "friction"
        ],
        "matter": [
            "solid",
            "liquid",
            "gas",
            "matter"
        ]
    },

    "biology": {
        "cells": [
            "cell",
            "cells",
            "cell structure"
        ],
        "photosynthesis": [
            "photosynthesis",
            "chlorophyll"
        ],
        "respiration": [
            "respiration",
            "breathing"
        ],
        "human_body": [
            "human body",
            "organ",
            "heart",
            "lungs"
        ]
    },

    "chemistry": {
        "atoms": [
            "atom",
            "atoms",
            "electron",
            "proton",
            "neutron"
        ],
        "elements": [
            "element",
            "elements",
            "periodic table"
        ],
        "acids": [
            "acid",
            "alkali",
            "alkaline",
            "ph"
        ],
        "chemical_symbols": [
            "chemical symbol",
            "symbol"
        ]
    },

    "physics": {
        "forces": [
            "force",
            "gravity",
            "friction"
        ],
        "energy": [
            "energy",
            "kinetic",
            "potential"
        ],
        "electricity": [
            "electricity",
            "current",
            "voltage",
            "circuit"
        ],
        "motion": [
            "motion",
            "speed",
            "velocity",
            "distance"
        ]
    },

    "geography": {
        "maps": [
            "map",
            "maps",
            "scale",
            "direction"
        ],
        "weather": [
            "weather",
            "rainfall",
            "temperature",
            "climate"
        ],
        "rivers": [
            "river",
            "rivers",
            "drainage"
        ],
        "population": [
            "population",
            "migration"
        ]
    },

    "history": {
        "sources": [
            "historical source",
            "primary source",
            "secondary source",
            "evidence"
        ],
        "colonialism": [
            "colonial",
            "colonialism",
            "colonisation"
        ],
        "independence": [
            "independence",
            "liberation"
        ]
    },

    "economics": {
        "supply_demand": [
            "supply",
            "demand",
            "equilibrium"
        ],
        "scarcity": [
            "scarcity",
            "shortage",
            "resources"
        ],
        "markets": [
            "market",
            "consumer",
            "producer"
        ]
    },

    "accounting": {
        "accounting_equation": [
            "accounting equation",
            "assets",
            "liabilities",
            "capital"
        ],
        "cash_book": [
            "cash book",
            "cashbook"
        ],
        "ledger": [
            "ledger",
            "debit",
            "credit"
        ]
    },

    "social studies": {
        "family": [
            "family",
            "families"
        ],
        "community": [
            "community",
            "communities"
        ],
        "citizenship": [
            "citizen",
            "citizenship",
            "rights",
            "responsibilities"
        ]
    }
}


def detect_topic(subject, message):

    subject_key = str(subject or "").lower()
    text = str(message or "").lower()

    topics = TOPICS.get(subject_key, {})

    for topic, words in topics.items():

        for word in words:

            if word in text:
                return topic

    return "general"


# -------------------------------------------------
# TEACHING CONTENT
# -------------------------------------------------

LESSONS = {

    "maths": {

        "fractions": {
            "title": "Understanding Fractions",
            "explanation":
                "A fraction represents a part of a whole. "
                "The numerator is the number on top and tells "
                "us how many parts we have. The denominator is "
                "the number below and tells us how many equal "
                "parts make the whole.",
            "example":
                "If a pizza is divided into 4 equal pieces "
                "and you eat 1 piece, you have eaten 1/4.",
            "question":
                "A cake is divided into 8 equal pieces. "
                "A pupil eats 3 pieces. What fraction of the "
                "cake was eaten?",
            "answer": "3/8"
        },

        "algebra": {
            "title": "Introduction to Algebra",
            "explanation":
                "Algebra uses letters to represent unknown values. "
                "An equation tells us that two expressions are equal.",
            "example":
                "If x + 5 = 12, subtract 5 from both sides. "
                "Therefore x = 7.",
            "question":
                "Solve: x + 8 = 15.",
            "answer": "7"
        },

        "percentages": {
            "title": "Understanding Percentages",
            "explanation":
                "A percentage means a part out of 100. "
                "For example, 25% means 25 out of every 100.",
            "example":
                "10% of 200 is 20.",
            "question":
                "What is 10% of 300?",
            "answer": "30"
        },

        "multiplication": {
            "title": "Multiplication",
            "explanation":
                "Multiplication is repeated addition. "
                "For example, 4 × 3 means four groups of three.",
            "example":
                "4 × 3 = 3 + 3 + 3 + 3 = 12.",
            "question":
                "What is 7 × 6?",
            "answer": "42"
        },

        "division": {
            "title": "Division",
            "explanation":
                "Division means sharing a quantity into equal groups.",
            "example":
                "12 ÷ 3 = 4 because 12 can be shared into "
                "3 equal groups of 4.",
            "question":
                "What is 24 ÷ 6?",
            "answer": "4"
        },

        "geometry": {
            "title": "Basic Geometry",
            "explanation":
                "Geometry is the study of shapes, sizes, "
                "angles and space.",
            "example":
                "The area of a rectangle is length × width.",
            "question":
                "A rectangle is 8 cm long and 5 cm wide. "
                "What is its area?",
            "answer": "40"
        }
    },

    "english": {

        "grammar": {
            "title": "Grammar",
            "explanation":
                "Grammar is the system of rules we use to "
                "construct meaningful sentences.",
            "example":
                "In 'The boy runs', 'boy' is a noun and "
                "'runs' is a verb.",
            "question":
                "Identify the noun in: 'The teacher opened the book.'",
            "answer": "teacher"
        },

        "tenses": {
            "title": "Verb Tenses",
            "explanation":
                "Tenses show when an action happens.",
            "example":
                "Present: I walk. Past: I walked. "
                "Future: I will walk.",
            "question":
                "Give the past tense of 'go'.",
            "answer": "went"
        },

        "sentence_construction": {
            "title": "Sentence Construction",
            "explanation":
                "A good sentence normally expresses a complete "
                "idea and begins with a capital letter.",
            "example":
                "The pupil completed the exercise.",
            "question":
                "Complete: The children _____ playing football.",
            "answer": "are"
        },

        "comprehension": {
            "title": "Reading Comprehension",
            "explanation":
                "Comprehension means understanding information "
                "that you read.",
            "example":
                "Read carefully, identify important details, "
                "and answer using evidence from the passage.",
            "question":
                "What is the main purpose of a comprehension passage?",
            "answer": "to test understanding"
        }
    },

    "science": {

        "human_body": {
            "title": "The Human Body",
            "explanation":
                "The human body contains organs that perform "
                "different functions.",
            "example":
                "The heart pumps blood around the body.",
            "question":
                "Which organ pumps blood around the body?",
            "answer": "heart"
        },

        "plants": {
            "title": "Plants and Photosynthesis",
            "explanation":
                "Green plants make their own food through "
                "photosynthesis using light energy.",
            "example":
                "Plants use carbon dioxide and water to make "
                "food in the presence of light.",
            "question":
                "What process do green plants use to make food?",
            "answer": "photosynthesis"
        },

        "forces": {
            "title": "Forces",
            "explanation":
                "A force is a push or a pull that can change "
                "the motion or shape of an object.",
            "example":
                "Gravity pulls objects towards Earth.",
            "question":
                "What force pulls objects towards Earth?",
            "answer": "gravity"
        },

        "matter": {
            "title": "States of Matter",
            "explanation":
                "The three common states of matter are solid, "
                "liquid and gas.",
            "example":
                "Ice is a solid, water is a liquid and steam "
                "is a gas.",
            "question":
                "Name the three common states of matter.",
            "answer": "solid liquid gas"
        }
    },

    "biology": {

        "cells": {
            "title": "Cells",
            "explanation":
                "A cell is the basic structural and functional "
                "unit of living organisms.",
            "example":
                "Human beings are made up of many cells.",
            "question":
                "What is the basic unit of life?",
            "answer": "cell"
        },

        "photosynthesis": {
            "title": "Photosynthesis",
            "explanation":
                "Photosynthesis is the process by which green "
                "plants make food using light energy.",
            "example":
                "Chlorophyll absorbs light energy.",
            "question":
                "What is the name of the process by which plants "
                "make food?",
            "answer": "photosynthesis"
        },

        "respiration": {
            "title": "Respiration",
            "explanation":
                "Respiration releases energy from food for use "
                "by living cells.",
            "example":
                "Aerobic respiration uses oxygen.",
            "question":
                "Which gas is required for aerobic respiration?",
            "answer": "oxygen"
        },

        "human_body": {
            "title": "Human Body",
            "explanation":
                "The human body contains specialised organs "
                "that work together.",
            "example":
                "The lungs are involved in gas exchange.",
            "question":
                "Which organs are mainly responsible for breathing?",
            "answer": "lungs"
        }
    },

    "chemistry": {

        "atoms": {
            "title": "Atoms",
            "explanation":
                "An atom is the smallest unit of an element "
                "that retains the properties of that element.",
            "example":
                "Atoms contain protons, neutrons and electrons.",
            "question":
                "Name the three main subatomic particles.",
            "answer": "protons neutrons electrons"
        },

        "elements": {
            "title": "Elements",
            "explanation":
                "An element is a pure substance made of only "
                "one type of atom.",
            "example":
                "Oxygen is an element.",
            "question":
                "What is a substance made of only one type of atom called?",
            "answer": "element"
        },

        "acids": {
            "title": "Acids and Alkalis",
            "explanation":
                "Acids and alkalis have different chemical "
                "properties and can be identified using indicators.",
            "example":
                "A neutral solution has a pH of 7.",
            "question":
                "What is the pH of a neutral solution?",
            "answer": "7"
        },

        "chemical_symbols": {
            "title": "Chemical Symbols",
            "explanation":
                "Chemical symbols are short forms used to "
                "represent elements.",
            "example":
                "O represents oxygen and H represents hydrogen.",
            "question":
                "What is the chemical symbol for oxygen?",
            "answer": "O"
        }
    },

    "physics": {

        "forces": {
            "title": "Forces",
            "explanation":
                "Forces are pushes or pulls that can change "
                "the motion of objects.",
            "example":
                "Gravity is a force that attracts objects towards Earth.",
            "question":
                "What force pulls objects towards Earth?",
            "answer": "gravity"
        },

        "energy": {
            "title": "Energy",
            "explanation":
                "Energy is the ability to do work or cause change.",
            "example":
                "Moving objects have kinetic energy.",
            "question":
                "What type of energy does a moving object have?",
            "answer": "kinetic energy"
        },

        "electricity": {
            "title": "Electricity",
            "explanation":
                "Electric current is the flow of electric charge.",
            "example":
                "Current is measured in amperes.",
            "question":
                "What is the unit of electric current?",
            "answer": "ampere"
        },

        "motion": {
            "title": "Motion",
            "explanation":
                "Motion describes a change in position over time.",
            "example":
                "Speed describes how quickly distance is covered.",
            "question":
                "What is the basic formula for speed?",
            "answer": "distance divided by time"
        }
    }
}


# -------------------------------------------------
# GENERAL TEACHING CONTENT
# -------------------------------------------------

GENERAL_LESSONS = {

    "geography": (
        "Geography is the study of places, people, environments "
        "and the relationships between them."
    ),

    "history": (
        "History is the study of past events using evidence "
        "from different sources."
    ),

    "economics": (
        "Economics studies how people and societies use limited "
        "resources to satisfy needs and wants."
    ),

    "accounting": (
        "Accounting involves recording, classifying and "
        "summarising financial transactions."
    ),

    "social studies": (
        "Social Studies helps learners understand people, "
        "communities, citizenship and society."
    )
}


def find_lesson(subject, topic):

    subject_key = str(subject or "").lower()

    if subject_key in LESSONS:

        if topic in LESSONS[subject_key]:
            return LESSONS[subject_key][topic]

    return None


# -------------------------------------------------
# MASTERY
# -------------------------------------------------

def update_mastery(
    student_id,
    subject,
    topic,
    correct
):

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM learning_topics
        WHERE student_id=?
        AND subject=?
        AND topic=?
    """, (
        student_id,
        subject,
        topic
    )).fetchone()

    now = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    if not row:

        attempts = 1
        correct_count = 1 if correct else 0

        mastery = int(
            (correct_count / attempts) * 100
        )

        conn.execute("""
            INSERT INTO learning_topics
            (
                student_id,
                subject,
                topic,
                level,
                attempts,
                correct,
                mastery,
                last_activity
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id,
            subject,
            topic,
            "developing",
            attempts,
            correct_count,
            mastery,
            now
        ))

    else:

        attempts = row["attempts"] + 1

        correct_count = (
            row["correct"] +
            (1 if correct else 0)
        )

        mastery = int(
            (correct_count / attempts) * 100
        )

        conn.execute("""
            UPDATE learning_topics

            SET attempts=?,
                correct=?,
                mastery=?,
                last_activity=?

            WHERE id=?
        """, (
            attempts,
            correct_count,
            mastery,
            now,
            row["id"]
        ))

    conn.commit()
    conn.close()


def get_mastery(student_id, subject, topic):

    conn = db()

    row = conn.execute("""
        SELECT mastery
        FROM learning_topics
        WHERE student_id=?
        AND subject=?
        AND topic=?
    """, (
        student_id,
        subject,
        topic
    )).fetchone()

    conn.close()

    if not row:
        return 0

    return row["mastery"]


# -------------------------------------------------
# ANSWER CHECKING
# -------------------------------------------------

def clean_answer(text):

    text = str(text or "").lower()

    text = re.sub(
        r"[^a-z0-9\s/%.+-]",
        "",
        text
    )

    return re.sub(
        r"\s+",
        " ",
        text
    ).strip()


def check_answer(answer, correct):

    given = clean_answer(answer)
    expected = clean_answer(correct)

    if not given:
        return False

    if given == expected:
        return True

    if expected and expected in given:
        return True

    return False


# -------------------------------------------------
# TUTOR RESPONSE
# -------------------------------------------------

def teach(
    student_id,
    subject,
    message
):

    conn = db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    if not student:
        return "I couldn't find this learner."

    name = student["name"]
    grade = student["grade_form"]

    topic = detect_topic(
        subject,
        message
    )

    lesson = find_lesson(
        subject,
        topic
    )

    if lesson:

        mastery = get_mastery(
            student_id,
            subject,
            topic
        )

        if mastery >= 80:

            difficulty = """
You are doing well with this topic. Your next step is
to practise examination-style questions and apply the
idea in unfamiliar situations.
"""

        elif mastery >= 50:

            difficulty = """
You have some understanding already. We will strengthen
the areas where you are still making mistakes.
"""

        else:

            difficulty = """
We are going to build this topic from the basics.
There is no need to rush.
"""

        response = f"""
👨‍🏫 {name}, let's work on {lesson['title']}.

🎓 Level:
{grade}

📚 Subject:
{subject}

🎯 Topic:
{topic.replace('_', ' ').title()}

━━━━━━━━━━━━━━━━━━

📖 EXPLANATION

{lesson['explanation']}

━━━━━━━━━━━━━━━━━━

💡 EXAMPLE

{lesson['example']}

━━━━━━━━━━━━━━━━━━

{difficulty}

━━━━━━━━━━━━━━━━━━

📝 YOUR TURN

{lesson['question']}

Don't worry about getting it wrong.

Try it yourself first, then send me your answer.

I'm going to use your answer to decide what we should
work on next.
""".strip()

    elif str(subject).lower() in GENERAL_LESSONS:

        response = f"""
👨‍🏫 {name}, let's work on {subject}.

🎓 Level:
{grade}

📚 Topic:
{topic.replace('_', ' ').title()}

━━━━━━━━━━━━━━━━━━

{GENERAL_LESSONS[str(subject).lower()]}

━━━━━━━━━━━━━━━━━━

🎯 YOUR MISSION

Tell me the exact topic you are studying in {subject},
or send me a question from your schoolwork.

I will break it down into smaller steps and help you
understand it.
""".strip()

    else:

        response = f"""
👨‍🏫 {name}, I'm ready to help you with {subject}.

Tell me the exact topic or question you are working on.

For example:

• Explain this topic
• Give me an example
• I don't understand this
• Give me an exam question
• Mark my answer

We will work through it step by step.
""".strip()

    conn = db()

    conn.execute("""
        INSERT INTO tutor_sessions
        (
            student_id,
            subject,
            topic,
            learner_message,
            tutor_response,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        student_id,
        subject,
        topic,
        message,
        response,
        datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    ))

    conn.commit()
    conn.close()

    return response

# Compatibility bridge:
# Some tutor routes use functions from the original tutor brain.
# Re-export them here so both systems can work together.

from tutor.brain import (
    get_student,
    get_subjects,
    save_subjects,
    remember,
    tutor_context,
    welcome,
    subject_selection_message,
    parse_subjects,
    tutor_reply
)

print("Tutor brain compatibility bridge: CONNECTED")
