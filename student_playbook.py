from flask import request, redirect, url_for, render_template_string
import sqlite3
from datetime import datetime


# ============================================================
# RESTRICTED TRIAL SETTINGS
# ============================================================
# During the free trial, students can access ONLY the first N topics
# per subject. Paid sessions unlock ALL topics.
RESTRICTED_TRIAL_TOPICS_PER_SUBJECT = 3


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

PLAYBOOK = {

"Maths": {
    "Fractions": {
        "goal": "Understand what fractions represent and how to work with them.",
        "learn": """A fraction shows part of a whole.

The top number is the numerator. It tells us how many parts we have.

The bottom number is the denominator. It tells us how many equal parts make the whole.

For example, 3/4 means 3 parts out of 4 equal parts.""",
        "example": "Example: 1/4 + 2/4 = 3/4 because the denominators are already the same.",
        "question": "What is 2/5 + 1/5?",
        "answer": "3/5",
        "hint": "The denominators are the same, so add the numerators."
    },

    "Decimals": {
        "goal": "Understand decimal numbers and place value.",
        "learn": """Decimals represent parts of a whole.

For example:
0.5 = five tenths
0.25 = twenty-five hundredths

The first digit after the decimal point represents tenths.
The second represents hundredths.""",
        "example": "Example: 0.4 + 0.3 = 0.7",
        "question": "What is 0.6 + 0.2?",
        "answer": "0.8",
        "hint": "Add the tenths."
    },

    "Percentages": {
        "goal": "Understand percentages and calculate simple percentages.",
        "learn": """Percent means 'out of 100'.

50% means 50 out of 100.
25% means 25 out of 100.
10% means 10 out of 100.

To find a percentage of a number, convert the percentage to a decimal and multiply.""",
        "example": "Example: 10% of 50 = 0.10 × 50 = 5",
        "question": "What is 10% of 80?",
        "answer": "8",
        "hint": "Convert 10% to 0.10 and multiply by 80."
    },

    "Algebra": {
        "goal": "Understand variables and simple algebraic expressions.",
        "learn": """A variable is a letter used to represent an unknown number.

For example:
x + 3 = 8

We want to find the value of x.

Subtract 3 from both sides:
x = 5""",
        "example": "Example: x + 4 = 10, therefore x = 6.",
        "question": "If x + 5 = 12, what is x?",
        "answer": "7",
        "hint": "Subtract 5 from 12."
    },

    "Multiplication": {
        "goal": "Build confidence with multiplication.",
        "learn": """Multiplication is repeated addition.

For example:
4 × 3 means 4 groups of 3.

3 + 3 + 3 + 3 = 12.

Therefore 4 × 3 = 12.""",
        "example": "Example: 6 × 5 = 30",
        "question": "What is 7 × 6?",
        "answer": "42",
        "hint": "Think of 7 groups of 6."
    },

    "Division": {
        "goal": "Understand division as sharing or grouping.",
        "learn": """Division tells us how many equal groups can be made.

For example:
12 ÷ 3 = 4

This means 12 can be divided into 3 equal groups of 4.""",
        "example": "Example: 20 ÷ 5 = 4",
        "question": "What is 24 ÷ 6?",
        "answer": "4",
        "hint": "Ask: 6 multiplied by what gives 24?"
    },

    "Geometry": {
        "goal": "Understand common shapes and their properties.",
        "learn": """Geometry is the study of shapes, sizes and space.

A triangle has 3 sides.
A rectangle has 4 sides.
A square has 4 equal sides.

The perimeter is the distance around a shape.""",
        "example": "A square with sides of 5 cm has a perimeter of 5 + 5 + 5 + 5 = 20 cm.",
        "question": "What is the perimeter of a square with sides of 4 cm?",
        "answer": "16 cm",
        "hint": "Add all four equal sides."
    }
},

"English": {
    "Grammar": {
        "goal": "Understand how words work together to form correct sentences.",
        "learn": """Grammar is the set of rules we use to communicate clearly.

A sentence normally begins with a capital letter and ends with punctuation.

Example:
The boy is reading a book.""",
        "example": "Incorrect: the boy is reading. Correct: The boy is reading.",
        "question": "Rewrite correctly: the girl is playing.",
        "answer": "The girl is playing.",
        "hint": "Start the sentence with a capital letter."
    },

    "Tenses": {
        "goal": "Understand past, present and future tense.",
        "learn": """Tense tells us when an action happens.

Present: I play.
Past: I played.
Future: I will play.

The verb changes to show the time.""",
        "example": "Present: She walks. Past: She walked.",
        "question": "Change this to past tense: 'He plays football.'",
        "answer": "He played football.",
        "hint": "Change 'plays' to its past form."
    },

    "Sentence Construction": {
        "goal": "Build clear and complete sentences.",
        "learn": """A complete sentence expresses a complete thought.

A simple sentence can contain:
Subject + Verb + Object.

Example:
Tinashe reads books.

Tinashe = subject
reads = verb
books = object""",
        "example": "The teacher explains the lesson.",
        "question": "Construct a sentence using the word 'school'.",
        "answer": "school",
        "hint": "Write a complete sentence containing the word school."
    },

    "Comprehension": {
        "goal": "Learn how to understand and answer questions about a passage.",
        "learn": """When answering comprehension questions:

1. Read the passage carefully.
2. Identify the important information.
3. Look at exactly what the question asks.
4. Answer using information from the passage.
5. Check your answer before submitting.""",
        "example": "If a passage says John went to school on Monday, the answer to 'When did John go to school?' is Monday.",
        "question": "What should you do first when answering a comprehension passage?",
        "answer": "read",
        "hint": "You need to understand the passage before answering."
    }
},

"Science": {
    "Human Body": {
        "goal": "Understand major parts and systems of the human body.",
        "learn": """The human body contains many organs that work together.

The heart pumps blood.
The lungs help us breathe.
The stomach helps digest food.
The brain controls many body activities.""",
        "example": "The lungs take oxygen into the body.",
        "question": "Which organ pumps blood around the body?",
        "answer": "heart",
        "hint": "It is a muscular organ in your chest."
    },

    "Plants": {
        "goal": "Understand how plants grow and make food.",
        "learn": """Plants need water, light, air and suitable conditions to grow.

Green plants make their own food through photosynthesis.

Roots absorb water and minerals from the soil.""",
        "example": "Roots absorb water while leaves receive sunlight.",
        "question": "Which part of a plant usually absorbs water from the soil?",
        "answer": "roots",
        "hint": "They are normally below the ground."
    },

    "Forces": {
        "goal": "Understand what a force is.",
        "learn": """A force is a push or a pull.

Forces can change the movement, direction or shape of an object.

Examples include pushing a door and pulling a box.""",
        "example": "Kicking a football applies a force to the ball.",
        "question": "Is a push a force?",
        "answer": "yes",
        "hint": "A force can be a push or a pull."
    },

    "Matter": {
        "goal": "Understand the basic states of matter.",
        "learn": """Matter is anything that has mass and takes up space.

The three common states are:
Solid
Liquid
Gas

Ice is a solid.
Water is a liquid.
Water vapour is a gas.""",
        "example": "When ice melts, it changes from solid to liquid.",
        "question": "What are the three common states of matter?",
        "answer": "solid liquid gas",
        "hint": "Think about ice, water and water vapour."
    }
},

"Biology": {
    "Cells": {
        "goal": "Understand the cell as the basic unit of life.",
        "learn": """A cell is the basic structural and functional unit of living organisms.

Plant and animal cells have some structures in common.

The nucleus contains genetic material and helps control cell activities.""",
        "example": "Many cells working together form tissues.",
        "question": "What is the basic unit of life?",
        "answer": "cell",
        "hint": "It is the smallest basic unit of a living organism."
    },

    "Photosynthesis": {
        "goal": "Understand how green plants make food.",
        "learn": """Photosynthesis is the process by which green plants make food.

Plants use:
• sunlight
• carbon dioxide
• water

Chlorophyll helps absorb light energy.

Oxygen is released as a product.""",
        "example": "Leaves contain chlorophyll which captures light energy.",
        "question": "What process do green plants use to make food?",
        "answer": "photosynthesis",
        "hint": "It starts with 'photo'."
    },

    "Respiration": {
        "goal": "Understand respiration and energy release.",
        "learn": """Respiration is a process that releases energy from food.

Aerobic respiration uses oxygen.

The energy released is used by cells for activities such as growth, movement and repair.""",
        "example": "During exercise, cells need energy to support muscle movement.",
        "question": "What does respiration release from food?",
        "answer": "energy",
        "hint": "Your cells need it to perform activities."
    }
},

"Chemistry": {
    "Atoms": {
        "goal": "Understand the basic idea of atoms.",
        "learn": """Everything around us is made from matter.

Atoms are very small units that make up elements.

An atom contains particles such as protons, neutrons and electrons.""",
        "example": "A piece of iron consists of enormous numbers of iron atoms.",
        "question": "What are the tiny units that make up elements?",
        "answer": "atoms",
        "hint": "The singular form is atom."
    },

    "Elements": {
        "goal": "Understand what a chemical element is.",
        "learn": """An element is a pure substance made from only one type of atom.

Examples include:
Hydrogen
Oxygen
Carbon
Iron

Each element has its own chemical symbol.""",
        "example": "O is the chemical symbol for oxygen.",
        "question": "What is the chemical symbol for oxygen?",
        "answer": "O",
        "hint": "It is one capital letter."
    },

    "Chemical Symbols": {
        "goal": "Learn common chemical symbols.",
        "learn": """Chemical symbols are short ways of representing elements.

Some examples:

H = Hydrogen
O = Oxygen
C = Carbon
N = Nitrogen
Na = Sodium
Cl = Chlorine
Fe = Iron""",
        "example": "H₂O contains hydrogen and oxygen.",
        "question": "What is the symbol for carbon?",
        "answer": "C",
        "hint": "It is the first letter of Carbon."
    },

    "Acids": {
        "goal": "Understand the basic idea of acids and indicators.",
        "learn": """Acids are substances with acidic properties.

The pH scale is used to describe how acidic or alkaline a solution is.

A pH below 7 is acidic.
A pH of 7 is neutral.
A pH above 7 is alkaline.""",
        "example": "Lemon juice is acidic.",
        "question": "What pH is neutral?",
        "answer": "7",
        "hint": "It is between acidic and alkaline."
    }
},

"Physics": {
    "Forces": {
        "goal": "Understand forces and their effects.",
        "learn": """A force is a push or pull.

Forces can cause an object to:
• speed up
• slow down
• change direction
• change shape

Gravity is a force that attracts objects towards Earth.""",
        "example": "A football changes direction when a player kicks it.",
        "question": "What force pulls objects towards Earth?",
        "answer": "gravity",
        "hint": "It keeps us on the ground."
    },

    "Energy": {
        "goal": "Understand different forms of energy.",
        "learn": """Energy is needed to make things happen.

Forms of energy include:
• kinetic
• potential
• thermal
• chemical
• electrical
• light

Energy can be transferred from one form to another.""",
        "example": "An electric bulb changes electrical energy into light and thermal energy.",
        "question": "What type of energy is stored in food?",
        "answer": "chemical energy",
        "hint": "It is stored in chemical bonds."
    },

    "Electricity": {
        "goal": "Understand simple electric circuits.",
        "learn": """An electric circuit provides a path through which electric current can flow.

A simple circuit can contain:
• a cell
• wires
• a switch
• a bulb

A complete circuit allows current to flow.""",
        "example": "Closing the switch can complete the circuit and light the bulb.",
        "question": "What must a circuit have for current to flow?",
        "answer": "complete circuit",
        "hint": "The path must not be broken."
    },

    "Motion": {
        "goal": "Understand movement and speed.",
        "learn": """Motion describes a change in position.

Speed tells us how quickly an object moves.

Speed = distance ÷ time.""",
        "example": "If a car travels 100 km in 2 hours, its average speed is 50 km/h.",
        "question": "What is the formula for speed?",
        "answer": "distance divided by time",
        "hint": "Think about distance and time."
    }
},

"Geography": {
    "Map Skills": {
        "goal": "Learn how maps represent places.",
        "learn": """Maps represent places and features of the Earth's surface.

Important map skills include:
• direction
• scale
• symbols
• grid references
• interpreting features

A compass can help identify direction.""",
        "example": "North, South, East and West are the four main compass directions.",
        "question": "Name the four main compass directions.",
        "answer": "north south east west",
        "hint": "They are the four basic points of a compass."
    },

    "Weather": {
        "goal": "Understand the difference between weather and climate.",
        "learn": """Weather describes atmospheric conditions over a short period.

Examples include:
temperature
rainfall
wind
cloud cover

Climate describes the usual weather conditions of an area over a much longer period.""",
        "example": "Today's rainfall is weather. The long-term rainfall pattern is climate.",
        "question": "What describes atmospheric conditions over a short period?",
        "answer": "weather",
        "hint": "It changes from day to day."
    }
},

"History": {
    "Historical Sources": {
        "goal": "Understand how historians learn about the past.",
        "learn": """Historians use evidence to learn about the past.

Sources can include:
• written records
• photographs
• artefacts
• oral accounts
• buildings
• maps

Primary sources come directly from the period being studied.""",
        "example": "An old letter written during a historical event can be a primary source.",
        "question": "What do historians use to learn about the past?",
        "answer": "evidence",
        "hint": "Sources provide this."
    },

    "Chronology": {
        "goal": "Understand the order in which historical events happened.",
        "learn": """Chronology means arranging events in the order in which they happened.

Dates help historians understand the sequence of events.

A timeline is a useful way to display chronology.""",
        "example": "If Event A happened in 1900 and Event B in 1910, Event A came first.",
        "question": "What does chronology mean?",
        "answer": "order of events",
        "hint": "Think about putting events in the correct sequence."
    }
},

"Economics": {
    "Scarcity": {
        "goal": "Understand why resources must be used carefully.",
        "learn": """Scarcity exists because resources are limited while human wants are unlimited.

Because resources are scarce, people have to make choices.

Every choice can involve an opportunity cost.""",
        "example": "If you spend money on a book, you may not have that money available for another purchase.",
        "question": "Why do people have to make choices?",
        "answer": "resources are limited",
        "hint": "Think about scarcity."
    },

    "Supply and Demand": {
        "goal": "Understand the basic relationship between supply and demand.",
        "learn": """Supply refers to the amount producers are willing and able to sell.

Demand refers to the amount consumers are willing and able to buy.

Prices can be affected by changes in supply and demand.""",
        "example": "If demand increases while supply stays limited, prices may rise.",
        "question": "What does demand refer to?",
        "answer": "amount consumers are willing and able to buy",
        "hint": "Think about buyers."
    }
},

"Accounting": {
    "Assets and Liabilities": {
        "goal": "Understand basic accounting terms.",
        "learn": """An asset is something valuable owned by a business.

Examples include:
cash
equipment
buildings
inventory

A liability is an amount owed by a business.

Examples include loans and amounts owed to suppliers.""",
        "example": "Cash is an asset. A bank loan is a liability.",
        "question": "What is something valuable owned by a business called?",
        "answer": "asset",
        "hint": "Cash and equipment are examples."
    },

    "Accounting Equation": {
        "goal": "Understand the basic accounting equation.",
        "learn": """The basic accounting equation is:

ASSETS = CAPITAL + LIABILITIES

This relationship is fundamental to accounting.

If one part changes, the other parts must remain balanced.""",
        "example": "If assets are $10 000 and liabilities are $4 000, capital is $6 000.",
        "question": "Complete the equation: Assets = Capital + ______",
        "answer": "liabilities",
        "hint": "It is money owed by the business."
    }
},

"Social Studies": {
    "Family and Community": {
        "goal": "Understand the importance of families and communities.",
        "learn": """A family is a group of people connected through relationships and responsibilities.

A community is a group of people living or working in the same area or sharing common interests.

People in communities have rights and responsibilities.""",
        "example": "Keeping the community clean is a responsibility shared by community members.",
        "question": "What do we call people living or working together in an area?",
        "answer": "community",
        "hint": "It begins with 'community'."
    },

    "Citizenship": {
        "goal": "Understand responsible citizenship.",
        "learn": """A responsible citizen respects other people, follows laws, protects the environment and participates positively in society.

Citizens have both rights and responsibilities.""",
        "example": "Respecting public property is responsible citizenship.",
        "question": "Name one responsibility of a good citizen.",
        "answer": "respect laws",
        "hint": "Following laws is one example."
    }
}
}


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS playbook_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            mastery REAL DEFAULT 0,
            last_activity TEXT
        )
    """)

    conn.commit()
    conn.close()


def student(sid):
    conn = db()
    row = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    conn.close()
    return row


def topics_for(subject):
    if subject in PLAYBOOK:
        return list(PLAYBOOK[subject].keys())
    return []


def get_playbook_question(sid, subject, topic):
    """
    Return the current grade/form-appropriate Playbook question.

    CURRICULUM_EXPANSION stores questions as:
        (subject, topic) -> {band: lesson}

    The student's learning band determines which lesson/question
    bank is used.
    """
    lesson = PLAYBOOK.get(subject, {}).get(topic)
    if not lesson:
        return None

    try:
        conn = db()
        row = conn.execute("""
            SELECT question_index
            FROM playbook_progress
            WHERE student_id=? AND subject=? AND topic=?
        """, (sid, subject, topic)).fetchone()
        conn.close()
    except Exception:
        row = None

    question_index = int(row["question_index"]) if row else 0

    try:
        from student_learning import get_student_learning_band
        from curriculum_expansion import CURRICULUM_EXPANSION

        band = get_student_learning_band(sid)

        # CURRICULUM_EXPANSION uses:
        # (subject, topic) -> {band: lesson}
        curriculum_by_band = CURRICULUM_EXPANSION.get(
            (subject, topic),
            {}
        )

        curriculum = curriculum_by_band.get(band)

        if curriculum:
            questions = curriculum.get("practice", [])

            if questions:
                index = question_index % len(questions)
                q = questions[index]

                result = dict(lesson)
                result["question"] = q.get("question", "")
                result["answer"] = (
                    q.get("answers", [""])[0]
                    if q.get("answers")
                    else ""
                )
                result["_answers"] = list(q.get("answers", []))
                result["_question_index"] = index
                result["_question_count"] = len(questions)
                result["_learning_band"] = band
                result["_curriculum"] = True

                return result

    except Exception:
        pass

    # Compatibility fallback for older Playbook topics that do not
    # yet have a curriculum question bank.
    result = dict(lesson)
    result["_answers"] = [lesson.get("answer", "")]
    result["_question_index"] = 0
    result["_question_count"] = 1
    return result

def update_progress(sid, subject, topic, correct):
    conn = db()

    row = conn.execute("""
        SELECT * FROM playbook_progress
        WHERE student_id=? AND subject=? AND topic=?
    """, (sid, subject, topic)).fetchone()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Find the number of curriculum questions for this student's
    # grade/form band so Playbook can rotate through them.
    question_count = 1
    try:
        from student_learning import get_student_learning_band
        from curriculum_expansion import CURRICULUM_EXPANSION

        band = get_student_learning_band(sid)

        # CURRICULUM_EXPANSION uses:
        # (subject, topic) -> {band: lesson}
        curriculum_by_band = CURRICULUM_EXPANSION.get(
            (subject, topic),
            {}
        )

        curriculum = curriculum_by_band.get(band)

        if curriculum:
            questions = curriculum.get("practice", [])
            if questions:
                question_count = len(questions)
    except Exception:
        question_count = 1

    if row:
        attempts = row["attempts"] + 1
        total_correct = row["correct"] + (1 if correct else 0)
        mastery = round((total_correct / attempts) * 100, 1)

        current_index = int(row["question_index"] or 0)
        next_index = (current_index + 1) % max(1, question_count)

        conn.execute("""
            UPDATE playbook_progress
            SET attempts=?,
                correct=?,
                mastery=?,
                last_activity=?,
                question_index=?
            WHERE id=?
        """, (
            attempts,
            total_correct,
            mastery,
            now,
            next_index,
            row["id"]
        ))
    else:
        attempts = 1
        total_correct = 1 if correct else 0
        mastery = 100 if correct else 0

        next_index = 1 % max(1, question_count)

        conn.execute("""
            INSERT INTO playbook_progress
            (student_id, subject, topic, attempts, correct, mastery,
             last_activity, question_index)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sid,
            subject,
            topic,
            attempts,
            total_correct,
            mastery,
            now,
            next_index
        ))

    conn.commit()
    conn.close()

