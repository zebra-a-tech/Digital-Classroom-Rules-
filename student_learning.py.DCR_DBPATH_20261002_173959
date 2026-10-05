from flask import render_template_string, request, redirect, url_for
import sqlite3
import random
from datetime import datetime

DB = "digital_classroom.db"

SUBJECT_TOPICS = {
    "Maths": [
        "Whole Numbers", "Fractions", "Decimals", "Percentages",
        "Ratio", "Algebra", "Multiplication", "Division",
        "Equations", "Geometry", "Measurement", "Statistics"
    ],
    "English": [
        "Grammar", "Tenses", "Sentence Construction", "Parts of Speech",
        "Comprehension", "Vocabulary", "Writing"
    ],
    "Science": [
        "Human Body", "Plants", "Forces", "Matter", "Energy",
        "Electricity", "Living Things"
    ],
    "Biology": [
        "Cells", "Photosynthesis", "Respiration", "Human Body",
        "Nutrition", "Reproduction", "Ecology"
    ],
    "Chemistry": [
        "Atoms", "Elements", "Chemical Symbols", "Acids and Bases",
        "Mixtures", "Chemical Reactions"
    ],
    "Physics": [
        "Forces", "Energy", "Electricity", "Motion",
        "Light", "Sound", "Pressure"
    ],
    "Geography": [
        "Maps", "Weather", "Climate", "Rivers",
        "Population", "Natural Resources"
    ],
    "History": [
        "Early Civilisations", "Colonial History",
        "Zimbabwe History", "African History",
        "World Wars"
    ],
    "Economics": [
        "Needs and Wants", "Scarcity", "Demand and Supply",
        "Markets", "Production", "Inflation"
    ],
    "Accounting": [
        "Accounting Basics", "Assets and Liabilities",
        "Cash Book", "Journals", "Ledgers", "Trial Balance"
    ],
    "Social Studies": [
        "Family", "Community", "Citizenship",
        "Culture", "Environment", "Human Rights"
    ]
}

QUESTION_BANK = {
    ("Maths", "Whole Numbers"): [
        {
            "question": "What is 25 + 15?",
            "answers": ["40", "forty"]
        },
        {
            "question": "What is 80 - 35?",
            "answers": ["45", "forty five", "forty-five"]
        },
        {
            "question": "What is 7 x 8?",
            "answers": ["56", "fifty six", "fifty-six"]
        },
        {
            "question": "What is 144 divided by 12?",
            "answers": ["12", "twelve"]
        },
        {
            "question": "What is 300 + 450?",
            "answers": ["750", "seven hundred and fifty", "seven hundred fifty"]
        },
        {
            "question": "What is 1000 - 275?",
            "answers": ["725", "seven hundred and twenty five", "seven hundred twenty five", "seven hundred and twenty-five", "seven hundred twenty-five"]
        },
        {
            "question": "What is 9 x 6?",
            "answers": ["54", "fifty four", "fifty-four"]
        },
        {
            "question": "What is 96 divided by 8?",
            "answers": ["12", "twelve"]
        },
        {
            "question": "Which number is greater: 456 or 465?",
            "answers": ["465", "four hundred and sixty five", "four hundred sixty five", "four hundred and sixty-five", "four hundred sixty-five"]
        },
        {
            "question": "What is the value of the digit 6 in 6,482?",
            "answers": ["6000", "6 000", "six thousand"]
        }
    ]
}