def normalize(value):
    return " ".join(
        str(value).lower()
        .replace(".", "")
        .replace(",", "")
        .replace("?", "")
        .replace("!", "")
        .strip()
        .split()
    )


def answer_correct(student_answer, correct_answer):
    a = normalize(student_answer)
    b = normalize(correct_answer)

    if not a:
        return False

    if a == b:
        return True

    # Accept useful longer answers containing the key answer.
    if b in a and len(b) > 2:
        return True

    # Common equivalent answers.
    equivalents = {
        "3/5": ["3 / 5"],
        "0.8": [".8"],
        "42": ["forty two"],
        "7": ["seven"],
        "8": ["eight"],
        "4": ["four"],
        "16 cm": ["16cm"],
        "heart": ["the heart"],
        "roots": ["the roots"],
        "yes": ["yes it is", "yes"],
        "cell": ["a cell", "the cell"],
        "photosynthesis": ["the process of photosynthesis"],
        "energy": ["release energy", "energy"],
        "atoms": ["atom", "atoms"],
        "gravity": ["force of gravity", "gravity"],
        "asset": ["an asset", "assets"],
        "liabilities": ["liability", "liabilities"]
    }

    for key, values in equivalents.items():
        if b == key and a in values:
            return True

    return False




def _filter_topics_for_trial(subject, topics_list, trial_active, paid_active):
    """During trial (not paid), only show first N topics per subject."""
    if paid_active:
        return topics_list  # full access
    if trial_active:
        return topics_list[:RESTRICTED_TRIAL_TOPICS_PER_SUBJECT]
    return []  # neither trial nor paid → nothing