LESSONS = {
    ("Maths", "Whole Numbers"): {
        "goal": "Understand whole numbers and how to add, subtract, multiply and divide them.",
        "learn": "Whole numbers are numbers such as 0, 1, 2, 3, 4 and so on. They do not have fractions or decimal parts.",
        "example": "For example, 25 + 15 = 40. The numbers 25, 15 and 40 are all whole numbers.",
        "question": "What is 25 + 15?",
        "answers": ["40", "forty"]
    },
    ("Maths", "Fractions"): {
        "goal": "Understand what a fraction represents and how to work with simple fractions.",
        "learn": "A fraction shows part of a whole. The top number is the numerator and the bottom number is the denominator.",
        "example": "If a pizza is divided into 4 equal pieces and you eat 3 pieces, you have eaten 3/4 of the pizza.",
        "question": "What fraction represents 2 parts out of 5 equal parts?",
        "answers": ["2/5", "2 / 5"]
    },
    ("Maths", "Decimals"): {
        "goal": "Understand decimal numbers and their relationship with fractions.",
        "learn": "Decimals represent parts of a whole. For example, 0.5 means five tenths, which is equal to 1/2.",
        "example": "0.25 is equal to 25/100, which can be simplified to 1/4.",
        "question": "What is 0.5 written as a fraction?",
        "answers": ["1/2", "1 / 2"]
    },
    ("Maths", "Percentages"): {
        "goal": "Understand percentages as parts out of 100.",
        "learn": "Percent means 'out of 100'. Therefore 25% means 25 out of 100.",
        "example": "50% = 50/100 = 1/2.",
        "question": "What is 25% written as a fraction?",
        "answers": ["1/4", "1 / 4"]
    },
    ("Maths", "Algebra"): {
        "goal": "Understand how letters can represent unknown numbers.",
        "learn": "In algebra, a letter such as x can represent a number we do not yet know.",
        "example": "If x + 3 = 8, then x = 5 because 5 + 3 = 8.",
        "question": "If x + 4 = 10, what is x?",
        "answers": ["6", "six"]
    },
    ("Maths", "Multiplication"): {
        "goal": "Understand multiplication as repeated addition.",
        "learn": "Multiplication is a quick way of adding the same number several times.",
        "example": "3 × 4 means 3 groups of 4, which equals 12.",
        "question": "What is 6 × 4?",
        "answers": ["24", "twenty four", "twenty-four"]
    },
    ("Maths", "Division"): {
        "goal": "Understand division as sharing equally.",
        "learn": "Division means splitting a quantity into equal groups.",
        "example": "12 ÷ 3 = 4 because 12 can be shared into 3 equal groups of 4.",
        "question": "What is 20 ÷ 5?",
        "answers": ["4", "four"]
    },
    ("Maths", "Geometry"): {
        "goal": "Identify common shapes and understand their properties.",
        "learn": "A triangle has 3 sides, while a rectangle has 4 sides.",
        "example": "A square has 4 equal sides and 4 right angles.",
        "question": "How many sides does a triangle have?",
        "answers": ["3", "three"]
    },
    ("English", "Grammar"): {
        "goal": "Understand how words work together to form correct sentences.",
        "learn": "Grammar gives us rules for using words correctly in sentences.",
        "example": "She walks to school. The verb 'walks' agrees with the subject 'She'.",
        "question": "Choose the correct sentence: 'He go to school' or 'He goes to school'.",
        "answers": ["he goes to school"]
    },
    ("English", "Tenses"): {
        "goal": "Understand how verbs show when an action happens.",
        "learn": "Tenses tell us whether an action happened in the past, is happening now, or will happen in the future.",
        "example": "Past: I walked. Present: I walk. Future: I will walk.",
        "question": "Change 'I walk to school' into the past tense.",
        "answers": ["i walked to school"]
    },
    ("English", "Sentence Construction"): {
        "goal": "Build clear and meaningful sentences.",
        "learn": "A sentence normally begins with a capital letter and expresses a complete idea.",
        "example": "The boy kicked the ball.",
        "question": "Construct a sentence using the words: 'girl', 'school', 'walks'.",
        "answers": []
    },
    ("English", "Parts of Speech"): {
        "goal": "Identify common parts of speech.",
        "learn": "A noun names a person, place, animal or thing. A verb shows an action or state.",
        "example": "In 'The dog runs', dog is a noun and runs is a verb.",
        "question": "What is the noun in: 'The teacher writes on the board'?",
        "answers": ["teacher"]
    },
    ("English", "Vocabulary"): {
        "goal": "Improve understanding and use of words.",
        "learn": "Vocabulary is the collection of words that a person understands and uses.",
        "example": "A synonym for 'happy' is 'joyful'.",
        "question": "Give a synonym for 'big'.",
        "answers": ["large", "huge", "enormous", "giant"]
    },
    ("Science", "Human Body"): {
        "goal": "Understand the basic function of important body organs.",
        "learn": "The human body contains organs that perform different jobs. The heart pumps blood around the body.",
        "example": "The lungs help us breathe by taking in oxygen.",
        "question": "Which organ pumps blood around the body?",
        "answers": ["heart"]
    },
    ("Science", "Plants"): {
        "goal": "Understand what plants need to grow.",
        "learn": "Plants need water, light, air and suitable nutrients to grow.",
        "example": "Leaves use sunlight to help the plant make food.",
        "question": "What gas do plants take in during photosynthesis?",
        "answers": ["carbon dioxide", "co2"]
    },
    ("Science", "Forces"): {
        "goal": "Understand what a force is.",
        "learn": "A force is a push or a pull that can change the movement or shape of an object.",
        "example": "Pushing a door is an example of a force.",
        "question": "Is pushing a box a push or a pull?",
        "answers": ["push", "a push"]
    },
    ("Science", "Matter"): {
        "goal": "Understand the three common states of matter.",
        "learn": "The three common states of matter are solid, liquid and gas.",
        "example": "Ice is a solid, water is a liquid, and steam is a gas.",
        "question": "Name the three common states of matter.",
        "answers": ["solid liquid gas", "solid, liquid and gas", "solid liquid and gas"]
    },
    ("Biology", "Cells"): {
        "goal": "Understand that cells are the basic units of living organisms.",
        "learn": "A cell is the basic structural and functional unit of life.",
        "example": "Plants and animals are made up of cells.",
        "question": "What is the basic unit of life?",
        "answers": ["cell", "a cell"]
    },
    ("Biology", "Photosynthesis"): {
        "goal": "Understand how green plants make food.",
        "learn": "Photosynthesis is the process by which green plants use light energy to make food from carbon dioxide and water.",
        "example": "Chlorophyll helps leaves absorb light energy.",
        "question": "What gas do plants use during photosynthesis?",
        "answers": ["carbon dioxide", "co2"]
    },
    ("Biology", "Respiration"): {
        "goal": "Understand respiration as the release of energy from food.",
        "learn": "Respiration releases energy from food so that cells can carry out life processes.",
        "example": "Aerobic respiration uses oxygen to release energy from glucose.",
        "question": "Which gas is used in aerobic respiration?",
        "answers": ["oxygen", "o2"]
    },
    ("Chemistry", "Atoms"): {
        "goal": "Understand what atoms are.",
        "learn": "An atom is the smallest unit of an element that retains the properties of that element.",
        "example": "A piece of iron is made from many iron atoms.",
        "question": "What is the smallest unit of an element?",
        "answers": ["atom", "an atom"]
    },
    ("Chemistry", "Elements"): {
        "goal": "Understand what chemical elements are.",
        "learn": "An element is a pure substance made from only one type of atom.",
        "example": "Gold is an element because it contains only gold atoms.",
        "question": "Is oxygen an element?",
        "answers": ["yes"]
    },
    ("Chemistry", "Chemical Symbols"): {
        "goal": "Recognise common chemical symbols.",
        "learn": "Chemical symbols are short ways of representing elements.",
        "example": "O represents oxygen and H represents hydrogen.",
        "question": "What is the chemical symbol for oxygen?",
        "answers": ["o"]
    },
    ("Physics", "Electricity"): {
        "goal": "Understand the basic idea of an electric circuit.",
        "learn": "An electric circuit provides a complete path through which electric current can flow.",
        "example": "A simple circuit can contain a cell, wires and a bulb.",
        "question": "What must a circuit have for current to flow?",
        "answers": ["complete circuit", "a complete circuit", "closed circuit", "a closed circuit"]
    },
    ("Physics", "Motion"): {
        "goal": "Understand motion as a change in position.",
        "learn": "An object is moving when its position changes relative to a reference point.",
        "example": "A moving car changes its position relative to the road.",
        "question": "What does it mean when an object is in motion?",
        "answers": ["its position changes", "position changes"]
    },
    ("Physics", "Energy"): {
        "goal": "Understand energy as the ability to do work or cause change.",
        "learn": "Energy exists in different forms such as heat, light, electrical and chemical energy.",
        "example": "A battery stores chemical energy that can be converted into electrical energy.",
        "question": "Name one form of energy.",
        "answers": ["heat", "light", "electrical", "chemical", "sound", "kinetic", "potential"]
    }
}

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def ensure_tables():
    con = db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS learning_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT NOT NULL,
            attempts INTEGER DEFAULT 0,
            correct INTEGER DEFAULT 0,
            mastery INTEGER DEFAULT 0,
            last_activity TEXT
        )
    """)
    con.commit()
    con.close()

def normalize(value):
    return " ".join((value or "").lower().strip().replace(".", "").split())

def get_question(subject, topic, question_index=None):
    bank = QUESTION_BANK.get((subject, topic), [])

    if not bank:
        return get_lesson(subject, topic), 0

    if question_index is None:
        index = random.randrange(len(bank))
    else:
        try:
            index = int(question_index) % len(bank)
        except Exception:
            index = random.randrange(len(bank))

    base = get_lesson(subject, topic).copy()
    base.update(bank[index])
    return base, index

def get_lesson(subject, topic):
    key = (subject, topic)
    if key in LESSONS:
        return LESSONS[key]

    return {
        "goal": f"Understand the main ideas of {topic}.",
        "learn": f"{topic} is an important part of {subject}. Your tutor will help you understand the key ideas, vocabulary and examination skills for this topic.",
        "example": f"Start by identifying the important facts and explaining them in your own words. Then practise applying {topic} to a question.",
        "question": f"Explain one important thing you know about {topic}.",
        "answers": []
    }



# ============================================================
# ZIMSEC-ALIGNED ORIGINAL CURRICULUM CONTENT
# First module: Mathematics - Fractions
#
# Content is original instructional material designed around
# progressive Zimbabwean school-level mathematics skills.
# ============================================================

CURRICULUM = {
    ("Maths", "Decimals"): {
        "G1_G3": {
            "title": "Decimals: Tenths and Simple Decimal Numbers",
            "objective": "Read, write, compare and use simple decimals in everyday situations.",
            "key_terms": [
                "decimal", "decimal point", "tenths", "ones",
                "place value", "compare", "addition", "subtraction"
            ],
            "learn": (
                "A decimal is another way of writing part of a whole. "
                "The decimal point separates whole numbers from parts of a whole. "
                "The first digit after the decimal point represents tenths. "
                "For example, 2.5 means two wholes and five tenths. "
                "Decimals can be used when measuring money, length and other quantities."
            ),
            "example": (
                "If a bottle contains 1.5 litres of water, it contains "
                "one whole litre and five tenths of a litre."
            ),
            "practice": [
                {"question": "What is 2.5 + 1.2?", "answers": ["3.7", "3,7"]},
                {"question": "Which is greater: 0.7 or 0.5?", "answers": ["0.7", "0,7"]},
                {"question": "What is 5.8 - 2.3?", "answers": ["3.5", "3,5"]},
                {
                    "question": "What is the value of the digit 4 in 3.4?",
                    "answers": ["4 tenths", "four tenths", "0.4", "0,4"]
                }
            ]
        },

        "G4_G5": {
            "title": "Decimals: Place Value and Operations",
            "objective": "Use decimal place value accurately and perform calculations involving decimals.",
            "key_terms": [
                "decimal place", "tenths", "hundredths", "thousandths",
                "place value", "addition", "subtraction",
                "multiplication", "division"
            ],
            "learn": (
                "Decimals can contain tenths, hundredths and thousandths. "
                "The position of each digit determines its value. "
                "When adding or subtracting decimals, line up the decimal points. "
                "Decimals can also be multiplied and divided using appropriate place-value methods."
            ),
            "example": (
                "Calculate 12.45 + 3.70. "
                "Align the decimal points: 12.45 + 3.70 = 16.15."
            ),
            "practice": [
                {"question": "Calculate 12.45 + 3.70.", "answers": ["16.15", "16,15"]},
                {"question": "Calculate 20.5 - 7.85.", "answers": ["12.65", "12,65"]},
                {"question": "Calculate 2.5 × 4.", "answers": ["10", "10.0", "10,0"]},
                {"question": "Calculate 8.4 ÷ 2.", "answers": ["4.2", "4,2"]}
            ]
        },

        "G6_G7": {
            "title": "Decimals: Advanced Operations and Problem Solving",
            "objective": "Apply decimal operations accurately to multi-step calculations and practical problems.",
            "key_terms": [
                "decimal", "place value", "rounding",
                "significant figure", "recurring decimal",
                "multiplication", "division", "estimation"
            ],
            "learn": (
                "At this level, decimals are used in more complex calculations "
                "and problem-solving situations. Decimal answers may need to be "
                "rounded to a specified number of decimal places or significant "
                "figures. Estimation can be used to check whether an answer is reasonable."
            ),
            "example": (
                "Calculate 3.75 × 2.4. "
                "First calculate 375 × 24 = 9000, then account for three decimal places. "
                "Therefore, 3.75 × 2.4 = 9.0."
            ),
            "practice": [
                {"question": "Calculate 3.6 × 2.5.", "answers": ["9", "9.0", "9,0"]},
                {"question": "Calculate 14.4 ÷ 0.6.", "answers": ["24", "twenty four", "twenty-four"]},
                {"question": "Round 7.846 to 2 decimal places.", "answers": ["7.85", "7,85"]},
                {"question": "Round 0.006784 to 2 significant figures.", "answers": ["0.0068", "0,0068"]}
            ]
        },

        "F1_F2": {
            "title": "Decimals: Recurring Decimals, Approximation and Applications",
            "objective": "Manipulate decimals accurately and apply approximation and recurring-decimal concepts in secondary mathematics.",
            "key_terms": [
                "terminating decimal", "recurring decimal", "approximation",
                "decimal place", "significant figure", "rounding",
                "conversion", "accuracy"
            ],
            "learn": (
                "A terminating decimal ends after a finite number of decimal places, "
                "while a recurring decimal continues indefinitely with a repeating pattern. "
                "Fractions can be converted to decimals by division. "
                "Decimals are often rounded to a required degree of accuracy."
            ),
            "example": (
                "The fraction 1/4 gives 0.25, which is a terminating decimal. "
                "The fraction 1/3 gives 0.333..., which is a recurring decimal."
            ),
            "practice": [
                {"question": "Write 3/4 as a decimal.", "answers": ["0.75", "0,75"]},
                {"question": "Write 1/3 as a decimal.", "answers": ["0.333...", "0.333", "0,333...", "0,333"]},
                {"question": "Round 18.764 to 1 decimal place.", "answers": ["18.8", "18,8"]},
                {"question": "Round 0.004872 to 2 significant figures.", "answers": ["0.0049", "0,0049"]}
            ]
        },

        "F3_F4": {
            "title": "Decimals: Recurring Decimals, Accuracy and Algebraic Applications",
            "objective": "Convert, manipulate and apply decimals accurately in examination-style mathematical problems.",
            "key_terms": [
                "recurring decimal", "terminating decimal", "exact value",
                "approximation", "accuracy", "significant figure",
                "decimal representation", "algebra"
            ],
            "learn": (
                "Decimals can represent rational numbers exactly or approximately. "
                "Recurring decimals can be converted to fractions using algebraic methods. "
                "When a problem asks for an exact answer, avoid unnecessary rounding. "
                "When approximation is required, follow the stated degree of accuracy."
            ),
            "example": (
                "Let x = 0.333... . Then 10x = 3.333... . "
                "Subtracting gives 9x = 3, so x = 1/3."
            ),
            "practice": [
                {"question": "Convert 0.25 to a fraction in its simplest form.", "answers": ["1/4", "1 / 4"]},
                {"question": "Convert 0.75 to a fraction in its simplest form.", "answers": ["3/4", "3 / 4"]},
                {"question": "Round 5.67891 to 3 significant figures.", "answers": ["5.68", "5,68"]},
                {"question": "Write 0.125 as a fraction in its simplest form.", "answers": ["1/8", "1 / 8"]}
            ]
        },

        "F5_F6": {
            "title": "Decimals: Advanced Approximation and Examination Applications",
            "objective": "Use decimal representations, approximation and recurring decimals accurately in advanced examination-style problems.",
            "key_terms": [
                "recurring decimal", "exact value", "approximation", "error",
                "upper bound", "lower bound", "significant figure",
                "degree of accuracy"
            ],
            "learn": (
                "Advanced decimal work involves exact values, approximation and error. "
                "A stated rounded value represents a range of possible actual values. "
                "Upper and lower bounds can therefore be used to analyse measurements "
                "and calculations. Recurring decimals may also need to be converted "
                "to exact fractional forms rather than treated as rounded decimals."
            ),
            "example": (
                "If a length is recorded as 5.2 cm correct to the nearest 0.1 cm, "
                "its lower bound is 5.15 cm and its upper bound is 5.25 cm."
            ),
            "practice": [
                {
                    "question": "Convert 0.125 to an exact fraction in its simplest form.",
                    "answers": ["1/8", "1 / 8"]
                },
                {
                    "question": "Convert 0.375 to an exact fraction in its simplest form.",
                    "answers": ["3/8", "3 / 8"]
                },
                {
                    "question": "A length is 7.4 cm correct to the nearest 0.1 cm. What is its lower bound?",
                    "answers": ["7.35", "7,35"]
                },
                {
                    "question": "A length is 7.4 cm correct to the nearest 0.1 cm. What is its upper bound?",
                    "answers": ["7.45", "7,45"]
                }
            ]
        }
    },


    ("Maths", "Whole Numbers"): {
        "G1_G3": {
            "title": "Whole Numbers: Counting, Ordering and Basic Operations",
            "objective": "Read, write, compare and use whole numbers in simple everyday calculations.",
            "key_terms": [
                "whole number",
                "counting",
                "place value",
                "ones",
                "tens",
                "hundreds",
                "addition",
                "subtraction"
            ],
            "learn": (
                "Whole numbers are numbers such as 0, 1, 2, 3 and 4. "
                "We use them to count objects and describe how many things we have. "
                "The position of a digit tells us its place value. "
                "For example, in 245, the 2 represents two hundreds, "
                "the 4 represents four tens and the 5 represents five ones. "
                "We can add whole numbers to find a total and subtract to find "
                "how many are left."
            ),
            "example": (
                "There are 23 books on one shelf and 15 books on another shelf. "
                "23 + 15 = 38. Therefore, there are 38 books altogether."
            ),
            "practice": [
                {
                    "question": "What is 25 + 15?",
                    "answers": ["40", "forty"]
                },
                {
                    "question": "What is 80 - 35?",
                    "answers": ["45", "forty five", "forty-five"]
                },
                {
                    "question": "Which number is greater: 456 or 465?",
                    "answers": [
                        "465",
                        "four hundred and sixty five",
                        "four hundred sixty five",
                        "four hundred and sixty-five",
                        "four hundred sixty-five"
                    ]
                },
                {
                    "question": "What is the value of the digit 6 in 6,482?",
                    "answers": ["6000", "6 000", "six thousand"]
                }
            ]
        },

        "G4_G5": {
            "title": "Whole Numbers: Place Value, Factors and Multiples",
            "objective": "Work confidently with larger whole numbers, place value, factors, multiples and the four basic operations.",
            "key_terms": [
                "place value",
                "factor",
                "multiple",
                "prime number",
                "common factor",
                "common multiple",
                "operation",
                "order of operations"
            ],
            "learn": (
                "Large whole numbers are organised according to place value. "
                "A number can be separated into thousands, hundreds, tens and ones. "
                "A factor divides a number exactly, while a multiple is produced "
                "when a number is multiplied by a whole number. "
                "Prime numbers have exactly two factors: 1 and the number itself. "
                "When solving calculations, use the correct order of operations."
            ),
            "example": (
                "The factors of 24 include 1, 2, 3, 4, 6, 8, 12 and 24. "
                "The first five multiples of 6 are 6, 12, 18, 24 and 30."
            ),
            "practice": [
                {
                    "question": "What is 3,475 + 2,618?",
                    "answers": ["6093", "6,093", "six thousand and ninety three", "six thousand ninety three"]
                },
                {
                    "question": "What is 8,000 - 3,475?",
                    "answers": ["4525", "4,525", "four thousand five hundred and twenty five", "four thousand five hundred twenty five"]
                },
                {
                    "question": "Give one factor of 36 other than 1 and 36.",
                    "answers": ["2", "3", "4", "6", "9", "12", "18"]
                },
                {
                    "question": "What is the smallest common multiple of 4 and 6?",
                    "answers": ["12", "twelve"]
                }
            ]
        },

        "G6_G7": {
            "title": "Whole Numbers: Integers, Factors, Multiples and Problem Solving",
            "objective": "Apply whole-number and integer concepts to multi-step calculations and practical problems.",
            "key_terms": [
                "integer",
                "positive number",
                "negative number",
                "prime factor",
                "HCF",
                "LCM",
                "divisibility",
                "order of operations"
            ],
            "learn": (
                "At this level, whole-number skills are extended to integers and "
                "more complex calculations. Positive and negative integers can be "
                "represented on a number line. Factors can be used to find the "
                "highest common factor (HCF), while multiples can be used to find "
                "the lowest common multiple (LCM). Divisibility rules can make "
                "calculations faster and help identify factors."
            ),
            "example": (
                "The HCF of 18 and 24 is 6 because 6 is the greatest number that "
                "divides both numbers exactly. The LCM of 6 and 8 is 24 because "
                "24 is the smallest positive number that is a multiple of both."
            ),
            "practice": [
                {
                    "question": "Find the HCF of 18 and 24.",
                    "answers": ["6", "six"]
                },
                {
                    "question": "Find the LCM of 6 and 8.",
                    "answers": ["24", "twenty four", "twenty-four"]
                },
                {
                    "question": "Calculate 125 - 180.",
                    "answers": ["-55", "−55", "negative 55", "minus 55"]
                },
                {
                    "question": "Is 37 a prime number?",
                    "answers": ["yes", "yes it is", "yes, it is", "true"]
                }
            ]
        },

        "F1_F2": {
            "title": "Number Systems: Integers, Factors, Indices and Standard Form",
            "objective": "Use number properties, integers, indices and standard form accurately in secondary-school mathematics.",
            "key_terms": [
                "integer",
                "index",
                "power",
                "base",
                "standard form",
                "prime factorisation",
                "HCF",
                "LCM"
            ],
            "learn": (
                "Secondary mathematics requires accurate manipulation of integers "
                "and powers. The laws of indices help simplify expressions involving "
                "multiplication and division of powers. Large and small numbers can "
                "be written in standard form as a × 10^n, where 1 ≤ a < 10. "
                "Prime factorisation is useful when finding HCF and LCM."
            ),
            "example": (
                "Using prime factors, 60 = 2² × 3 × 5. "
                "The number 4,500 can be written in standard form as 4.5 × 10³."
            ),
            "practice": [
                {
                    "question": "Write 72 as a product of its prime factors.",
                    "answers": ["2^3 x 3^2", "2^3×3^2", "2³ × 3²", "2³x3²"]
                },
                {
                    "question": "Write 4,500 in standard form.",
                    "answers": ["4.5 x 10^3", "4.5×10^3", "4.5 × 10³", "4.5e3"]
                },
                {
                    "question": "Calculate 2³ × 2².",
                    "answers": ["32", "thirty two", "thirty-two"]
                },
                {
                    "question": "Find the HCF of 36 and 48.",
                    "answers": ["12", "twelve"]
                }
            ]
        },

        "F3_F4": {
            "title": "Number: Indices, Standard Form and Surds",
            "objective": "Manipulate powers, standard form and surds and apply number concepts to examination-style problems.",
            "key_terms": [
                "index law",
                "negative index",
                "fractional index",
                "standard form",
                "surd",
                "rationalise",
                "prime factorisation"
            ],
            "learn": (
                "Index laws provide efficient methods for simplifying powers. "
                "For example, a^m × a^n = a^(m+n), while a^m ÷ a^n = a^(m-n), "
                "provided the expressions are defined. Standard form is useful "
                "for very large or very small numbers. Surds are exact irrational "
                "forms such as √2 and can often be simplified by extracting square factors."
            ),
            "example": (
                "Simplify √72. Since 72 = 36 × 2, "
                "√72 = √36 × √2 = 6√2."
            ),
            "practice": [
                {
                    "question": "Simplify 2³ × 2⁴.",
                    "answers": ["128", "2^7", "2⁷"]
                },
                {
                    "question": "Write 0.00056 in standard form.",
                    "answers": ["5.6 x 10^-4", "5.6×10^-4", "5.6 × 10⁻⁴", "5.6e-4"]
                },
                {
                    "question": "Simplify √72.",
                    "answers": ["6√2", "6 root 2", "6sqrt2"]
                },
                {
                    "question": "Evaluate 5⁰.",
                    "answers": ["1", "one"]
                }
            ]
        },

        "F5_F6": {
            "title": "Number: Advanced Indices, Surds and Examination Applications",
            "objective": "Apply advanced number concepts accurately in algebraic manipulation and examination-style problems.",
            "key_terms": [
                "index laws",
                "negative index",
                "fractional index",
                "surd",
                "rationalisation",
                "standard form",
                "logarithm"
            ],
            "learn": (
                "Advanced number work combines index laws, surds, standard form and "
                "other number relationships with algebra. Negative indices represent "
                "reciprocals, while fractional indices can represent roots. "
                "Surds should be simplified exactly rather than converted to rounded "
                "decimal values when an exact answer is required. In examination "
                "problems, show the logical steps used to transform each expression."
            ),
            "example": (
                "Simplify 1/√3 by rationalising the denominator. "
                "Multiply the numerator and denominator by √3: "
                "1/√3 = √3/3."
            ),
            "practice": [
                {
                    "question": "Simplify 2⁻³.",
                    "answers": ["1/8", "0.125"]
                },
                {
                    "question": "Simplify √50.",
                    "answers": ["5√2", "5 root 2", "5sqrt2"]
                },
                {
                    "question": "Rationalise 1/√5.",
                    "answers": ["√5/5", "sqrt5/5"]
                },
                {
                    "question": "Write 0.0000032 in standard form.",
                    "answers": ["3.2 x 10^-6", "3.2×10^-6", "3.2 × 10⁻⁶", "3.2e-6"]
                }
            ]
        }
    },


    ("Maths", "Fractions"): {

        "G1_G3": {
            "title": "Fractions: Parts of a Whole",
            "objective": "Understand that a fraction represents equal parts of a whole.",
            "key_terms": [
                "whole",
                "fraction",
                "numerator",
                "denominator",
                "half",
                "quarter"
            ],
            "learn": (
                "A fraction tells us about part of a whole. "
                "The denominator is the bottom number and tells us how many "
                "equal parts the whole has been divided into. "
                "The numerator is the top number and tells us how many of "
                "those parts we have."
            ),
            "example": (
                "If a pizza is divided into 4 equal pieces and you eat 1 piece, "
                "you have eaten 1/4 of the pizza. The 4 tells us that the pizza "
                "was divided into four equal parts, while the 1 tells us that "
                "one part was taken."
            ),
            "practice": [
                {
                    "question": "What fraction means one half?",
                    "answers": ["1/2", "½"]
                },
                {
                    "question": "A shape is divided into 4 equal parts. One part is shaded. What fraction is shaded?",
                    "answers": ["1/4", "¼"]
                },
                {
                    "question": "In the fraction 3/4, what is the numerator?",
                    "answers": ["3"]
                }
            ]
        },

        "G4_G5": {
            "title": "Fractions: Equivalent Fractions and Operations",
            "objective": "Compare, simplify and perform basic operations with fractions.",
            "key_terms": [
                "proper fraction",
                "improper fraction",
                "equivalent fractions",
                "simplest form",
                "common denominator"
            ],
            "learn": (
                "Equivalent fractions have different numbers but represent the "
                "same value. For example, 1/2 and 2/4 are equivalent because "
                "multiplying both the numerator and denominator of 1/2 by 2 "
                "gives 2/4. Fractions should be simplified to their lowest terms "
                "when required."
            ),
            "example": (
                "To add 1/4 and 2/4, the denominators are already the same. "
                "Add the numerators: 1 + 2 = 3. Therefore, "
                "1/4 + 2/4 = 3/4."
            ),
            "practice": [
                {
                    "question": "Simplify 4/8 to its simplest form.",
                    "answers": ["1/2", "½"]
                },
                {
                    "question": "Calculate 2/7 + 3/7.",
                    "answers": ["5/7"]
                },
                {
                    "question": "Which is larger: 3/5 or 2/5?",
                    "answers": ["3/5"]
                }
            ]
        },

        "G6_G7": {
            "title": "Fractions: Mixed Numbers and Problem Solving",
            "objective": "Apply fraction operations to mixed numbers and real-life problems.",
            "key_terms": [
                "mixed number",
                "improper fraction",
                "common denominator",
                "simplify",
                "reciprocal"
            ],
            "learn": (
                "A mixed number contains a whole number and a fraction, such as "
                "2 1/3. To convert a mixed number to an improper fraction, "
                "multiply the whole number by the denominator, add the numerator, "
                "and keep the same denominator. Fraction problems should be "
                "solved carefully, with the answer simplified where possible."
            ),
            "example": (
                "Convert 2 1/3 to an improper fraction. "
                "First calculate 2 × 3 = 6. Add the numerator: 6 + 1 = 7. "
                "Therefore, 2 1/3 = 7/3."
            ),
            "practice": [
                {
                    "question": "Convert 2 1/4 to an improper fraction.",
                    "answers": ["9/4"]
                },
                {
                    "question": "Calculate 3/4 + 1/8.",
                    "answers": ["7/8"]
                },
                {
                    "question": "Convert 11/4 to a mixed number.",
                    "answers": ["2 3/4", "2 3/4"]
                }
            ]
        },

        "F1_F2": {
            "title": "Fractions: Operations and Algebraic Applications",
            "objective": "Perform operations with fractions and apply them to algebraic and numerical problems.",
            "key_terms": [
                "numerator",
                "denominator",
                "lowest common denominator",
                "improper fraction",
                "mixed number",
                "reciprocal"
            ],
            "learn": (
                "When adding or subtracting fractions with different denominators, "
                "first find a common denominator. When multiplying fractions, "
                "multiply the numerators together and the denominators together. "
                "To divide by a fraction, multiply by its reciprocal. "
                "Always simplify the final answer where possible."
            ),
            "example": (
                "Calculate 2/3 + 1/4. The lowest common denominator is 12. "
                "Convert 2/3 to 8/12 and 1/4 to 3/12. "
                "Therefore 8/12 + 3/12 = 11/12."
            ),
            "practice": [
                {
                    "question": "Calculate 3/5 + 1/10.",
                    "answers": ["7/10"]
                },
                {
                    "question": "Calculate 2/3 × 3/4.",
                    "answers": ["1/2", "½"]
                },
                {
                    "question": "Calculate 3/4 ÷ 1/2.",
                    "answers": ["3/2", "1.5"]
                }
            ]
        },

        "F3_F4": {
            "title": "Fractions: Algebraic Manipulation and Applications",
            "objective": "Use fractions confidently in algebraic expressions and examination-style problems.",
            "key_terms": [
                "algebraic fraction",
                "factor",
                "common denominator",
                "simplification",
                "reciprocal",
                "expression"
            ],
            "learn": (
                "Fractions can contain algebraic expressions as numerators or "
                "denominators. Simplification requires identifying common factors "
                "and cancelling only factors, not individual terms. When adding "
                "algebraic fractions, a suitable common denominator must first be "
                "found."
            ),
            "example": (
                "Simplify (6x)/(9x), where x is not zero. "
                "The common factor is 3x. Dividing numerator and denominator "
                "by 3x gives 2/3. Therefore (6x)/(9x) = 2/3."
            ),
            "practice": [
                {
                    "question": "Simplify 12x/18x, where x is not zero.",
                    "answers": ["2/3"]
                },
                {
                    "question": "Simplify 3/4 + 1/8.",
                    "answers": ["7/8"]
                },
                {
                    "question": "Simplify (x/3) + (x/6).",
                    "answers": ["x/2", "1/2x"]
                }
            ]
        },

        "F5_F6": {
            "title": "Fractions: Advanced Algebraic and Examination Applications",
            "objective": "Manipulate numerical and algebraic fractions accurately and apply them to complex problems.",
            "key_terms": [
                "algebraic fraction",
                "factorisation",
                "rational expression",
                "lowest common denominator",
                "restriction",
                "simplification"
            ],
            "learn": (
                "At advanced secondary level, fractions occur within algebraic "
                "expressions, equations and more complex applications. "
                "A rational expression must be simplified by factorising where "
                "appropriate and cancelling common factors. Restrictions on "
                "variables must be considered because a denominator cannot be zero."
            ),
            "example": (
                "Simplify (x² - 9)/(x² - 3x). "
                "Factorise the numerator: x² - 9 = (x - 3)(x + 3). "
                "Factorise the denominator: x² - 3x = x(x - 3). "
                "For x ≠ 0 and x ≠ 3, cancel the common factor (x - 3). "
                "The simplified expression is (x + 3)/x."
            ),
            "practice": [
                {
                    "question": "Simplify (x² - 16)/(x² - 4x), stating the restrictions on x.",
                    "answers": ["(x+4)/x", "x+4/x"]
                },
                {
                    "question": "Simplify 1/x + 1/(2x), where x is not zero.",
                    "answers": ["3/(2x)", "3/2x"]
                },
                {
                    "question": "Solve 1/x = 1/5 for x.",
                    "answers": ["5"]
                }
            ]
        }
    }
}


# ============================================================
# AUTO-LOAD CURRICULUM FROM SQLITE (added by connect_curriculum_v2.py)
# ============================================================
def _load_sqlite_curriculum():
    """Load all lessons from the 'curriculum' SQLite table and merge into CURRICULUM."""
    import sqlite3
    try:
        conn = sqlite3.connect("digital_classroom.db")
        conn.row_factory = sqlite3.Row
        rows = conn.execute('''
            SELECT grade_form, subject, topic, lesson_goal, content,
                   tutor_intro, requires_parent_assist
            FROM curriculum
        ''').fetchall()
        conn.close()

        loaded = 0
        for r in rows:
            subj = (r["subject"] or "").strip()
            topic = (r["topic"] or "").strip()
            if not subj or not topic:
                continue
            key = (subj, topic)
            if key not in CURRICULUM:
                CURRICULUM[key] = {
                    "goal":      r["lesson_goal"],
                    "content":   r["content"],
                    "tutor":     r["tutor_intro"],
                    "parent":    r["requires_parent_assist"] == "YES",
                    "grade":     r["grade_form"],
                    "_from_sql": True,
                }
            loaded += 1
        return loaded
    except Exception as e:
        print(f"⚠️ Curriculum loader error: {e}")
        return 0

_SQLITE_LESSONS_LOADED = _load_sqlite_curriculum()
print(f"📚 Loaded {_SQLITE_LESSONS_LOADED} lessons from SQLite curriculum table")


# ------------------------------------------------------------
# FULL CURRICULUM EXPANSION
# Existing curriculum entries are preserved with setdefault().
# ------------------------------------------------------------
from curriculum_expansion import CURRICULUM_EXPANSION
for _curriculum_key, _curriculum_value in CURRICULUM_EXPANSION.items():
    CURRICULUM.setdefault(_curriculum_key, _curriculum_value)
del _curriculum_key, _curriculum_value



def get_grade_aware_lesson(student_id, subject, topic):
    """
    Return curriculum-specific teaching content for the student's
    Grade/Form when available.

    Falls back to the existing LESSONS content for topics that have
    not yet been added to the curriculum bank.
    """

    grade = get_student_grade_form(student_id)
    band = get_student_learning_band(student_id)

    curriculum_topic = CURRICULUM.get((subject, topic), {})
    curriculum_lesson = curriculum_topic.get(band)

    if curriculum_lesson:
        lesson = dict(curriculum_lesson)

        # The expanded curriculum uses "objective",
        # while the existing lesson system uses "goal".
        # Keep both so existing code remains compatible.
        if "goal" not in lesson and "objective" in lesson:
            lesson["goal"] = lesson["objective"]

        lesson["_grade_form"] = str(grade or "")
        lesson["_learning_band"] = str(band or "")
        lesson["_curriculum"] = True

        return lesson

    # Existing lesson system remains the fallback.
    base = dict(get_lesson(subject, topic) or {})

    level_intro = {
        "G1_G3": "Learn this step by step using simple language and everyday examples.",
        "G4_G5": "Build your understanding carefully and practise using clear examples.",
        "G6_G7": "Focus on accurate methods, reasoning and applying the concept to problems.",
        "F1_F2": "Build a strong secondary-school foundation and show each important step.",
        "F3_F4": "Focus on deeper understanding, correct methods and examination-style application.",
        "F5_F6": "Focus on advanced secondary-school understanding, precise terminology and examination skills."
    }

    level_focus = {
        "G1_G3": "At this level, concentrate on the basic idea, vocabulary and simple examples.",
        "G4_G5": "At this level, concentrate on understanding the method and applying it to familiar problems.",
        "G6_G7": "At this level, concentrate on reasoning, accuracy and applying the method to different problems.",
        "F1_F2": "At this level, connect the basic idea to secondary-school terminology and structured problem solving.",
        "F3_F4": "At this level, explain your reasoning clearly and practise applying the concept in examination-style questions.",
        "F5_F6": "At this level, use precise terminology, show complete reasoning and apply the concept to unfamiliar examination-style problems."
    }

    prefix = level_intro.get(
        band,
        "Learn the concept carefully and practise applying it."
    )

    focus = level_focus.get(
        band,
        "Concentrate on understanding the concept and applying it correctly."
    )

    original_learn = str(base.get("learn", ""))
    original_example = str(base.get("example", ""))
    original_goal = str(base.get("goal", ""))

    base["goal"] = (
        f"{original_goal} "
        f"This lesson is adapted for {grade or 'your Grade/Form'}."
    )

    base["learn"] = (
        f"{prefix} {original_learn} {focus}"
    )

    base["example"] = (
        f"{original_example} "
        f"When working at {grade or 'your Grade/Form'} level, "
        f"show your working clearly and check your answer before submitting it."
    )

    base["_grade_form"] = str(grade or "")
    base["_learning_band"] = str(band or "")
    base["_curriculum"] = False

    return base

def get_progress(student_id, subject, topic):
    con = db()
    row = con.execute("""
        SELECT * FROM learning_progress
        WHERE student_id=? AND subject=? AND topic=?
        ORDER BY id DESC LIMIT 1
    """, (student_id, subject, topic)).fetchone()
    con.close()
    return row

def save_progress(student_id, subject, topic, correct):
    con = db()
    row = con.execute("""
        SELECT id, attempts, correct FROM learning_progress
        WHERE student_id=? AND subject=? AND topic=?
        ORDER BY id DESC LIMIT 1
    """, (student_id, subject, topic)).fetchone()

    if row:
        attempts = row["attempts"] + 1
        correct_total = row["correct"] + (1 if correct else 0)
        mastery = min(100, int((correct_total / attempts) * 100))
        con.execute("""
            UPDATE learning_progress
            SET attempts=?, correct=?, mastery=?, last_activity=?
            WHERE id=?
        """, (
            attempts,
            correct_total,
            mastery,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            row["id"]
        ))
    else:
        attempts = 1
        correct_total = 1 if correct else 0
        mastery = 100 if correct else 0
        con.execute("""
            INSERT INTO learning_progress
            (student_id, subject, topic, attempts, correct, mastery, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, subject, topic, attempts, correct_total, mastery,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

    con.commit()
    con.close()


GRADE_FORM_BANDS = {
    "Grade 1":"G1_G3",
    "Grade 2":"G1_G3",
    "Grade 3":"G1_G3",
    "Grade 4":"G4_G5",
    "Grade 5":"G4_G5",
    "Grade 6":"G6_G7",
    "Grade 7":"G6_G7",
    "Form 1":"F1_F2",
    "Form 2":"F1_F2",
    "Form 3":"F3_F4",
    "Form 4":"F3_F4",
    "Form 5":"F5_F6",
    "Form 6":"F5_F6",
}

def normalize_grade_form(value):
    value = str(value or "").strip()
    aliases = {
        "G1":"Grade 1","G2":"Grade 2","G3":"Grade 3",
        "G4":"Grade 4","G5":"Grade 5","G6":"Grade 6","G7":"Grade 7",
        "F1":"Form 1","F2":"Form 2","F3":"Form 3",
        "F4":"Form 4","F5":"Form 5","F6":"Form 6",
    }
    return aliases.get(value, value)

def get_student_grade_form(student_id):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT grade_form FROM students WHERE id=?",
        (student_id,)
    ).fetchone()
    con.close()
    return normalize_grade_form(row["grade_form"]) if row else ""

def get_student_learning_band(student_id):
    grade = get_student_grade_form(student_id)
    return GRADE_FORM_BANDS.get(grade, "G6_G7")

def get_grade_aware_question(student_id, subject, topic, question_index=None):
    grade = get_student_grade_form(student_id)
    band = get_student_learning_band(student_id)

    bank = QUESTION_BANK.get((subject, topic), [])

    if not bank:
        result = get_question(subject, topic, question_index)

        # Preserve the original (lesson, question_index) return format.
        if isinstance(result, tuple) and len(result) >= 2:
            lesson = dict(result[0] or {})
            index = result[1]
        else:
            lesson = dict(result or {})
            index = question_index

        lesson["_grade_form"] = str(grade or "")
        lesson["_learning_band"] = str(band or "")

        return lesson, index

    # Select the requested question or a random question.
    if question_index is None:
        index = random.randrange(len(bank))
    else:
        try:
            index = int(question_index) % len(bank)
        except Exception:
            index = 0

    # Build from the student's real Grade/Form curriculum lesson.
    base_lesson = get_grade_aware_lesson(student_id, subject, topic)
    lesson = dict(base_lesson or {})

    # Use the student's Grade/Form curriculum practice when available.
    curriculum_practice = lesson.get("practice") or []

    if curriculum_practice:
        try:
            practice_index = int(question_index) % len(curriculum_practice)
        except Exception:
            practice_index = 0

        practice = dict(curriculum_practice[practice_index])
        lesson.update(practice)
    else:
        # Fall back to the existing question bank.
        lesson.update(dict(bank[index]))

    # Attach the student's actual Grade/Form information.
    lesson["_grade_form"] = str(grade or "")
    lesson["_learning_band"] = str(band or "")

    return lesson, index