def register_student_playbook(app):

    ensure_tables()

    @app.route("/student/<int:sid>/playbook")
    def playbook_home(sid):
        s = student(sid)

        if not s:
            return "Student not found", 404

        # ====================================================
        # LEARNING ACCESS GATE
        # ====================================================
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row
        trial = conn.execute("SELECT * FROM student_sessions WHERE student_id=? AND session_type='trial' AND completed=0 ORDER BY id DESC LIMIT 1",(sid,)).fetchone()
        conn.close()
        if trial:
            if bool(trial["paused"]):
                trial_active = True
            else:
                trial_active = datetime.now() < datetime.fromisoformat(trial["expires_at"])
        else:
            trial_active = False
        try:
            from paid_access import active_paid_session
            paid = active_paid_session(sid)
        except Exception:
            paid = None
        print("PLAYBOOK DEBUG:", "trial=", bool(trial), "trial_active=", trial_active, "paid=", bool(paid))
        if not trial_active and not paid:
            return redirect(f"/student/{sid}/paid")

        html = """
        <!doctype html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Lesson Playbook</title>
        <style>
        body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
        .top{background:#172554;color:white;padding:20px}
        .wrap{max-width:850px;margin:auto;padding:18px}
        .card{background:white;padding:18px;margin:12px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
        a{display:block;text-decoration:none}
        .subject{font-size:19px;font-weight:bold;color:#172554;margin-bottom:12px}
        .topic{background:#eef4ff;padding:14px;border-radius:12px;margin:8px 0;color:#172554}
        .back{background:#222;color:white;padding:12px;border-radius:10px;text-align:center;margin-bottom:15px}
        </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:24px;font-weight:bold;">📚 Lesson Playbook</div>
            <div>Learn step by step, practise and build mastery.</div>
        </div>

        <div class="wrap">

        {% if trial_active and not paid_active %}
        <div class="card" style="background:#fff3cd;border-left:6px solid #f0ad4e;padding:20px;">
            <div style="font-size:22px;font-weight:bold;color:#8a6d3b;margin-bottom:10px;">
                🎁 You Are On The FREE TRIAL
            </div>
            <div style="font-size:15px;color:#66512c;line-height:1.6;">
                <p><strong>Here's what you get during your free trial:</strong></p>
                <ul style="margin-left:20px;">
                    <li>⏱️ <strong>30 minutes</strong> of learning time</li>
                    <li>📚 Access to the <strong>first {{ R }} topics</strong> in every subject</li>
                    <li>✍️ Practice questions and instant feedback</li>
                    <li>📊 Progress tracking</li>
                </ul>
                <p style="margin-top:12px;"><strong>Want the FULL experience?</strong></p>
                <ul style="margin-left:20px;">
                    <li>✅ <strong>ALL topics</strong> in every subject</li>
                    <li>⏱️ <strong>60 minutes</strong> per paid session</li>
                    <li>📝 Full homework, tests and exams</li>
                    <li>🎓 Exam-focused tutoring</li>
                </ul>
                <p style="margin-top:12px;font-size:16px;">
                    💰 <strong>Just $1 to unlock everything for 1 hour.</strong>
                </p>
                <a href="/student/{{s['id']}}/paid" 
                   style="display:inline-block;background:#172554;color:white;padding:12px 24px;border-radius:10px;text-decoration:none;margin-top:10px;font-weight:bold;">
                    💳 Unlock Full Access for $1
                </a>
            </div>
        </div>
        {% endif %}

        {% if paid_active %}
        <div class="card" style="background:#d4edda;border-left:6px solid #28a745;padding:16px;">
            <div style="font-size:18px;font-weight:bold;color:#155724;">
                ✅ FULL ACCESS UNLOCKED
            </div>
            <div style="color:#155724;margin-top:6px;">
                You have access to <strong>ALL topics</strong> in every subject. 
                Your paid session is active. Let's learn! 🚀
            </div>
        </div>
        {% endif %}


        <a class="back" href="/student/{{s['id']}}/home">← Back to Learning Centre</a>

        <div class="card">
            <h2>👋 {{s['name']}}'s Lessons</h2>
            <p>Choose a subject, then choose a topic.</p>
        </div>

        {% for subject in subjects %}
            <div class="card">
                <div class="subject">📘 {{subject}}</div>

                {% for topic in _filter_topics_for_trial(subject, topics(subject), trial_active, paid_active) %}
                    <a class="topic"
                       href="/student/{{s['id']}}/playbook/{{subject|urlencode}}/{{topic|urlencode}}">
                       📖 {{topic}}
                    </a>
                {% endfor %}
            </div>
        {% endfor %}


        <div class="card" style="text-align:center;background:#eef4ff;padding:16px;">
            <strong>❓ Need help understanding the free trial?</strong><br>
            <span style="font-size:14px;color:#4a5a6a;">
                Free trial = 30 min + first {{ R }} topics per subject.<br>
                Paid session = 60 min + ALL topics. Just $1.
            </span>
        </div>
        </div>

        </div>
        </body>
        </html>
        """

        return render_template_string(
            html,
            s=s,
            subjects=SUBJECTS,
            topics=topics_for,
            trial_active=trial_active,
            paid_active=bool(paid),
            R=RESTRICTED_TRIAL_TOPICS_PER_SUBJECT
        )


    @app.route("/student/<int:sid>/playbook/<subject>/<topic>")
    def playbook_lesson(sid, subject, topic):
        s = student(sid)

        if not s:
            return "Student not found", 404

        # ====================================================
        # PLAYBOOK ACCESS GATE
        # Active/paused free trial OR paid session may access lessons.
        # ====================================================
        try:
            from paid_access import active_paid_session
            paid = active_paid_session(sid)
        except Exception:
            paid = None

        trial_active = False
        try:
            conn = db()
            trial_row = conn.execute("""
                SELECT paused, expires_at
                FROM student_sessions
                WHERE student_id=?
                  AND session_type='trial'
                  AND completed=0
                ORDER BY id DESC
                LIMIT 1
            """, (sid,)).fetchone()
            conn.close()

            # A paused trial remains alive, but it must NOT allow
            # answers until the student resumes the lesson.
            if trial_row and not trial_row["paused"]:
                from datetime import datetime
                try:
                    trial_active = datetime.now() < datetime.fromisoformat(
                        trial_row["expires_at"]
                    )
                except Exception:
                    trial_active = False
        except Exception:
            trial_active = False

        # A paused paid lesson is also not allowed to submit answers.
        paid_active = bool(paid) and not bool(paid["paused"])

        if not paid_active and not trial_active:
            return redirect(f"/student/{sid}/paid")

        # The lesson timer/template must use the actual active session.
        # During the free trial, paid is None, so use trial_row instead.
        lesson_session = paid if paid else trial_row
        is_trial_lesson = paid is None and trial_active

        lesson = get_playbook_question(sid, subject, topic)

        if not lesson:
            return "Lesson not found", 404

        conn = db()
        progress = conn.execute("""
            SELECT * FROM playbook_progress
            WHERE student_id=? AND subject=? AND topic=?
        """, (sid, subject, topic)).fetchone()
        conn.close()

        mastery = progress["mastery"] if progress else 0

        html = """
        <!doctype html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>{{topic}} - Lesson</title>
        <style>
        body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
        .top{background:#172554;color:white;padding:20px}
        .wrap{max-width:800px;margin:auto;padding:18px}
        .card{background:white;padding:20px;margin:14px 0;border-radius:17px;box-shadow:0 3px 12px #0001}
        .goal{background:#fff7d6;padding:15px;border-radius:12px}
        .example{background:#eaf7ee;padding:15px;border-radius:12px}
        .question{background:#eef4ff;padding:18px;border-radius:12px}
        textarea{width:100%;box-sizing:border-box;padding:13px;border:1px solid #bbb;border-radius:10px;font-size:16px}
        button{width:100%;padding:14px;border:0;border-radius:11px;background:#172554;color:white;font-size:16px;margin-top:10px}
        .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none}
        .mastery{font-size:18px;font-weight:bold}

        .timer-card{
            background:#172554;
            color:white;
            padding:18px;
            margin:14px 0;
            border-radius:17px;
            box-shadow:0 3px 12px #0002;
            text-align:center;
        }

        .timer-title{
            font-size:15px;
            opacity:.9;
            margin-bottom:6px;
        }

        .timer{
            font-size:32px;
            font-weight:bold;
            letter-spacing:1px;
            margin:6px 0 12px;
        }

        .timer-paused{
            font-size:22px;
            font-weight:bold;
            margin:8px 0 12px;
        }

        .timer-btn{
            display:block;
            width:100%;
            box-sizing:border-box;
            padding:13px;
            border:0;
            border-radius:11px;
            background:white;
            color:#172554;
            font-size:16px;
            font-weight:bold;
            text-decoration:none;
        }

        .timer-note{
            font-size:13px;
            margin-top:10px;
            opacity:.85;
        }
        </style>
        </head>

        <body>

        <div class="top">
            <div style="font-size:23px;font-weight:bold;">📖 {{subject}}</div>
            <div>{{topic}}</div>
        </div>

        <div class="wrap">

        <!-- LESSON SESSION TIMER -->
        <div class="timer-card">

            {% if lesson_session['paused'] %}

                <div class="timer-title">
                    {% if is_trial_lesson %}Your Free Trial Lesson{% else %}Your Paid Lesson{% endif %}
                </div>

                <div class="timer-paused">⏸️ LESSON PAUSED</div>

                {% if is_trial_lesson %}
                <a class="timer-btn"
                   href="/student/{{s['id']}}/resume-trial?next=/student/{{s['id']}}/playbook/{{subject}}/{{topic}}">
                    ▶️ RESUME LESSON
                </a>
                {% else %}
                <a class="timer-btn"
                   href="/student/{{s['id']}}/resume-paid?next=/student/{{s['id']}}/playbook/{{subject}}/{{topic}}">
                    ▶️ RESUME LESSON
                </a>
                {% endif %}

                <div class="timer-note">
                    Your remaining lesson time is protected while paused.
                </div>

            {% else %}

                <div class="timer-title">
                    {% if is_trial_lesson %}Your Free Trial Lesson — Time Remaining{% else %}Your Paid Lesson — Time Remaining{% endif %}
                </div>

                <div class="timer" id="lessonTimer">--:--:--</div>

                {% if is_trial_lesson %}
                <a class="timer-btn"
                   href="/student/{{s['id']}}/pause-trial?next=/student/{{s['id']}}/playbook/{{subject}}/{{topic}}">
                    ⏸️ PAUSE LESSON
                </a>
                {% else %}
                <a class="timer-btn"
                   href="/student/{{s['id']}}/pause-paid?next=/student/{{s['id']}}/playbook/{{subject}}/{{topic}}">
                    ⏸️ PAUSE LESSON
                </a>
                {% endif %}

                <div class="timer-note">
                    Changing subjects or topics does not reset your timer.
                </div>

            {% endif %}

        </div>

        <a class="back" href="/student/{{s['id']}}/playbook">← All Lessons</a>

        <div class="card">
            <h1>🎯 {{topic}}</h1>
            <div class="goal">
                <b>Lesson Goal</b><br><br>
                {{lesson['goal']}}
            </div>
        </div>

        <div class="card">
            <h2>🧑‍🏫 Learn</h2>
            <div style="white-space:pre-line;line-height:1.7;">
                {{lesson['learn']}}
            </div>
        </div>

        <div class="card example">
            <h2>💡 Worked Example</h2>
            <div style="white-space:pre-line;line-height:1.7;">
                {{lesson['example']}}
            </div>
        </div>

        <div class="card">
            <h2>✏️ Your Turn</h2>

            <div class="question">
                <b>{{lesson['question']}}</b>
            </div>

            <form method="post"
                  action="/student/{{s['id']}}/playbook-answer">
                <input type="hidden" name="subject" value="{{subject}}">
                <input type="hidden" name="topic" value="{{topic}}">

                <textarea name="answer"
                          rows="4"
                          placeholder="Write your answer here..."></textarea>

                <button type="submit">✅ Submit Answer</button>
            </form>
        </div>

        <div class="card">
            <div class="mastery">📊 Topic Mastery: {{mastery}}%</div>
            <p>Keep practising. Your mastery improves as you answer questions correctly.</p>
        </div>

        {% if not lesson_session['paused'] %}

        <script>
        (function(){

            const expiresAt = new Date("{{ lesson_session['expires_at'] }}").getTime();
            const timer = document.getElementById("lessonTimer");

            function updateTimer(){

                if (!timer) return;

                const now = new Date().getTime();
                let remaining = Math.floor((expiresAt - now) / 1000);

                if (remaining <= 0){
                    timer.textContent = "00:00:00";

                    {% if is_trial_lesson %}
                    window.location.href = "/student/{{s['id']}}/trial";
                    {% else %}
                    window.location.href = "/student/{{s['id']}}/paid";
                    {% endif %}

                    return;
                }

                const hours = Math.floor(remaining / 3600);
                remaining %= 3600;

                const minutes = Math.floor(remaining / 60);
                const seconds = remaining % 60;

                timer.textContent =
                    String(hours).padStart(2,"0") + ":" +
                    String(minutes).padStart(2,"0") + ":" +
                    String(seconds).padStart(2,"0");
            }

            updateTimer();
            setInterval(updateTimer, 1000);

        })();
        </script>

        {% endif %}

        </div>
        </body>
        </html>
        """

        return render_template_string(
            html,
            s=s,
            subject=subject,
            topic=topic,
            lesson=lesson,
            mastery=mastery,
            paid=paid,
            lesson_session=lesson_session,
            is_trial_lesson=is_trial_lesson
        )


    @app.route("/student/<int:sid>/playbook-answer", methods=["POST"])
    def playbook_answer(sid):
        s = student(sid)

        if not s:
            return "Student not found", 404

        # ====================================================
        # PLAYBOOK ANSWER ACCESS GATE
        # Active free trial OR active paid session may submit.
        # Paused sessions cannot submit answers.
        # ====================================================
        try:
            from paid_access import active_paid_session
            paid = active_paid_session(sid)
        except Exception:
            paid = None

        paid_active = bool(paid) and not bool(paid["paused"])
        trial_active = False

        try:
            conn = db()
            trial_row = conn.execute("""
                SELECT paused, expires_at
                FROM student_sessions
                WHERE student_id=?
                  AND session_type='trial'
                  AND completed=0
                ORDER BY id DESC
                LIMIT 1
            """, (sid,)).fetchone()
            conn.close()

            if trial_row and not bool(trial_row["paused"]):
                from datetime import datetime
                try:
                    trial_active = (
                        datetime.now()
                        < datetime.fromisoformat(trial_row["expires_at"])
                    )
                except Exception:
                    trial_active = False
        except Exception:
            trial_active = False

        if not paid_active and not trial_active:
            return redirect(f"/student/{sid}/paid")

        subject = request.form.get("subject", "").strip()
        topic = request.form.get("topic", "").strip()
        answer = request.form.get("answer", "").strip()

        lesson = get_playbook_question(sid, subject, topic)

        if not lesson:
            return "Lesson not found", 404

        accepted_answers = lesson.get("_answers", [])

        if accepted_answers:
            correct = any(
                answer_correct(answer, expected)
                for expected in accepted_answers
            )
        else:
            correct = answer_correct(
                answer,
                lesson.get("answer", "")
            )

        # Records the result and advances exactly one question.
        update_progress(
            sid,
            subject,
            topic,
            correct
        )

        if correct:
            title = "🎉 Excellent!"
            message = "That's correct! You are building mastery of this topic."
            extra = "Your next question is ready."
        else:
            title = "💪 Keep Going!"
            message = "Not quite yet. That's okay — mistakes are part of learning."
            extra = "Your next question is ready. Keep practising."

        # Get the question that follows the submitted question.
        next_lesson = get_playbook_question(sid, subject, topic)

        html = """
        <!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <style>
            body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
            .wrap{max-width:700px;margin:auto;padding:20px}
            .card{background:white;padding:22px;border-radius:18px;
                  box-shadow:0 3px 12px #0001;margin-top:20px}
            .correct{background:#eaf7ee;padding:16px;border-radius:12px}
            .wrong{background:#fff1f1;padding:16px;border-radius:12px}
            a{display:block;text-align:center;text-decoration:none;
              padding:14px;border-radius:11px;margin-top:10px;
              background:#172554;color:white}
            .answer{background:#eef4ff;padding:15px;
                    border-radius:12px;margin-top:12px}
            .next{background:#f0f4ff;padding:16px;border-radius:12px;
                  margin-top:15px}
            </style>
        </head>
        <body>
        <div class="wrap">
        <div class="card">

            <h1>{{title}}</h1>

            <div class="{{'correct' if correct else 'wrong'}}">
                <b>{{message}}</b>
                <p>{{extra}}</p>
            </div>

            <div class="answer">
                <b>Correct answer:</b><br><br>
                {{lesson['answer']}}
                <br><br>
                <b>💡 Hint:</b><br>
                {{lesson['hint']}}
            </div>

            {% if next_lesson %}
            <div class="next">
                <b>➡️ Next Question</b><br><br>
                {{next_lesson['question']}}
            </div>
            {% endif %}

            <a href="/student/{{sid}}/playbook/{{subject|urlencode}}/{{topic|urlencode}}">
                ➡️ Continue
            </a>

            <a href="/student/{{sid}}/playbook">
                📚 More Lessons
            </a>

            <a href="/student/{{sid}}/home">
                🏠 Home
            </a>

        </div>
        </div>
        </body>
        </html>
        """

        return render_template_string(
            html,
            sid=sid,
            subject=subject,
            topic=topic,
            lesson=lesson,
            next_lesson=next_lesson,
            correct=correct,
            title=title,
            message=message,
            extra=extra
        )


# Compatibility name
register_playbook = register_student_playbook