def register_student_learning(app):

    ensure_tables()

    @app.route("/student/<int:sid>/learn")
    def student_learn(sid):
        subject = request.args.get("subject", "")
        topic = request.args.get("topic", "")

        if not subject:
            return redirect(url_for("student_learning_topics", sid=sid))

        topics = SUBJECT_TOPICS.get(subject, [])
        if not topic:
            return render_template_string("""
            <!doctype html>
            <html>
            <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Choose Topic</title>
            <style>
            body{font-family:Arial;background:#f4f7fb;margin:0;padding:20px}
            .box{max-width:700px;margin:auto}
            .card{background:white;padding:18px;margin:12px 0;border-radius:16px;box-shadow:0 2px 10px #ddd}
            a{display:block;text-decoration:none;color:#111}
            .top{background:#111;color:white;padding:20px;border-radius:18px}
            </style>
            </head>
            <body>
            <div class="box">
            <div class="top">
            <h1>📚 {{subject}}</h1>
            <p>Choose what you want to learn.</p>
            </div>

            {% for t in topics %}
            <div class="card">
            <a href="{{url_for('student_learn',sid=sid,subject=subject,topic=t)}}">
            <b>📖 {{t}}</b><br>
            <small>Start this lesson →</small>
            </a>
            </div>
            {% endfor %}

            <p><a href="{{url_for('student_learning_topics',sid=sid)}}">⬅ Back to Subjects</a></p>
            </div>
            </body>
            </html>
            """, sid=sid, subject=subject, topics=topics)

        question_index = request.args.get('q')

        lesson, question_index = get_grade_aware_question(
            sid,
            subject,
            topic,
            question_index
        )

        progress = get_progress(sid, subject, topic)

        return render_template_string("""
        <!doctype html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>{{topic}}</title>
        <style>
        body{font-family:Arial;background:#f4f7fb;margin:0;padding:15px}
        .box{max-width:760px;margin:auto}
        .header{background:#111;color:white;padding:22px;border-radius:20px;margin-bottom:15px}
        .card{background:white;padding:20px;border-radius:18px;margin:14px 0;box-shadow:0 2px 10px #ddd}
        .goal{background:#e8f3ff;border-left:5px solid #1976d2}
        .example{background:#fff8df;border-left:5px solid #e0a800}
        textarea{width:100%;box-sizing:border-box;padding:14px;border:1px solid #ccc;border-radius:12px;font-size:17px;min-height:100px}
        button{width:100%;padding:15px;border:0;border-radius:12px;background:#111;color:white;font-size:17px}
        a{color:#111;text-decoration:none}
        .mastery{font-size:18px;font-weight:bold}
        </style>
        </head>
        <body>
        <div class="box">

        <div class="header">
        <h1>📚 {{subject}}</h1>
        <h2>{{topic}}</h2>
        <p>Learn • Practise • Improve</p>
        </div>

        <div class="card goal">
        <h3>🎯 Lesson Goal</h3>
        <p>{{lesson.goal}}</p>
        </div>

        <div class="card">
        <h3>📖 Learn</h3>
        <p>{{lesson.learn}}</p>
        </div>

        <div class="card example">
        <h3>💡 Example</h3>
        <p>{{lesson.example}}</p>
        </div>

        <div class="card">
        <h3>✏️ Your Turn</h3>
        <p><b>{{lesson.question}}</b></p>

        <form method="post" action="{{url_for('student_check_answer',sid=sid)}}">
        <input type="hidden" name="subject" value="{{subject}}">
        <input type="hidden" name="topic" value="{{topic}}">
        <input type="hidden" name="question_index" value="{{question_index}}">
        <textarea name="answer" placeholder="Write your answer here..." required></textarea>
        <br><br>
        <button type="submit">SUBMIT ANSWER</button>
        </form>
        </div>

        {% if progress %}
        <div class="card">
        <h3>📊 Your Progress</h3>
        <p>Attempts: {{progress.attempts}}</p>
        <p>Correct: {{progress.correct}}</p>
        <p class="mastery">Mastery: {{progress.mastery}}%</p>
        </div>
        {% endif %}

        <p>
        <a href="{{url_for('student_learning_topics',sid=sid)}}">⬅ Choose Another Subject</a>
        </p>

        </div>
        </body>
        </html>
        """,
        sid=sid,
        subject=subject,
        topic=topic,
        lesson=lesson,
        progress=progress,
        question_index=question_index)

    @app.route("/student/<int:sid>/learning")
    def student_learning_topics(sid):
        return render_template_string("""
        <!doctype html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Learning Centre</title>
        <style>
        body{font-family:Arial;background:#f4f7fb;margin:0;padding:15px}
        .box{max-width:760px;margin:auto}
        .header{background:#111;color:white;padding:22px;border-radius:20px}
        .card{background:white;padding:18px;margin:12px 0;border-radius:16px;box-shadow:0 2px 10px #ddd}
        a{text-decoration:none;color:#111;display:block}
        </style>
        </head>
        <body>
        <div class="box">
        <div class="header">
        <h1>🧠 Learning Centre</h1>
        <p>Choose a subject, then choose a topic.</p>
        </div>

        {% for subject in subjects %}
        <div class="card">
        <a href="{{url_for('student_learn',sid=sid,subject=subject)}}">
        <b>📘 {{subject}}</b><br>
        <small>Choose a topic →</small>
        </a>
        </div>
        {% endfor %}

        <p><a href="http://127.0.0.1:5001/student/{{sid}}/home">🏠 Back to Student Home</a></p>
        </div>
        </body>
        </html>
        """, sid=sid, subjects=list(SUBJECT_TOPICS.keys()))

    @app.route("/student/<int:sid>/check-answer", methods=["POST"])
    def student_check_answer(sid):
        subject = request.form.get("subject", "")
        topic = request.form.get("topic", "")
        answer = request.form.get("answer", "")

        question_index = request.form.get("question_index")

        lesson, question_index = get_grade_aware_question(
            sid,
            subject,
            topic,
            question_index
        )
        clean = normalize(answer)

        correct = False

        if lesson["answers"]:
            for expected in lesson["answers"]:
                if clean == normalize(expected):
                    correct = True
                    break
        else:
            # Never mark an answer correct merely because it contains
            # enough words. A question without a defined answer must
            # not automatically award mastery.
            correct = False

        save_progress(sid, subject, topic, correct)

        progress = get_progress(sid, subject, topic)

        bank = QUESTION_BANK.get((subject, topic), [])
        if bank:
            next_question_index = (int(question_index) + 1) % len(bank)
        else:
            next_question_index = 0

        if correct:
            title = "🎉 Excellent Work!"
            message = "That answer shows that you understand the key idea."
            feedback = "Keep going. Your mastery is improving."
        else:
            title = "💪 Good Try!"
            message = "You have not mastered this question yet."
            feedback = "Read the explanation again, study the example, and try the question again."

        return render_template_string("""
        <!doctype html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Result</title>
        <style>
        body{font-family:Arial;background:#f4f7fb;padding:20px}
        .box{max-width:700px;margin:auto}
        .card{background:white;padding:22px;border-radius:18px;box-shadow:0 2px 10px #ddd}
        .good{background:#e8f8ed;border-left:6px solid #219653}
        .try{background:#fff4e5;border-left:6px solid #f2994a}
        a,button{display:block;text-align:center;padding:14px;margin-top:12px;border-radius:12px;text-decoration:none}
        a{background:#111;color:white}
        </style>
        </head>
        <body>
        <div class="box">
        <div class="card {{'good' if correct else 'try'}}">
        <h1>{{title}}</h1>
        <h2>{{message}}</h2>
        <p>{{feedback}}</p>
          <p><b>Question:</b> {{lesson.question}}</p>
          <p><b>Your answer:</b> {{answer}}</p>

          {% if not correct %}
          <hr>
          <h3>📖 Let's Correct It</h3>

          {% if lesson.answers %}
          <p><b>Correct answer:</b> {{lesson.answers[0]}}</p>
          <p>
          The correct answer to this question is
          <b>{{lesson.answers[0]}}</b>.
          Review the question and try another one.
          </p>
          {% else %}
          <p>{{lesson.learn}}</p>
          <p><b>Example:</b> {{lesson.example}}</p>
          {% endif %}

          {% endif %}

        <p><b>Mastery: {{progress.mastery}}%</b></p>

        <a href="{{url_for('student_learn',sid=sid,subject=subject,topic=topic,q=next_question_index)}}">
        🔄 Try Another Question
        </a>

        <a href="{{url_for('student_learn',sid=sid,subject=subject)}}">
        📚 Choose Another Topic
        </a>

        <a href="http://127.0.0.1:5001/student/{{sid}}/home">
        🏠 Student Home
        </a>
        </div>
        </div>
        </body>
        </html>
        """,
        sid=sid,
        subject=subject,
        topic=topic,
        answer=answer,
        correct=correct,
        title=title,
        message=message,
        feedback=feedback,
        lesson=lesson,
        progress=progress,
        question_index=question_index,
        next_question_index=next_question_index
        )



# =========================================================
# FULL QUESTION BANK UPGRADE
# =========================================================

def _q(question, answer):
    return {
        "question": question,
        "answers": [str(answer)]
    }


def _build_maths_question_bank():
    banks = {}

    topics = SUBJECT_TOPICS.get("Maths", [])

    for topic in topics:

        t = str(topic).lower().strip()
        bank = []

        # -------------------------------------------------
        # WHOLE NUMBERS
        # -------------------------------------------------
        if "whole number" in t:
            bank = [
                _q("What is 25 + 15?", "40"),
                _q("What is 80 - 35?", "45"),
                _q("What is 7 × 8?", "56"),
                _q("What is 144 divided by 12?", "12"),
                _q("What is 300 + 450?", "750"),
                _q("What is 1000 - 275?", "725"),
                _q("What is 9 × 6?", "54"),
                _q("What is 96 divided by 8?", "12"),
                _q("Which number is greater: 456 or 465?", "465"),
                _q("What is the value of the digit 6 in 6,482?", "6000"),
            ]

        # -------------------------------------------------
        # DECIMALS
        # -------------------------------------------------
        elif "decimal" in t:
            bank = [
                _q("What is 2.5 + 1.5?", "4"),
                _q("What is 7.8 - 2.3?", "5.5"),
                _q("What is 0.5 × 10?", "5"),
                _q("What is 4.2 + 3.6?", "7.8"),
                _q("What is 9.5 - 4.5?", "5"),
                _q("What is 2.5 × 4?", "10"),
                _q("What is 6.4 ÷ 2?", "3.2"),
                _q("Which is greater: 0.7 or 0.6?", "0.7"),
                _q("Write one half as a decimal.", "0.5"),
                _q("What is 1.25 + 0.75?", "2"),
            ]

        # -------------------------------------------------
        # FRACTIONS
        # -------------------------------------------------
        elif "fraction" in t:
            bank = [
                _q("What is 1/2 + 1/2?", "1"),
                _q("What is 1/4 + 1/4?", "1/2"),
                _q("What is 3/4 - 1/4?", "1/2"),
                _q("What is 1/2 of 10?", "5"),
                _q("What is 1/4 of 20?", "5"),
                _q("What is 3/4 of 20?", "15"),
                _q("Which is greater: 1/2 or 1/4?", "1/2"),
                _q("What is 2/3 + 1/3?", "1"),
                _q("What is 5/6 - 2/6?", "1/2"),
                _q("What is 1/5 of 25?", "5"),
            ]

        # -------------------------------------------------
        # PERCENTAGES
        # -------------------------------------------------
        elif "percent" in t:
            bank = [
                _q("What is 10% of 100?", "10"),
                _q("What is 50% of 80?", "40"),
                _q("What is 25% of 100?", "25"),
                _q("What is 10% of 250?", "25"),
                _q("What is 20% of 200?", "40"),
                _q("What is 50% of 60?", "30"),
                _q("What is 25% of 80?", "20"),
                _q("What is 75% of 100?", "75"),
                _q("What is 5% of 200?", "10"),
                _q("What is 30% of 100?", "30"),
            ]

        # -------------------------------------------------
        # RATIO
        # -------------------------------------------------
        elif "ratio" in t:
            bank = [
                _q("Simplify the ratio 2:4.", "1:2"),
                _q("Simplify the ratio 3:6.", "1:2"),
                _q("Simplify the ratio 5:10.", "1:2"),
                _q("Simplify the ratio 4:8.", "1:2"),
                _q("Simplify the ratio 6:9.", "2:3"),
                _q("Simplify the ratio 10:15.", "2:3"),
                _q("If boys:girls = 2:3 and there are 4 boys, how many girls are there?", "6"),
                _q("If 1:2 represents 5:10, what is the second number when the first is 10?", "20"),
                _q("What is the ratio of 10 apples to 5 oranges in simplest form?", "2:1"),
                _q("Simplify the ratio 8:12.", "2:3"),
            ]

        # -------------------------------------------------
        # ALGEBRA / EQUATIONS
        # -------------------------------------------------
        elif "algebra" in t or "equation" in t:
            bank = [
                _q("Solve x + 5 = 12.", "7"),
                _q("Solve x - 4 = 9.", "13"),
                _q("Solve 2x = 10.", "5"),
                _q("Solve x + 8 = 20.", "12"),
                _q("Solve x - 7 = 3.", "10"),
                _q("Solve 3x = 18.", "6"),
                _q("Solve x + 15 = 25.", "10"),
                _q("Solve 4x = 20.", "5"),
                _q("Solve x - 9 = 6.", "15"),
                _q("Solve 5x = 35.", "7"),
            ]

        # -------------------------------------------------
        # GEOMETRY / SHAPES
        # -------------------------------------------------
        elif "geometry" in t or "shape" in t:
            bank = [
                _q("How many sides does a triangle have?", "3"),
                _q("How many sides does a square have?", "4"),
                _q("How many sides does a pentagon have?", "5"),
                _q("How many sides does a hexagon have?", "6"),
                _q("How many degrees are in a right angle?", "90"),
                _q("How many degrees are in a straight angle?", "180"),
                _q("How many equal sides does a square have?", "4"),
                _q("How many vertices does a cube have?", "8"),
                _q("How many sides does an octagon have?", "8"),
                _q("How many degrees are in a full turn?", "360"),
            ]

        # -------------------------------------------------
        # MEASUREMENT
        # -------------------------------------------------
        elif "measurement" in t or "measure" in t:
            bank = [
                _q("How many centimetres are in 1 metre?", "100"),
                _q("How many metres are in 1 kilometre?", "1000"),
                _q("How many millimetres are in 1 centimetre?", "10"),
                _q("How many minutes are in 1 hour?", "60"),
                _q("How many seconds are in 1 minute?", "60"),
                _q("How many hours are in 1 day?", "24"),
                _q("How many days are in 1 week?", "7"),
                _q("How many grams are in 1 kilogram?", "1000"),
                _q("How many millilitres are in 1 litre?", "1000"),
                _q("How many months are in 1 year?", "12"),
            ]

        # -------------------------------------------------
        # STATISTICS
        # -------------------------------------------------
        elif "statistic" in t:
            bank = [
                _q("Find the mean of 2, 4 and 6.", "4"),
                _q("Find the mean of 5, 5 and 5.", "5"),
                _q("What is the mode of 2, 3, 3, 4?", "3"),
                _q("What is the mode of 5, 5, 6, 7?", "5"),
                _q("What is the range of 2, 5, 9?", "7"),
                _q("What is the range of 10, 15, 20?", "10"),
                _q("What is the median of 2, 4, 6?", "4"),
                _q("What is the median of 1, 3, 5, 7, 9?", "5"),
                _q("Find the mean of 10 and 20.", "15"),
                _q("What is the mode of 1, 2, 2, 3, 4?", "2"),
            ]

        # -------------------------------------------------
        # AVERAGES
        # -------------------------------------------------
        elif "average" in t or "mean" in t:
            bank = [
                _q("Find the average of 2, 4 and 6.", "4"),
                _q("Find the average of 5 and 15.", "10"),
                _q("Find the average of 10, 20 and 30.", "20"),
                _q("Find the average of 4, 6 and 8.", "6"),
                _q("Find the average of 5, 10 and 15.", "10"),
                _q("Find the average of 20 and 40.", "30"),
                _q("Find the average of 3, 6 and 9.", "6"),
                _q("Find the average of 10, 10 and 20.", "13.3333333333"),
                _q("Find the average of 12 and 18.", "15"),
                _q("Find the average of 8, 10 and 12.", "10"),
            ]

        # -------------------------------------------------
        # MULTIPLICATION
        # -------------------------------------------------
        elif "multiplication" in t or "multiply" in t:
            bank = [
                _q("What is 6 × 7?", "42"),
                _q("What is 8 × 9?", "72"),
                _q("What is 12 × 5?", "60"),
                _q("What is 7 × 7?", "49"),
                _q("What is 9 × 8?", "72"),
                _q("What is 11 × 6?", "66"),
                _q("What is 12 × 12?", "144"),
                _q("What is 15 × 4?", "60"),
                _q("What is 25 × 4?", "100"),
                _q("What is 20 × 6?", "120"),
            ]

        # -------------------------------------------------
        # DIVISION
        # -------------------------------------------------
        elif "division" in t or "divide" in t:
            bank = [
                _q("What is 24 ÷ 6?", "4"),
                _q("What is 36 ÷ 6?", "6"),
                _q("What is 48 ÷ 8?", "6"),
                _q("What is 72 ÷ 9?", "8"),
                _q("What is 81 ÷ 9?", "9"),
                _q("What is 100 ÷ 10?", "10"),
                _q("What is 144 ÷ 12?", "12"),
                _q("What is 96 ÷ 8?", "12"),
                _q("What is 120 ÷ 10?", "12"),
                _q("What is 150 ÷ 15?", "10"),
            ]

        # -------------------------------------------------
        # ADDITION / SUBTRACTION
        # -------------------------------------------------
        elif "addition" in t or "add" in t:
            bank = [
                _q("What is 45 + 25?", "70"),
                _q("What is 120 + 80?", "200"),
                _q("What is 250 + 150?", "400"),
                _q("What is 35 + 65?", "100"),
                _q("What is 500 + 250?", "750"),
                _q("What is 75 + 25?", "100"),
                _q("What is 125 + 125?", "250"),
                _q("What is 600 + 300?", "900"),
                _q("What is 45 + 55?", "100"),
                _q("What is 325 + 175?", "500"),
            ]

        elif "subtraction" in t or "subtract" in t:
            bank = [
                _q("What is 75 - 25?", "50"),
                _q("What is 100 - 35?", "65"),
                _q("What is 250 - 100?", "150"),
                _q("What is 500 - 250?", "250"),
                _q("What is 90 - 45?", "45"),
                _q("What is 120 - 70?", "50"),
                _q("What is 300 - 125?", "175"),
                _q("What is 1000 - 400?", "600"),
                _q("What is 200 - 75?", "125"),
                _q("What is 650 - 150?", "500"),
            ]

        # -------------------------------------------------
        # PLACE VALUE / NUMBER
        # -------------------------------------------------
        elif "place value" in t or "number" in t:
            bank = [
                _q("What is the value of 5 in 5,432?", "5000"),
                _q("What is the value of 3 in 3,210?", "3000"),
                _q("What is the value of 7 in 1,725?", "700"),
                _q("What is the value of 4 in 4,321?", "4000"),
                _q("Which is greater: 789 or 798?", "798"),
                _q("Which is smaller: 345 or 354?", "345"),
                _q("What comes after 999?", "1000"),
                _q("What comes before 500?", "499"),
                _q("How many hundreds are in 500?", "5"),
                _q("How many tens are in 90?", "9"),
            ]

        # -------------------------------------------------
        # GENERIC BUT UNIQUE FALLBACK
        # -------------------------------------------------
        else:
            bank = [
                _q(f"What topic are you studying in this lesson?", topic),
                _q(f"What is the name of this Maths topic?", topic),
                _q(f"Which topic should you focus on in this lesson?", topic),
                _q(f"Write the Maths topic you are currently learning.", topic),
                _q(f"What topic is shown at the top of this lesson?", topic),
            ]

        banks[( "Maths", topic )] = bank

    return banks


# Build banks for every Maths topic already installed.
QUESTION_BANK.update(_build_maths_question_bank())


# =========================================================
# QUESTION BANK NAVIGATION SAFETY
# =========================================================

def get_question(subject, topic, question_index=None):

    bank = QUESTION_BANK.get((subject, topic), [])

    if not bank:
        return get_lesson(subject, topic), 0

    try:
        if question_index is None:
            index = random.randrange(len(bank))
        else:
            index = int(question_index) % len(bank)
    except Exception:
        index = 0

    base = get_lesson(subject, topic).copy()
    base.update(bank[index])

    return base, index

