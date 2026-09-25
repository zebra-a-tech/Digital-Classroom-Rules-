"""
Digital Classroom Rules
Full Curriculum Expansion

Adds the missing curriculum topics without modifying the existing
Whole Numbers, Fractions and Decimals curriculum.

Bands:
G1_G3, G4_G5, G6_G7, F1_F2, F3_F4, F5_F6
"""

BANDS = (
    "G1_G3",
    "G4_G5",
    "G6_G7",
    "F1_F2",
    "F3_F4",
    "F5_F6",
)

BAND_NAMES = {
    "G1_G3": "Grades 1–3",
    "G4_G5": "Grades 4–5",
    "G6_G7": "Grades 6–7",
    "F1_F2": "Forms 1–2",
    "F3_F4": "Forms 3–4",
    "F5_F6": "Forms 5–6",
}

# ---------------------------------------------------------------------
# Progressive curriculum focus
# ---------------------------------------------------------------------

FOCUS = {
    "Maths": {
        "Percentages": {
            "G1_G3": "Recognise simple parts of a hundred and relate familiar fractions to percentages.",
            "G4_G5": "Find simple percentages of quantities and convert between fractions, decimals and percentages.",
            "G6_G7": "Solve percentage increase, decrease and comparison problems.",
            "F1_F2": "Apply percentages to profit, loss, discounts, simple interest and everyday problems.",
            "F3_F4": "Solve reverse percentage, repeated percentage change and examination-style problems.",
            "F5_F6": "Apply percentage methods to compound change, financial mathematics and algebraic applications.",
        },
        "Algebra": {
            "G1_G3": "Recognise patterns and use simple symbols for unknown numbers.",
            "G4_G5": "Use letters for unknowns and simplify simple expressions.",
            "G6_G7": "Form, simplify and substitute into algebraic expressions.",
            "F1_F2": "Expand brackets, collect like terms and solve simple linear equations.",
            "F3_F4": "Factorise expressions and solve simultaneous and quadratic-related problems.",
            "F5_F6": "Use advanced algebraic manipulation, functions and algebraic modelling.",
        },
        "Multiplication": {
            "G1_G3": "Develop multiplication facts and use multiplication in everyday problems.",
            "G4_G5": "Multiply larger whole numbers and decimals using efficient written methods.",
            "G6_G7": "Apply multiplication to fractions, decimals, measures and multi-step problems.",
            "F1_F2": "Use multiplication confidently with directed numbers, fractions and algebraic terms.",
            "F3_F4": "Apply multiplication in algebra, standard form and examination problems.",
            "F5_F6": "Use multiplication accurately in advanced algebraic, numerical and financial applications.",
        },
        "Division": {
            "G1_G3": "Understand sharing, grouping and basic division facts.",
            "G4_G5": "Divide larger numbers and interpret remainders in context.",
            "G6_G7": "Divide decimals, fractions and quantities and solve multi-step problems.",
            "F1_F2": "Work with directed numbers, fractions and algebraic division.",
            "F3_F4": "Use division in algebraic manipulation, ratios and standard form.",
            "F5_F6": "Apply exact and approximate division in advanced numerical and algebraic problems.",
        },
        "Geometry": {
            "G1_G3": "Recognise common 2-D and 3-D shapes, position and simple measures.",
            "G4_G5": "Work with angles, perimeter, area and properties of common shapes.",
            "G6_G7": "Use angle properties, area, volume, symmetry and geometric reasoning.",
            "F1_F2": "Apply angle theorems, polygons, circles and geometric constructions.",
            "F3_F4": "Use similarity, congruence, circle geometry and coordinate geometry.",
            "F5_F6": "Apply advanced geometry, trigonometric relationships and proof-based reasoning.",
        },
        "Percentages": {},
    },
    "English": {
        "Grammar": {
            "G1_G3": "Build correct simple sentences using nouns, verbs, pronouns and basic punctuation.",
            "G4_G5": "Use grammatical structures accurately in increasingly complex sentences.",
            "G6_G7": "Identify and correct grammatical errors in extended writing.",
            "F1_F2": "Use formal grammatical structures, agreement, clauses and sentence variety.",
            "F3_F4": "Analyse and manipulate complex grammatical structures for effective writing.",
            "F5_F6": "Apply advanced grammar accurately for formal, academic and examination writing.",
        },
        "Tenses": {
            "G1_G3": "Use simple present, past and future forms.",
            "G4_G5": "Distinguish common present, past and future tense forms.",
            "G6_G7": "Use continuous and perfect forms appropriately.",
            "F1_F2": "Control tense sequence and consistency in extended writing.",
            "F3_F4": "Use complex tense structures accurately for narrative and formal writing.",
            "F5_F6": "Manipulate tense and aspect precisely for advanced written expression.",
        },
        "Sentence Construction": {
            "G1_G3": "Build clear simple sentences with correct word order and punctuation.",
            "G4_G5": "Combine simple sentences into compound and more detailed sentences.",
            "G6_G7": "Use compound and complex sentences accurately.",
            "F1_F2": "Construct varied sentences using clauses and linking devices.",
            "F3_F4": "Use sophisticated sentence structures for purpose and audience.",
            "F5_F6": "Control complex syntax for precise formal and academic communication.",
        },
        "Parts of Speech": {
            "G1_G3": "Identify common nouns, verbs, adjectives and pronouns.",
            "G4_G5": "Identify and use the major parts of speech in sentences.",
            "G6_G7": "Analyse how parts of speech affect meaning and sentence structure.",
            "F1_F2": "Use parts of speech accurately in formal and extended writing.",
            "F3_F4": "Analyse grammatical roles and word classes in complex sentences.",
            "F5_F6": "Apply detailed grammatical analysis and deliberate word-class choices.",
        },
        "Vocabulary": {
            "G1_G3": "Build everyday vocabulary and understand simple synonyms and antonyms.",
            "G4_G5": "Expand vocabulary through context, synonyms, antonyms and word families.",
            "G6_G7": "Use context clues, prefixes, suffixes and precise vocabulary.",
            "F1_F2": "Develop formal vocabulary and distinguish shades of meaning.",
            "F3_F4": "Use advanced vocabulary appropriately for audience, purpose and context.",
            "F5_F6": "Demonstrate precise, varied and sophisticated vocabulary in formal communication.",
        },
    },
    "Science": {
        "Human Body": {
            "G1_G3": "Identify major body parts and describe basic healthy habits.",
            "G4_G5": "Describe major organs and their basic functions.",
            "G6_G7": "Explain major body systems and how they work together.",
            "F1_F2": "Study organs and systems involved in nutrition, respiration, circulation and excretion.",
            "F3_F4": "Explain physiological processes and relationships between body systems.",
            "F5_F6": "Apply detailed biological principles to human physiology and homeostasis.",
        },
        "Plants": {
            "G1_G3": "Identify plant parts and describe what plants need to grow.",
            "G4_G5": "Explain roots, stems, leaves, flowers and seed formation.",
            "G6_G7": "Explain photosynthesis, transport and reproduction in flowering plants.",
            "F1_F2": "Study plant nutrition, transport and reproduction.",
            "F3_F4": "Explain plant physiology and factors affecting growth and photosynthesis.",
            "F5_F6": "Apply advanced principles of plant transport, reproduction and physiological control.",
        },
        "Forces": {
            "G1_G3": "Recognise pushes, pulls and simple effects of forces.",
            "G4_G5": "Describe common forces such as gravity, friction and air resistance.",
            "G6_G7": "Explain balanced and unbalanced forces and their effects on motion.",
            "F1_F2": "Use force diagrams and calculate simple resultant forces.",
            "F3_F4": "Apply Newtonian ideas, moments, pressure and force relationships.",
            "F5_F6": "Analyse forces quantitatively using mechanics and advanced problem solving.",
        },
        "Matter": {
            "G1_G3": "Recognise solids, liquids and gases.",
            "G4_G5": "Describe properties and changes of state.",
            "G6_G7": "Explain particle behaviour and changes of state.",
            "F1_F2": "Use the particle model to explain physical properties and changes.",
            "F3_F4": "Apply kinetic particle theory to pressure, diffusion and changes of state.",
            "F5_F6": "Use quantitative and microscopic models to explain advanced behaviour of matter.",
        },
    },
    "Biology": {
        "Cells": {
            "G1_G3": "Recognise that living things are made of cells at a basic level.",
            "G4_G5": "Identify basic cell structures and their functions.",
            "G6_G7": "Compare plant and animal cells and explain specialised cells.",
            "F1_F2": "Describe cell structure, organisation and microscopy.",
            "F3_F4": "Explain cell division, transport and specialised cellular functions.",
            "F5_F6": "Apply advanced cell biology to membranes, organelles, division and transport.",
        },
        "Photosynthesis": {
            "G1_G3": "Understand that plants need light, water and air to grow.",
            "G4_G5": "Describe photosynthesis as the process by which green plants make food.",
            "G6_G7": "State the word equation and explain the role of light and chlorophyll.",
            "F1_F2": "Use the balanced chemical equation and investigate factors affecting photosynthesis.",
            "F3_F4": "Analyse limiting factors and experimental evidence.",
            "F5_F6": "Apply advanced biochemical and quantitative reasoning to photosynthesis.",
        },
        "Respiration": {
            "G1_G3": "Understand that living things need energy to live and grow.",
            "G4_G5": "Describe respiration as an energy-releasing process.",
            "G6_G7": "Distinguish aerobic and anaerobic respiration.",
            "F1_F2": "State respiration equations and relate respiration to exercise.",
            "F3_F4": "Explain aerobic and anaerobic pathways and energy transfer.",
            "F5_F6": "Apply advanced cellular respiration and energy-yield concepts.",
        },
    },
    "Chemistry": {
        "Atoms": {
            "G1_G3": "Understand that materials are made from tiny particles.",
            "G4_G5": "Recognise atoms as basic building units of elements.",
            "G6_G7": "Describe simple atomic structure.",
            "F1_F2": "Identify protons, neutrons and electrons and use atomic and mass numbers.",
            "F3_F4": "Explain isotopes, electron arrangements and ions.",
            "F5_F6": "Apply advanced atomic structure, electron configurations and isotopic reasoning.",
        },
        "Elements": {
            "G1_G3": "Recognise common elements and materials made from them.",
            "G4_G5": "Understand that elements contain one type of atom.",
            "G6_G7": "Use the periodic table to identify common elements.",
            "F1_F2": "Relate periodic position to atomic structure and properties.",
            "F3_F4": "Explain trends and chemical behaviour across the periodic table.",
            "F5_F6": "Apply periodic trends and electronic structure to predict chemical behaviour.",
        },
        "Chemical Symbols": {
            "G1_G3": "Recognise familiar chemical symbols such as O, H and C.",
            "G4_G5": "Use common element symbols correctly.",
            "G6_G7": "Interpret symbols and simple chemical formulae.",
            "F1_F2": "Write and interpret formulae for common substances.",
            "F3_F4": "Use formulae accurately in equations and quantitative chemistry.",
            "F5_F6": "Apply chemical notation, formulae and equations in advanced calculations.",
        },
    },
    "Physics": {
        "Electricity": {
            "G1_G3": "Recognise simple electrical circuits and safe uses of electricity.",
            "G4_G5": "Identify circuit components and explain simple series circuits.",
            "G6_G7": "Explain current, voltage and resistance at an introductory level.",
            "F1_F2": "Use circuit diagrams and basic relationships between current, voltage and resistance.",
            "F3_F4": "Calculate electrical quantities and analyse series and parallel circuits.",
            "F5_F6": "Apply advanced circuit analysis, electrical power and energy calculations.",
        },
        "Motion": {
            "G1_G3": "Describe movement using everyday words such as fast, slow, near and far.",
            "G4_G5": "Compare speeds and describe changes in motion.",
            "G6_G7": "Calculate speed and interpret simple distance-time information.",
            "F1_F2": "Use speed, distance and time calculations and interpret graphs.",
            "F3_F4": "Calculate acceleration and analyse velocity-time graphs.",
            "F5_F6": "Apply advanced mechanics to displacement, velocity, acceleration and motion graphs.",
        },
        "Energy": {
            "G1_G3": "Recognise energy in familiar activities such as food, light and movement.",
            "G4_G5": "Identify common forms and transfers of energy.",
            "G6_G7": "Explain energy stores, transfers and conservation.",
            "F1_F2": "Calculate simple work, power and energy quantities.",
            "F3_F4": "Apply energy equations to mechanical and electrical systems.",
            "F5_F6": "Analyse energy efficiency, power and advanced physical applications.",
        },
    },
}

# Remove the intentionally unused placeholder.
FOCUS["Maths"].pop("Percentages", None)


# ---------------------------------------------------------------------
# Topic-specific key terms
# ---------------------------------------------------------------------

KEY_TERMS = {
    "Percentages": ["percentage", "fraction", "decimal", "increase", "decrease"],
    "Algebra": ["variable", "coefficient", "constant", "expression", "equation"],
    "Multiplication": ["factor", "product", "multiple", "array", "multiply"],
    "Division": ["dividend", "divisor", "quotient", "remainder", "inverse"],
    "Geometry": ["angle", "perimeter", "area", "volume", "polygon"],
    "Grammar": ["noun", "verb", "agreement", "clause", "punctuation"],
    "Tenses": ["present", "past", "future", "continuous", "perfect"],
    "Sentence Construction": ["subject", "predicate", "clause", "phrase", "conjunction"],
    "Parts of Speech": ["noun", "pronoun", "verb", "adjective", "adverb"],
    "Vocabulary": ["synonym", "antonym", "prefix", "suffix", "context"],
    "Human Body": ["organ", "system", "respiration", "circulation", "digestion"],
    "Plants": ["root", "stem", "leaf", "flower", "photosynthesis"],
    "Forces": ["force", "friction", "gravity", "mass", "motion"],
    "Matter": ["solid", "liquid", "gas", "particle", "state"],
    "Cells": ["cell", "nucleus", "membrane", "cytoplasm", "organelle"],
    "Photosynthesis": ["chlorophyll", "glucose", "carbon dioxide", "water", "light"],
    "Respiration": ["respiration", "glucose", "oxygen", "energy", "carbon dioxide"],
    "Atoms": ["atom", "proton", "neutron", "electron", "nucleus"],
    "Elements": ["element", "periodic table", "group", "period", "atom"],
    "Chemical Symbols": ["symbol", "formula", "element", "compound", "equation"],
    "Electricity": ["current", "voltage", "resistance", "circuit", "charge"],
    "Motion": ["distance", "speed", "velocity", "acceleration", "time"],
    "Energy": ["energy", "power", "work", "efficiency", "transfer"],
}


# ---------------------------------------------------------------------
# Safe, topic-specific practice questions
# These provide a reliable baseline while the lesson explanations
# establish the appropriate level for each band.
# ---------------------------------------------------------------------

PRACTICE = {
    ("Maths", "Percentages"): [
        ("What percentage is one half?", ["50%", "50"]),
        ("Convert 25% to a fraction in simplest form.", ["1/4", "1 / 4"]),
        ("What is 10% of 200?", ["20"]),
        ("Increase 100 by 10%.", ["110"]),
    ],
    ("Maths", "Algebra"): [
        ("If x = 5, what is x + 3?", ["8"]),
        ("Simplify 2x + 3x.", ["5x"]),
        ("Solve x + 4 = 9.", ["5"]),
        ("Solve 2x = 14.", ["7"]),
    ],
    ("Maths", "Multiplication"): [
        ("What is 6 × 7?", ["42"]),
        ("What is 12 × 8?", ["96"]),
        ("What is 25 × 4?", ["100"]),
        ("What is 125 × 8?", ["1000"]),
    ],
    ("Maths", "Division"): [
        ("What is 42 ÷ 6?", ["7"]),
        ("What is 96 ÷ 8?", ["12"]),
        ("What is 100 ÷ 4?", ["25"]),
        ("What is 1000 ÷ 8?", ["125"]),
    ],
    ("Maths", "Geometry"): [
        ("How many degrees are in a right angle?", ["90", "90°"]),
        ("How many sides does a triangle have?", ["3"]),
        ("How many degrees are in a straight angle?", ["180", "180°"]),
        ("What is the perimeter of a square with side 5 cm?", ["20 cm", "20"]),
    ],
    ("English", "Grammar"): [
        ("Identify the noun in: 'The boy runs.'", ["boy"]),
        ("Identify the verb in: 'The girl sings.'", ["sings"]),
        ("What is the plural of 'child'?", ["children"]),
        ("Choose the correct form: 'She ___ happy.'", ["is"]),
    ],
    ("English", "Tenses"): [
        ("Change 'walk' to the simple past tense.", ["walked"]),
        ("What is the future form of 'I eat'?", ["I will eat"]),
        ("Identify the tense: 'She is reading.'", ["present continuous"]),
        ("Identify the tense: 'They had finished.'", ["past perfect"]),
    ],
    ("English", "Sentence Construction"): [
        ("Complete: 'The dog ___ loudly.'", ["barks"]),
        ("Which word is the subject in 'The teacher speaks'?", ["teacher"]),
        ("Join 'I was tired' and 'I continued working' using 'but'.", ["I was tired but I continued working."]),
        ("What punctuation mark ends a question?", ["question mark", "?"]),
    ],
    ("English", "Parts of Speech"): [
        ("What part of speech is 'quickly'?", ["adverb"]),
        ("What part of speech is 'beautiful'?", ["adjective"]),
        ("What part of speech is 'teacher'?", ["noun"]),
        ("What part of speech is 'run' in 'They run daily'?", ["verb"]),
    ],
    ("English", "Vocabulary"): [
        ("Give a synonym for 'happy'.", ["glad", "joyful", "cheerful"]),
        ("Give an antonym for 'hot'.", ["cold"]),
        ("What is the opposite of 'early'?", ["late"]),
        ("Give a synonym for 'large'.", ["big", "huge", "large"]),
    ],
    ("Science", "Human Body"): [
        ("Which organ pumps blood around the body?", ["heart"]),
        ("Which organ is mainly used for breathing?", ["lungs"]),
        ("Which organ controls the body?", ["brain"]),
        ("Where does most digestion and absorption of food occur?", ["small intestine"]),
    ],
    ("Science", "Plants"): [
        ("Which plant part usually absorbs water from the soil?", ["root", "roots"]),
        ("Which part of a plant usually makes food?", ["leaf", "leaves"]),
        ("What gas do plants take in for photosynthesis?", ["carbon dioxide"]),
        ("What gas is released during photosynthesis?", ["oxygen"]),
    ],
    ("Science", "Forces"): [
        ("What force pulls objects towards Earth?", ["gravity", "gravitational force"]),
        ("What force opposes motion between surfaces?", ["friction"]),
        ("What can a force change: an object's motion or colour?", ["motion"]),
        ("What is measured in newtons?", ["force"]),
    ],
    ("Science", "Matter"): [
        ("Name the three common states of matter.", ["solid, liquid and gas", "solid liquid gas"]),
        ("Which state has a fixed shape?", ["solid"]),
        ("What happens to ice when it melts?", ["it becomes liquid", "melts into water"]),
        ("What is matter made of?", ["particles"]),
    ],
    ("Biology", "Cells"): [
        ("What is the basic unit of life?", ["cell"]),
        ("Which structure controls many activities of the cell?", ["nucleus"]),
        ("Which structure controls movement of substances into and out of a cell?", ["cell membrane", "membrane"]),
        ("Which organelle is the site of photosynthesis?", ["chloroplast", "chloroplasts"]),
    ],
    ("Biology", "Photosynthesis"): [
        ("Which pigment absorbs light for photosynthesis?", ["chlorophyll"]),
        ("Which gas is used in photosynthesis?", ["carbon dioxide"]),
        ("What carbohydrate is produced during photosynthesis?", ["glucose"]),
        ("What is the energy source for photosynthesis?", ["light", "light energy"]),
    ],
    ("Biology", "Respiration"): [
        ("What process releases energy from glucose?", ["respiration"]),
        ("Which gas is needed for aerobic respiration?", ["oxygen"]),
        ("Name one product of aerobic respiration.", ["carbon dioxide", "water"]),
        ("Where does most aerobic respiration occur in a cell?", ["mitochondria", "mitochondrion"]),
    ],
    ("Chemistry", "Atoms"): [
        ("What particle has a positive charge?", ["proton"]),
        ("What particle has a negative charge?", ["electron"]),
        ("What particle has no charge?", ["neutron"]),
        ("Where are protons and neutrons found?", ["nucleus"]),
    ],
    ("Chemistry", "Elements"): [
        ("What is an element?", ["a substance made of one type of atom"]),
        ("Which element has the symbol O?", ["oxygen"]),
        ("Which element has the symbol H?", ["hydrogen"]),
        ("Where are elements arranged?", ["periodic table"]),
    ],
    ("Chemistry", "Chemical Symbols"): [
        ("What is the chemical symbol for oxygen?", ["O"]),
        ("What is the chemical symbol for hydrogen?", ["H"]),
        ("What is the chemical symbol for carbon?", ["C"]),
        ("What is the chemical symbol for sodium?", ["Na"]),
    ],
    ("Physics", "Electricity"): [
        ("What is the unit of current?", ["ampere", "amp", "A"]),
        ("What is the unit of voltage?", ["volt", "V"]),
        ("What is the unit of resistance?", ["ohm", "Ω"]),
        ("What component provides energy in a simple circuit?", ["cell", "battery"]),
    ],
    ("Physics", "Motion"): [
        ("What is the formula for speed?", ["distance/time", "distance ÷ time"]),
        ("What is the SI unit of speed?", ["m/s", "metres per second"]),
        ("What does acceleration describe?", ["change in velocity"]),
        ("What quantity tells how far an object has travelled?", ["distance"]),
    ],
    ("Physics", "Energy"): [
        ("What is the SI unit of energy?", ["joule", "J"]),
        ("What is the SI unit of power?", ["watt", "W"]),
        ("What does efficiency compare?", ["useful output with total input"]),
        ("Can energy be created or destroyed?", ["no", "No"]),
    ],
}


# ---------------------------------------------------------------------
# Band-specific teaching adjustments
# ---------------------------------------------------------------------

LEVEL_INTRO = {
    "G1_G3": "Use simple language, familiar examples and short steps.",
    "G4_G5": "Build from concrete examples towards simple written methods.",
    "G6_G7": "Use clear reasoning, multi-step examples and correct mathematical/scientific terminology.",
    "F1_F2": "Use formal terminology and introduce structured examination-style reasoning.",
    "F3_F4": "Emphasise method, accuracy, explanation and multi-step application.",
    "F5_F6": "Emphasise advanced reasoning, precision, modelling and examination application.",
}


def _make_example(subject, topic, band):
    if subject == "Maths":
        examples = {
            "G1_G3": f"Start with a familiar {topic.lower()} example. Work one step at a time and check the answer.",
            "G4_G5": f"Set out a {topic.lower()} calculation clearly, identify the operation needed, calculate carefully and check the result.",
            "G6_G7": f"Translate the {topic.lower()} problem into a mathematical operation, show each step and verify the result.",
            "F1_F2": f"Define the quantities involved, select the appropriate {topic.lower()} method, show the working and check the answer.",
            "F3_F4": f"Identify the mathematical structure of the {topic.lower()} problem, apply the relevant method and justify the result.",
            "F5_F6": f"Model the {topic.lower()} problem algebraically or numerically, maintain exact values where appropriate and verify the final result.",
        }
    elif subject == "English":
        examples = {
            "G1_G3": f"Build a short sentence and identify how {topic.lower()} helps the sentence communicate clearly.",
            "G4_G5": f"Read the sentence carefully, identify the {topic.lower()} feature and explain its effect.",
            "G6_G7": f"Identify the {topic.lower()} structure, correct any errors and explain why the chosen form is appropriate.",
            "F1_F2": f"Analyse the {topic.lower()} feature in context and revise the sentence for accuracy.",
            "F3_F4": f"Compare alternative forms of {topic.lower()} and select the most appropriate one for purpose and audience.",
            "F5_F6": f"Analyse and manipulate {topic.lower()} structures precisely, considering meaning, register, purpose and audience.",
        }
    else:
        examples = {
            "G1_G3": f"Use a familiar everyday example to explain {topic.lower()} in simple steps.",
            "G4_G5": f"Identify the main idea in the {topic.lower()} example and explain what happens.",
            "G6_G7": f"Describe the process involved in {topic.lower()} and link the explanation to observable evidence.",
            "F1_F2": f"Define the relevant terms for {topic.lower()}, explain the process and use a suitable scientific example.",
            "F3_F4": f"Apply scientific principles to explain {topic.lower()} and connect the explanation to evidence or calculation.",
            "F5_F6": f"Use precise scientific terminology and quantitative or mechanistic reasoning to analyse {topic.lower()}.",
        }
    return examples[band]


def _make_learn(subject, topic, band):
    focus = FOCUS[subject][topic][band]
    return (
        f"{focus}\n\n"
        f"{LEVEL_INTRO[band]}\n\n"
        f"Lesson approach: begin by defining the key idea, connect it to a "
        f"familiar example, work through the method carefully, then apply it "
        f"to practice questions. Always check units, signs, spelling or "
        f"reasoning where appropriate."
    )


def _make_objective(subject, topic, band):
    return (
        f"By the end of this lesson, the learner should be able to "
        f"understand and apply the main {topic.lower()} ideas appropriate "
        f"to {BAND_NAMES[band]}, explain the method clearly, and answer "
        f"basic examination-style questions accurately."
    )


def _make_practice(subject, topic, band):
    """
    Return four genuinely progressive practice questions for the
    learner's subject, topic and learning band.

    The original PRACTICE dictionary is retained as a baseline, but
    questions are now differentiated by learning band.
    """

    practice = {
        # =============================================================
        # MATHS
        # =============================================================

        ("Maths", "Algebra"): {
            "G1_G3": [
                ("Find the missing number: 5 + __ = 9.", ["4"]),
                ("Find the missing number: __ + 3 = 8.", ["5"]),
                ("If a box contains 4 pencils and you add 2 more, how many pencils are there?", ["6"]),
                ("Continue the pattern: 2, 4, 6, __.", ["8"]),
            ],
            "G4_G5": [
                ("If x = 7, find x + 5.", ["12"]),
                ("If a = 9, find 2a.", ["18"]),
                ("Simplify 4x + 2x.", ["6x"]),
                ("Solve x + 8 = 15.", ["7"]),
            ],
            "G6_G7": [
                ("If x = 4, find 3x + 2.", ["14"]),
                ("Simplify 7a + 3a - 2a.", ["8a"]),
                ("Expand 3(x + 4).", ["3x + 12"]),
                ("Solve 3x + 2 = 14.", ["4"]),
            ],
            "F1_F2": [
                ("Expand 4(x + 3).", ["4x + 12"]),
                ("Simplify 5x + 3 - 2x + 7.", ["3x + 10"]),
                ("Solve 2x + 5 = 17.", ["6"]),
                ("Solve 3(x - 2) = 15.", ["7"]),
            ],
            "F3_F4": [
                ("Factorise 6x + 12.", ["6(x + 2)"]),
                ("Solve simultaneously: x + y = 10 and x - y = 2.", ["x = 6, y = 4"]),
                ("Solve x² - 5x + 6 = 0.", ["x = 2 or x = 3"]),
                ("Simplify (x² - 9)/(x - 3).", ["x + 3"]),
            ],
            "F5_F6": [
                ("Differentiate y = 3x² + 4x - 5.", ["6x + 4"]),
                ("Solve 2x² - 5x - 3 = 0.", ["x = 3 or x = -1/2"]),
                ("If f(x) = 2x + 3, find f(5).", ["13"]),
                ("Solve 1/x + 1/2 = 1.", ["x = 2"]),
            ],
        },

        ("Maths", "Multiplication"): {
            "G1_G3": [
                ("What is 2 × 3?", ["6"]),
                ("What is 4 × 5?", ["20"]),
                ("What is 5 × 6?", ["30"]),
                ("There are 3 bags with 4 apples each. How many apples?", ["12"]),
            ],
            "G4_G5": [
                ("What is 24 × 6?", ["144"]),
                ("What is 35 × 7?", ["245"]),
                ("What is 125 × 4?", ["500"]),
                ("What is 2.5 × 4?", ["10"]),
            ],
            "G6_G7": [
                ("What is 36 × 25?", ["900"]),
                ("Calculate 4.5 × 0.6.", ["2.7"]),
                ("Calculate 3/4 × 8.", ["6"]),
                ("A box contains 24 packets with 15 items each. How many items?", ["360"]),
            ],
            "F1_F2": [
                ("Calculate (-6) × 8.", ["-48"]),
                ("Simplify 3x × 4.", ["12x"]),
                ("Calculate 2/3 × 9/4.", ["3/2", "1.5"]),
                ("Calculate 0.25 × 0.8.", ["0.2"]),
            ],
            "F3_F4": [
                ("Expand 3x(2x + 5).", ["6x² + 15x"]),
                ("Calculate 2.4 × 10⁵.", ["240000"]),
                ("Simplify (2x)(3x²).", ["6x³"]),
                ("A quantity increases from 80 by a factor of 1.25. Find the new value.", ["100"]),
            ],
            "F5_F6": [
                ("Expand (2x + 3)(x - 4).", ["2x² - 5x - 12"]),
                ("Calculate (3 × 10⁴)(2 × 10⁻³).", ["60"]),
                ("If P = 3x and Q = 2x², find PQ.", ["6x³"]),
                ("A value is multiplied by 1.08 each year. Express the value after 3 years as a multiplier.", ["1.08³"]),
            ],
        },

        ("Maths", "Division"): {
            "G1_G3": [
                ("What is 10 ÷ 2?", ["5"]),
                ("What is 12 ÷ 3?", ["4"]),
                ("Share 15 sweets equally among 5 children. How many each?", ["3"]),
                ("What is 20 ÷ 4?", ["5"]),
            ],
            "G4_G5": [
                ("What is 84 ÷ 7?", ["12"]),
                ("What is 144 ÷ 12?", ["12"]),
                ("What is 225 ÷ 5?", ["45"]),
                ("What is 7.2 ÷ 3?", ["2.4"]),
            ],
            "G6_G7": [
                ("Calculate 360 ÷ 24.", ["15"]),
                ("Calculate 4.8 ÷ 0.6.", ["8"]),
                ("Calculate 3/4 ÷ 1/2.", ["3/2", "1.5"]),
                ("A 12 m rope is cut into pieces of 0.75 m. How many pieces?", ["16"]),
            ],
            "F1_F2": [
                ("Calculate (-48) ÷ 6.", ["-8"]),
                ("Simplify 12x² ÷ 3x.", ["4x"]),
                ("Calculate 5/6 ÷ 10/9.", ["3/4"]),
                ("Solve 4x ÷ 2 = 14.", ["7"]),
            ],
            "F3_F4": [
                ("Simplify (12x³)/(3x).", ["4x²"]),
                ("Write 6.4 × 10⁵ ÷ 8 × 10² in standard form.", ["8 × 10²"]),
                ("Divide x² - 9 by x - 3.", ["x + 3"]),
                ("If 3x/4 = 12, find x.", ["16"]),
            ],
            "F5_F6": [
                ("Simplify (6x²y)/(3xy²).", ["2x/y"]),
                ("Evaluate 8 × 10⁶ ÷ 2 × 10³.", ["4 × 10³"]),
                ("Solve 1/x = 0.25.", ["4"]),
                ("If dy/dx = 6x and y(0) = 4, find y.", ["3x² + 4"]),
            ],
        },

        ("Maths", "Geometry"): {
            "G1_G3": [
                ("How many sides does a square have?", ["4"]),
                ("How many sides does a triangle have?", ["3"]),
                ("What shape has no corners and is round?", ["circle"]),
                ("How many corners does a rectangle have?", ["4"]),
            ],
            "G4_G5": [
                ("How many degrees are in a right angle?", ["90", "90°"]),
                ("Find the perimeter of a square with side 6 cm.", ["24 cm", "24"]),
                ("Find the area of a rectangle 5 cm by 4 cm.", ["20 cm²", "20"]),
                ("How many degrees are in a straight angle?", ["180", "180°"]),
            ],
            "G6_G7": [
                ("Find the area of a triangle with base 8 cm and height 5 cm.", ["20 cm²", "20"]),
                ("A square has perimeter 36 cm. Find its side length.", ["9 cm"]),
                ("Find the missing angle in a triangle with angles 50° and 60°.", ["70°", "70"]),
                ("Find the volume of a cuboid measuring 4 cm × 3 cm × 5 cm.", ["60 cm³", "60"]),
            ],
            "F1_F2": [
                ("Find the third angle of a triangle with angles 45° and 65°.", ["70°", "70"]),
                ("Find the circumference of a circle of radius 7 cm using π = 22/7.", ["44 cm", "44"]),
                ("Two parallel lines are crossed by a transversal. If one corresponding angle is 65°, find the other.", ["65°", "65"]),
                ("Find the area of a circle with radius 7 cm using π = 22/7.", ["154 cm²", "154"]),
            ],
            "F3_F4": [
                ("Two similar triangles have corresponding sides 4 cm and 10 cm. What is the scale factor?", ["2.5"]),
                ("A circle has radius 5 cm. Find its area in terms of π.", ["25π"]),
                ("Find the distance between (0,0) and (3,4).", ["5"]),
                ("A right triangle has legs 6 cm and 8 cm. Find the hypotenuse.", ["10 cm", "10"]),
            ],
            "F5_F6": [
                ("Find the exact value of sin 30°.", ["1/2"]),
                ("A right triangle has opposite side 5 and hypotenuse 13. Find sin θ.", ["5/13"]),
                ("Find the gradient of the line through (2,3) and (6,11).", ["2"]),
                ("Prove that the angles in a triangle sum to 180° using a parallel-line argument.", ["180°"]),
            ],
        },

        # =============================================================
        # ENGLISH
        # =============================================================

        ("English", "Grammar"): {
            "G1_G3": [
                ("Identify the noun: 'The dog runs.'", ["dog"]),
                ("Identify the verb: 'The girl sings.'", ["sings"]),
                ("Choose: 'He ___ happy.'", ["is"]),
                ("Write the plural of 'cat'.", ["cats"]),
            ],
            "G4_G5": [
                ("Identify the adjective: 'The tall boy ran.'", ["tall"]),
                ("Choose the correct verb: 'The children ___ playing.'", ["are"]),
                ("Write the plural of 'knife'.", ["knives"]),
                ("Correct the sentence: 'she like apples.'", ["She likes apples."]),
            ],
            "G6_G7": [
                ("Correct the agreement error: 'The group of boys are ready.'", ["The group of boys is ready."]),
                ("Identify the pronoun: 'They visited the museum.'", ["They"]),
                ("Identify the subordinate clause: 'Although it rained, we played.'", ["Although it rained"]),
                ("Correct: 'Neither of the boys were late.'", ["Neither of the boys was late."]),
            ],
            "F1_F2": [
                ("Identify the main clause: 'When the bell rang, the pupils left.'", ["the pupils left"]),
                ("Correct: 'Each of the students have a book.'", ["Each of the students has a book."]),
                ("Change to passive voice: 'The teacher marked the books.'", ["The books were marked by the teacher."]),
                ("Identify the conjunction in: 'Although he was tired, he continued.'", ["Although"]),
            ],
            "F3_F4": [
                ("Rewrite formally: 'The results were really bad.'", ["The results were very poor."]),
                ("Identify the type of clause: 'because the road was flooded'.", ["subordinate clause"]),
                ("Correct the error: 'If I would have known, I would have helped.'", ["If I had known, I would have helped."]),
                ("Change to reported speech: He said, 'I am tired.'", ["He said that he was tired."]),
            ],
            "F5_F6": [
                ("Identify the function of 'which' in: 'The book, which I borrowed, was useful.'", ["relative pronoun"]),
                ("Rewrite using a nominalisation: 'The committee decided to postpone the meeting.'", ["The committee made a decision to postpone the meeting."]),
                ("Identify the grammatical structure: 'Having completed the work, she left.'", ["participial clause"]),
                ("Correct the sentence: 'It is essential that every student submits the form.'", ["It is essential that every student submit the form."]),
            ],
        },

        ("English", "Tenses"): {
            "G1_G3": [
                ("Change 'walk' to the simple past tense.", ["walked"]),
                ("Complete: 'Tomorrow I ___ go to school.'", ["will"]),
                ("Identify the tense: 'She is reading.'", ["present continuous"]),
                ("Complete: 'I ___ football every Saturday.'", ["play"]),
            ],
            "G4_G5": [
                ("Change 'eat' to the simple past tense.", ["ate"]),
                ("Complete: 'They ___ playing yesterday.'", ["were"]),
                ("Identify the tense: 'I have finished my work.'", ["present perfect"]),
                ("Write the future form of 'She sings.'", ["She will sing."]),
            ],
            "G6_G7": [
                ("Identify the tense: 'They had finished before we arrived.'", ["past perfect"]),
                ("Complete: 'She ___ studying when I called.'", ["was"]),
                ("Change to past perfect: 'He eats before school.'", ["He had eaten before school."]),
                ("Correct: 'I have seen him yesterday.'", ["I saw him yesterday."]),
            ],
            "F1_F2": [
                ("Complete: 'By next week, she ___ the course.'", ["will have completed"]),
                ("Identify the tense: 'They had been waiting for an hour.'", ["past perfect continuous"]),
                ("Correct: 'When he arrived, I am sleeping.'", ["When he arrived, I was sleeping."]),
                ("Change to reported speech: She said, 'I will come tomorrow.'", ["She said that she would come the next day."]),
            ],
            "F3_F4": [
                ("Explain the tense in: 'By the time we arrived, the film had started.'", ["past perfect"]),
                ("Rewrite using the present perfect continuous: 'She started studying two hours ago and is still studying.'", ["She has been studying for two hours."]),
                ("Correct: 'If he will arrive early, we will start.'", ["If he arrives early, we will start."]),
                ("Change to passive: 'They have completed the project.'", ["The project has been completed."]),
            ],
            "F5_F6": [
                ("Identify the aspect in: 'She will have been working for five hours.'", ["future perfect continuous"]),
                ("Rewrite to emphasise duration: 'He started living here in 2020 and still lives here.'", ["He has been living here since 2020."]),
                ("Correct: 'Had I knew the answer, I would have told you.'", ["Had I known the answer, I would have told you."]),
                ("Explain the tense choice in: 'The train leaves at 6 tomorrow.'", ["present simple for a scheduled future event"]),
            ],
        },

        ("English", "Sentence Construction"): {
            "G1_G3": [
                ("Complete: 'The dog ___ loudly.'", ["barks"]),
                ("What is the subject in 'The teacher speaks'?", ["teacher"]),
                ("Add the correct punctuation: 'Where are you going'", ["Where are you going?"]),
                ("Put the words in order: 'school / goes / Tino / to'.", ["Tino goes to school."]),
            ],
            "G4_G5": [
                ("Join using 'because': 'I stayed home. I was sick.'", ["I stayed home because I was sick."]),
                ("Identify the subject: 'The young girl opened the door.'", ["The young girl"]),
                ("Join using 'but': 'I was tired. I continued working.'", ["I was tired but I continued working."]),
                ("Add punctuation: 'What a beautiful day'", ["What a beautiful day!"]),
            ],
            "G6_G7": [
                ("Combine using 'although': 'It was raining. We continued playing.'", ["Although it was raining, we continued playing."]),
                ("Identify the subordinate clause: 'Because he was late, he missed the bus.'", ["Because he was late"]),
                ("Write a complex sentence using 'while'.", ["Answers may vary."]),
                ("Correct: 'The boy which won the race was happy.'", ["The boy who won the race was happy."]),
            ],
            "F1_F2": [
                ("Combine using a relative clause: 'I met a woman. She is a doctor.'", ["I met a woman who is a doctor."]),
                ("Identify the main clause: 'Although she was tired, she finished the work.'", ["she finished the work"]),
                ("Rewrite in passive voice: 'The pupils completed the task.'", ["The task was completed by the pupils."]),
                ("Write a compound-complex sentence containing 'although'.", ["Answers may vary."]),
            ],
            "F3_F4": [
                ("Rewrite to avoid repetition: 'The car was old. The car was expensive.'", ["The old car was expensive."]),
                ("Combine using a participial phrase: 'She finished the work. She went home.'", ["Having finished the work, she went home."]),
                ("Identify the relative clause: 'The book that you gave me is excellent.'", ["that you gave me"]),
                ("Rewrite for a formal audience: 'Kids don't like the new rules.'", ["Children do not like the new rules."]),
            ],
            "F5_F6": [
                ("Rewrite using inversion for emphasis: 'I had never seen such a performance.'", ["Never had I seen such a performance."]),
                ("Combine the ideas using a concessive clause: 'The evidence was limited. The conclusion was accepted.'", ["Although the evidence was limited, the conclusion was accepted."]),
                ("Identify the noun phrase: 'The rapid growth of the new company surprised investors.'", ["The rapid growth of the new company"]),
                ("Construct a sentence using a non-finite clause and a main clause.", ["Answers may vary."]),
            ],
        },

        ("English", "Parts of Speech"): {
            "G1_G3": [
                ("What part of speech is 'dog'?", ["noun"]),
                ("What part of speech is 'run'?", ["verb"]),
                ("What part of speech is 'beautiful'?", ["adjective"]),
                ("What part of speech is 'quickly'?", ["adverb"]),
            ],
            "G4_G5": [
                ("Identify the adjective: 'The small house is clean.'", ["small"]),
                ("Identify the adverb: 'She sang beautifully.'", ["beautifully"]),
                ("Identify the pronoun: 'They went home.'", ["They"]),
                ("Identify the conjunction: 'I stayed because it rained.'", ["because"]),
            ],
            "G6_G7": [
                ("What part of speech is 'although'?", ["conjunction"]),
                ("Identify the preposition: 'The book is under the table.'", ["under"]),
                ("What word class is 'carefully'?", ["adverb"]),
                ("Identify the pronoun: 'Everyone enjoyed themselves.'", ["Everyone", "themselves"]),
            ],
            "F1_F2": [
                ("Identify the determiner in: 'Those books are mine.'", ["Those"]),
                ("Identify the modal verb: 'You should study.'", ["should"]),
                ("Identify the conjunction: 'He left because he was tired.'", ["because"]),
                ("Identify the adjective phrase: 'extremely difficult'.", ["extremely difficult"]),
            ],
            "F3_F4": [
                ("Identify the relative pronoun in: 'The student who won was rewarded.'", ["who"]),
                ("Identify the modal auxiliary in: 'They might arrive late.'", ["might"]),
                ("Identify the adverbial phrase in: 'She spoke with great confidence.'", ["with great confidence"]),
                ("Explain the function of 'that' in: 'I know that he is honest.'", ["conjunction"]),
            ],
            "F5_F6": [
                ("Identify the syntactic function of 'the results' in: 'The results surprised the researchers.'", ["subject"]),
                ("Identify the word class of 'although' in a complex sentence.", ["subordinating conjunction"]),
                ("Analyse the function of 'quickly' in: 'The athlete quickly crossed the line.'", ["adverbial"]),
                ("Identify the noun phrase in: 'Several highly trained scientists attended.'", ["Several highly trained scientists"]),
            ],
        },

        ("English", "Vocabulary"): {
            "G1_G3": [
                ("Give a synonym for 'happy'.", ["glad", "joyful", "cheerful"]),
                ("Give an antonym for 'hot'.", ["cold"]),
                ("What is the opposite of 'early'?", ["late"]),
                ("Give a synonym for 'big'.", ["large", "huge"]),
            ],
            "G4_G5": [
                ("Give a synonym for 'brave'.", ["courageous"]),
                ("Give an antonym for 'ancient'.", ["modern"]),
                ("What does the prefix 'un-' usually mean?", ["not"]),
                ("Give a synonym for 'rapid'.", ["fast", "quick"]),
            ],
            "G6_G7": [
                ("What does the suffix '-less' mean?", ["without"]),
                ("Give a synonym for 'accurate'.", ["correct", "precise"]),
                ("Use the word 'essential' in a sentence.", ["Answers may vary."]),
                ("Give an antonym for 'scarce'.", ["abundant", "plentiful"]),
            ],
            "F1_F2": [
                ("What is the difference between 'affect' and 'effect'?", ["affect is usually a verb; effect is usually a noun"]),
                ("Give a formal synonym for 'help'.", ["assist"]),
                ("What does 'ambiguous' mean?", ["having more than one possible meaning"]),
                ("Use 'consequently' correctly in a sentence.", ["Answers may vary."]),
            ],
            "F3_F4": [
                ("Give a synonym for 'significant' suitable for formal writing.", ["important", "substantial"]),
                ("Explain the difference between 'infer' and 'imply'.", ["infer is to draw a conclusion; imply is to suggest"]),
                ("What does 'mitigate' mean?", ["reduce the severity or impact"]),
                ("Use 'nevertheless' in a formal sentence.", ["Answers may vary."]),
            ],
            "F5_F6": [
                ("Define 'juxtaposition'.", ["placing contrasting ideas or elements close together"]),
                ("Give a precise synonym for 'ubiquitous'.", ["widespread", "everywhere"]),
                ("Explain the connotation of the word 'home' compared with 'house'.", ["home suggests belonging or emotional attachment; house refers mainly to the building"]),
                ("Use 'notwithstanding' correctly in a formal sentence.", ["Answers may vary."]),
            ],
        },

        # =============================================================
        # SCIENCE
        # =============================================================

        ("Science", "Human Body"): {
            "G1_G3": [
                ("Which organ pumps blood around the body?", ["heart"]),
                ("Which organ helps us breathe?", ["lungs"]),
                ("Which organ helps us think?", ["brain"]),
                ("Which body part helps us see?", ["eyes"]),
            ],
            "G4_G5": [
                ("What is the main function of the heart?", ["pump blood"]),
                ("What is the main function of the lungs?", ["gas exchange", "breathing"]),
                ("Which organ digests food in the stomach?", ["stomach"]),
                ("Which organ removes waste from the blood to make urine?", ["kidneys"]),
            ],
            "G6_G7": [
                ("What is the main function of red blood cells?", ["carry oxygen"]),
                ("What is the role of the small intestine?", ["digestion and absorption"]),
                ("Which system controls body responses using electrical signals?", ["nervous system"]),
                ("Why does the heart rate increase during exercise?", ["to deliver more oxygen and nutrients to muscles"]),
            ],
            "F1_F2": [
                ("What is the function of haemoglobin?", ["transport oxygen"]),
                ("Where does gas exchange occur in the lungs?", ["alveoli"]),
                ("What is the role of the villi in the small intestine?", ["increase surface area for absorption"]),
                ("Name the main blood vessels carrying blood away from the heart.", ["arteries"]),
            ],
            "F3_F4": [
                ("Explain why alveoli are efficient surfaces for gas exchange.", ["large surface area, thin walls and good blood supply"]),
                ("What is the role of insulin in blood glucose regulation?", ["reduces blood glucose by promoting glucose uptake/storage"]),
                ("Explain how the kidneys help maintain water balance.", ["they regulate water and solute reabsorption"]),
                ("What is homeostasis?", ["maintenance of a stable internal environment"]),
            ],
            "F5_F6": [
                ("Explain how negative feedback maintains homeostasis.", ["a change triggers responses that oppose the original change"]),
                ("Explain the role of ADH in water balance.", ["ADH increases kidney water reabsorption"]),
                ("Describe how oxygen is transported from alveoli to tissues.", ["diffuses into blood, binds haemoglobin and is transported in red blood cells"]),
                ("Explain why tissue respiration increases during exercise.", ["greater energy demand requires increased aerobic respiration"]),
            ],
        },

        ("Science", "Plants"): {
            "G1_G3": [
                ("Which part of a plant absorbs water?", ["root", "roots"]),
                ("Which part usually makes food?", ["leaf", "leaves"]),
                ("What do plants need from sunlight?", ["light"]),
                ("What part holds a plant upright?", ["stem"]),
            ],
            "G4_G5": [
                ("What is the function of roots?", ["absorb water and minerals and anchor the plant"]),
                ("What is the function of the stem?", ["support the plant and transport substances"]),
                ("What is the function of a flower?", ["reproduction"]),
                ("What happens when a seed germinates?", ["it begins to grow"]),
            ],
            "G6_G7": [
                ("What is photosynthesis?", ["the process by which green plants make food using light"]),
                ("Which tissue transports water upwards?", ["xylem"]),
                ("Which tissue transports sugars?", ["phloem"]),
                ("Why are leaves broad and flat?", ["to provide a large surface area for light absorption"]),
            ],
            "F1_F2": [
                ("Write the word equation for photosynthesis.", ["carbon dioxide + water → glucose + oxygen"]),
                ("What is transpiration?", ["loss of water vapour from plant leaves"]),
                ("What is the role of stomata?", ["gas exchange and control of water loss"]),
                ("Which tissue transports mineral ions and water?", ["xylem"]),
            ],
            "F3_F4": [
                ("Explain how stomata balance gas exchange and water loss.", ["they allow gases to enter/leave but can close to reduce water loss"]),
                ("What factors affect the rate of photosynthesis?", ["light intensity, carbon dioxide concentration and temperature"]),
                ("Explain the role of phloem.", ["transports organic nutrients such as sucrose"]),
                ("Why does transpiration increase with higher temperature?", ["water evaporates faster"]),
            ],
            "F5_F6": [
                ("Explain how water moves from roots to leaves.", ["water enters roots and moves through xylem driven by transpiration and water potential gradients"]),
                ("What is the role of guard cells?", ["control stomatal opening and closing"]),
                ("Explain how mineral deficiencies affect plant growth.", ["lack of essential ions disrupts biochemical processes and growth"]),
                ("Describe the pressure-flow mechanism of phloem transport.", ["sugars are loaded into phloem, water enters by osmosis and pressure drives translocation"]),
            ],
        },

        ("Science", "Forces"): {
            "G1_G3": [
                ("What force pulls objects towards Earth?", ["gravity", "gravitational force"]),
                ("What force can slow a moving object when surfaces rub?", ["friction"]),
                ("Can a push change the motion of an object?", ["yes"]),
                ("What is a force?", ["a push or pull"]),
            ],
            "G4_G5": [
                ("What is friction?", ["a force that opposes motion between surfaces"]),
                ("What force keeps us on the ground?", ["gravity"]),
                ("Give one effect a force can have on an object.", ["change its motion", "change its shape"]),
                ("What force acts against a falling object through air?", ["air resistance"]),
            ],
            "G6_G7": [
                ("What is the difference between balanced and unbalanced forces?", ["balanced forces have zero resultant; unbalanced forces have a non-zero resultant"]),
                ("What happens when the resultant force on an object is zero?", ["its motion does not change"]),
                ("What is the unit of force?", ["newton", "N"]),
                ("Why does friction act opposite to motion?", ["it opposes relative movement between surfaces"]),
            ],
            "F1_F2": [
                ("Two forces of 10 N and 6 N act in opposite directions. Find the resultant.", ["4 N"]),
                ("What is the weight of a 5 kg mass if g = 10 N/kg?", ["50 N"]),
                ("Draw or describe the forces acting on a book resting on a table.", ["weight downward and normal reaction upward"]),
                ("What happens to acceleration when the resultant force increases for constant mass?", ["it increases"]),
            ],
            "F3_F4": [
                ("State Newton's second law.", ["F = ma"]),
                ("Calculate the acceleration of a 4 kg object acted on by 20 N.", ["5 m/s²"]),
                ("Calculate the moment of a 10 N force acting 0.5 m from a pivot.", ["5 Nm"]),
                ("What happens to pressure when the same force acts on a smaller area?", ["pressure increases"]),
            ],
            "F5_F6": [
                ("Calculate the resultant force on a 2 kg mass accelerating at 6 m/s².", ["12 N"]),
                ("A 20 N force acts at 30° to a horizontal surface. Find its horizontal component.", ["10√3 N"]),
                ("Explain the condition for rotational equilibrium.", ["clockwise moments equal anticlockwise moments"]),
                ("A car accelerates from 10 to 30 m/s in 5 s. Find its acceleration.", ["4 m/s²"]),
            ],
        },

        ("Science", "Matter"): {
            "G1_G3": [
                ("Name the three common states of matter.", ["solid, liquid and gas"]),
                ("Which state has a fixed shape?", ["solid"]),
                ("What happens to ice when it melts?", ["it becomes liquid"]),
                ("What is matter made of?", ["particles"]),
            ],
            "G4_G5": [
                ("What happens when water freezes?", ["it changes from liquid to solid"]),
                ("Which state takes the shape of its container but keeps a fixed volume?", ["liquid"]),
                ("Which state fills its container?", ["gas"]),
                ("What happens to water when it boils?", ["it changes from liquid to gas"]),
            ],
            "G6_G7": [
                ("How are particles arranged in a solid?", ["closely packed in fixed positions"]),
                ("Why can gases be compressed?", ["their particles are far apart"]),
                ("What happens to particles when a substance is heated?", ["they gain energy and move faster"]),
                ("What is diffusion?", ["movement of particles from high concentration to low concentration"]),
            ],
            "F1_F2": [
                ("Use the particle model to explain melting.", ["particles gain energy and leave their fixed positions"]),
                ("Why does gas pressure increase when temperature increases at constant volume?", ["particles move faster and collide more frequently/forcefully"]),
                ("Explain diffusion in terms of particle motion.", ["particles move randomly from higher to lower concentration"]),
                ("What is the difference between evaporation and boiling?", ["evaporation occurs at the surface at any temperature; boiling occurs throughout at boiling point"]),
            ],
            "F3_F4": [
                ("Why does increasing temperature increase the rate of diffusion?", ["particles have greater kinetic energy and move faster"]),
                ("Explain why a gas exerts pressure.", ["moving particles collide with container walls"]),
                ("What happens to gas volume when pressure increases at constant temperature?", ["volume decreases"]),
                ("Explain why evaporation causes cooling.", ["higher-energy particles escape, lowering average kinetic energy"]),
            ],
            "F5_F6": [
                ("State the ideal gas relationship between pressure, volume and temperature.", ["PV = nRT"]),
                ("Explain Brownian motion using kinetic theory.", ["random motion results from collisions with microscopic particles"]),
                ("Why does real gas behaviour differ from the ideal model at high pressure?", ["intermolecular forces and finite particle volume become significant"]),
                ("Explain why absolute temperature is used in gas-law calculations.", ["it is proportional to average molecular kinetic energy"]),
            ],
        },

        # =============================================================
        # BIOLOGY
        # =============================================================

        ("Biology", "Cells"): {
            "G1_G3": [
                ("What is the basic unit of life?", ["cell"]),
                ("What controls many activities inside a cell?", ["nucleus"]),
                ("Which part surrounds a cell?", ["cell membrane"]),
                ("What is a group of similar cells called?", ["tissue"]),
            ],
            "G4_G5": [
                ("Name one structure found in plant cells but not animal cells.", ["cell wall", "chloroplast", "large vacuole"]),
                ("What is the function of the nucleus?", ["controls cell activities"]),
                ("What is the function of the cell membrane?", ["controls movement of substances in and out"]),
                ("What is the function of chloroplasts?", ["photosynthesis"]),
            ],
            "G6_G7": [
                ("Give two differences between plant and animal cells.", ["plant cells have cell wall/chloroplast/large vacuole"]),
                ("What is a specialised cell?", ["a cell adapted to perform a particular function"]),
                ("Give one adaptation of a red blood cell.", ["biconcave shape", "no nucleus", "contains haemoglobin"]),
                ("Why do root hair cells have long extensions?", ["to increase surface area for absorption"]),
            ],
            "F1_F2": [
                ("What is the function of mitochondria?", ["site of aerobic respiration"]),
                ("What is the function of ribosomes?", ["protein synthesis"]),
                ("What is magnification?", ["image size divided by actual size"]),
                ("Why is a stain used when viewing cells under a microscope?", ["to increase contrast"]),
            ],
            "F3_F4": [
                ("Describe the role of the cell membrane in transport.", ["controls movement of substances into and out of the cell"]),
                ("What is mitosis?", ["cell division producing genetically identical cells"]),
                ("Compare diffusion and osmosis.", ["diffusion is particle movement down a concentration gradient; osmosis is water movement through a partially permeable membrane"]),
                ("What is active transport?", ["movement against a concentration gradient using energy"]),
            ],
            "F5_F6": [
                ("Explain the fluid mosaic model of the cell membrane.", ["phospholipid bilayer containing proteins and other components"]),
                ("Explain how membrane proteins contribute to transport.", ["channels/carriers facilitate movement and pumps can use ATP"]),
                ("Why does increasing surface area to volume ratio affect exchange efficiency?", ["larger relative surface area allows faster exchange"]),
                ("Explain how DNA controls cell function.", ["DNA contains genes coding for proteins that determine cellular structure and processes"]),
            ],
        },

        ("Biology", "Photosynthesis"): {
            "G1_G3": [
                ("What do plants need from sunlight?", ["light energy"]),
                ("Which gas do plants take in for photosynthesis?", ["carbon dioxide"]),
                ("What substance do roots absorb for photosynthesis?", ["water"]),
                ("Where does photosynthesis mainly occur?", ["leaves"]),
            ],
            "G4_G5": [
                ("What is photosynthesis?", ["the process by which green plants make food using light"]),
                ("Which pigment absorbs light?", ["chlorophyll"]),
                ("Which gas is released during photosynthesis?", ["oxygen"]),
                ("What food is made during photosynthesis?", ["glucose"]),
            ],
            "G6_G7": [
                ("State the word equation for photosynthesis.", ["carbon dioxide + water → glucose + oxygen"]),
                ("What is the role of chlorophyll?", ["absorbs light energy"]),
                ("Why is light necessary for photosynthesis?", ["provides energy"]),
                ("What happens to glucose made by photosynthesis?", ["it may be used for respiration or converted/stored as starch and other substances"]),
            ],
            "F1_F2": [
                ("Write the balanced chemical equation for photosynthesis.", ["6CO2 + 6H2O → C6H12O6 + 6O2"]),
                ("Name three factors affecting the rate of photosynthesis.", ["light intensity, carbon dioxide concentration, temperature"]),
                ("Why is starch used as a test for photosynthesis?", ["glucose is converted to starch and starch can be detected with iodine"]),
                ("Why must a plant be destarched before an experiment?", ["to remove stored starch"]),
            ],
            "F3_F4": [
                ("What is a limiting factor?", ["a factor that restricts the rate when it is in shortest effective supply"]),
                ("Why does increasing light intensity eventually stop increasing photosynthesis?", ["another factor becomes limiting"]),
                ("Describe how a light-intensity experiment can measure photosynthesis.", ["measure oxygen production while changing light intensity and controlling other variables"]),
                ("Why does very high temperature reduce photosynthesis?", ["enzymes involved can denature"]),
            ],
            "F5_F6": [
                ("What is photophosphorylation?", ["production of ATP using light energy during photosynthesis"]),
                ("What is the role of ATP in the Calvin cycle?", ["provides energy for carbon fixation/reduction reactions"]),
                ("Explain how carbon dioxide concentration can limit photosynthesis.", ["CO2 is a substrate for carbon fixation, so low concentration limits the rate"]),
                ("Why can excessive light damage photosynthetic systems?", ["it can cause photoinhibition and oxidative damage"]),
            ],
        },

        ("Biology", "Respiration"): {
            "G1_G3": [
                ("What process releases energy from food?", ["respiration"]),
                ("What gas is needed for aerobic respiration?", ["oxygen"]),
                ("Why do living things need energy?", ["growth, movement and life processes"]),
                ("Where does respiration happen?", ["cells"]),
            ],
            "G4_G5": [
                ("What is respiration?", ["the process of releasing energy from food"]),
                ("What is aerobic respiration?", ["respiration using oxygen"]),
                ("Name one product of aerobic respiration.", ["carbon dioxide", "water"]),
                ("Which organ supplies oxygen to the blood?", ["lungs"]),
            ],
            "G6_G7": [
                ("Write the word equation for aerobic respiration.", ["glucose + oxygen → carbon dioxide + water + energy"]),
                ("What is the difference between aerobic and anaerobic respiration?", ["aerobic uses oxygen; anaerobic does not"]),
                ("Why does breathing rate increase during exercise?", ["to supply more oxygen and remove carbon dioxide"]),
                ("Where does most aerobic respiration occur in a cell?", ["mitochondria"]),
            ],
            "F1_F2": [
                ("Write the chemical equation for aerobic respiration.", ["C6H12O6 + 6O2 → 6CO2 + 6H2O + energy"]),
                ("What is produced during anaerobic respiration in muscles?", ["lactic acid"]),
                ("Why does anaerobic respiration release less energy?", ["glucose is incompletely broken down"]),
                ("What is oxygen debt?", ["extra oxygen needed after exercise to process accumulated products and restore normal conditions"]),
            ],
            "F3_F4": [
                ("Where does glycolysis occur?", ["cytoplasm"]),
                ("What is the role of mitochondria in aerobic respiration?", ["site of Krebs cycle and oxidative phosphorylation"]),
                ("Why does lactic acid accumulate during intense exercise?", ["oxygen supply is insufficient for the energy demand"]),
                ("Explain why breathing remains high after strenuous exercise.", ["to repay oxygen debt and restore normal conditions"]),
            ],
            "F5_F6": [
                ("What is the role of NAD in respiration?", ["it carries hydrogen/electrons in redox reactions"]),
                ("Where does the electron transport chain occur?", ["inner mitochondrial membrane"]),
                ("How is ATP produced during oxidative phosphorylation?", ["proton gradient drives ATP synthase"]),
                ("Why does aerobic respiration yield more ATP than anaerobic respiration?", ["glucose is more completely oxidised"]),
            ],
        },

        # =============================================================
        # CHEMISTRY
        # =============================================================

        ("Chemistry", "Atoms"): {
            "G1_G3": [
                ("What are materials made from?", ["tiny particles"]),
                ("What is an atom?", ["a tiny building block of matter"]),
                ("Name one particle found inside an atom.", ["proton", "neutron", "electron"]),
                ("Where is the centre of an atom?", ["nucleus"]),
            ],
            "G4_G5": [
                ("What is an atom?", ["the basic building block of an element"]),
                ("What charge does a proton have?", ["positive"]),
                ("What charge does an electron have?", ["negative"]),
                ("What charge does a neutron have?", ["no charge", "neutral"]),
            ],
            "G6_G7": [
                ("Where are protons and neutrons found?", ["nucleus"]),
                ("Where are electrons found?", ["around the nucleus"]),
                ("What determines the identity of an element?", ["number of protons"]),
                ("What is the atomic number?", ["number of protons"]),
            ],
            "F1_F2": [
                ("An atom has atomic number 11. How many protons does it have?", ["11"]),
                ("An atom has 17 protons and 18 neutrons. What is its mass number?", ["35"]),
                ("How many electrons does a neutral atom with 12 protons have?", ["12"]),
                ("What is an isotope?", ["atoms of the same element with different numbers of neutrons"]),
            ],
            "F3_F4": [
                ("What is an ion?", ["a charged particle formed when electrons are gained or lost"]),
                ("How many electrons are in Na⁺ if sodium has atomic number 11?", ["10"]),
                ("Why do isotopes of an element have similar chemical properties?", ["they have the same electron arrangement"]),
                ("Write the electron arrangement of chlorine, atomic number 17.", ["2,8,7"]),
            ],
            "F5_F6": [
                ("Explain why successive ionisation energies generally increase.", ["more energy is required to remove electrons increasingly close to the nucleus"]),
                ("What is the ground-state electron configuration of sodium?", ["1s² 2s² 2p⁶ 3s¹"]),
                ("Why do isotopes have different masses?", ["they contain different numbers of neutrons"]),
                ("Explain the relationship between nuclear charge and atomic radius across a period.", ["increasing nuclear charge pulls electrons closer, reducing atomic radius"]),
            ],
        },

        ("Chemistry", "Elements"): {
            "G1_G3": [
                ("What is an element?", ["a substance made of one type of atom"]),
                ("Is oxygen an element?", ["yes"]),
                ("Which element has the symbol H?", ["hydrogen"]),
                ("Which element has the symbol O?", ["oxygen"]),
            ],
            "G4_G5": [
                ("What is an element made of?", ["one type of atom"]),
                ("Which element has the symbol C?", ["carbon"]),
                ("Which element has the symbol Na?", ["sodium"]),
                ("Where are elements arranged?", ["periodic table"]),
            ],
            "G6_G7": [
                ("What information does the periodic table provide?", ["elements arranged by atomic number and properties"]),
                ("What is a group in the periodic table?", ["a vertical column"]),
                ("What is a period?", ["a horizontal row"]),
                ("Why do elements in the same group have similar properties?", ["they have similar outer electron arrangements"]),
            ],
            "F1_F2": [
                ("Why do elements in Group 1 become more reactive down the group?", ["outer electron is farther from nucleus and easier to lose"]),
                ("What type of elements are found on the left side of the periodic table?", ["mostly metals"]),
                ("What type of elements are found on the right side?", ["mostly non-metals"]),
                ("What determines an element's position in the periodic table?", ["atomic number"]),
            ],
            "F3_F4": [
                ("Explain the trend in atomic radius across a period.", ["it generally decreases due to increasing nuclear charge"]),
                ("Why are noble gases unreactive?", ["their outer electron shells are full"]),
                ("Predict the ion formed by magnesium.", ["Mg²⁺"]),
                ("Why does Group 7 reactivity decrease down the group?", ["attraction for an incoming electron decreases with distance and shielding"]),
            ],
            "F5_F6": [
                ("Explain periodicity in terms of electron configuration.", ["properties recur as outer electron configurations repeat"]),
                ("Why does first ionisation energy generally increase across a period?", ["nuclear charge increases while electrons enter the same shell"]),
                ("Explain the anomalous ionisation energies between some adjacent elements.", ["subshell energies and electron pairing affect stability"]),
                ("Predict the bonding behaviour of an element from its valence electrons.", ["valence configuration indicates likely electron loss, gain or sharing"]),
            ],
        },

        ("Chemistry", "Chemical Symbols"): {
            "G1_G3": [
                ("What is the symbol for oxygen?", ["O"]),
                ("What is the symbol for hydrogen?", ["H"]),
                ("What is the symbol for carbon?", ["C"]),
                ("What is the symbol for sodium?", ["Na"]),
            ],
            "G4_G5": [
                ("Write the symbol for iron.", ["Fe"]),
                ("Write the symbol for calcium.", ["Ca"]),
                ("Write the symbol for magnesium.", ["Mg"]),
                ("Write the symbol for chlorine.", ["Cl"]),
            ],
            "G6_G7": [
                ("What does H₂ mean?", ["two hydrogen atoms", "a molecule containing two hydrogen atoms"]),
                ("What does O₂ mean?", ["two oxygen atoms", "a molecule containing two oxygen atoms"]),
                ("What does CO₂ represent?", ["carbon dioxide"]),
                ("How many oxygen atoms are in H₂O?", ["1"]),
            ],
            "F1_F2": [
                ("Write the formula for magnesium oxide.", ["MgO"]),
                ("Write the formula for sodium chloride.", ["NaCl"]),
                ("How many atoms are represented by H₂SO₄?", ["7"]),
                ("Write the formula for calcium carbonate.", ["CaCO₃"]),
            ],
            "F3_F4": [
                ("Balance: H₂ + O₂ → H₂O.", ["2H₂ + O₂ → 2H₂O"]),
                ("Balance: Mg + O₂ → MgO.", ["2Mg + O₂ → 2MgO"]),
                ("What does the coefficient 3 in 3CO₂ mean?", ["three molecules of carbon dioxide"]),
                ("Write the formula for aluminium oxide.", ["Al₂O₃"]),
            ],
            "F5_F6": [
                ("Balance: C₃H₈ + O₂ → CO₂ + H₂O.", ["C₃H₈ + 5O₂ → 3CO₂ + 4H₂O"]),
                ("Calculate the relative formula mass of H₂SO₄.", ["98"]),
                ("How many moles are present in 18 g of H₂O? (Mr = 18)", ["1 mol"]),
                ("Write the ionic formula for calcium nitrate.", ["Ca(NO₃)₂"]),
            ],
        },

        # =============================================================
        # PHYSICS
        # =============================================================

        ("Physics", "Electricity"): {
            "G1_G3": [
                ("What provides energy in a simple circuit?", ["cell", "battery"]),
                ("What component can turn a circuit on and off?", ["switch"]),
                ("What happens when a circuit is complete?", ["current can flow"]),
                ("Name one electrical appliance used at home.", ["Answers may vary."]),
            ],
            "G4_G5": [
                ("What is the unit of current?", ["ampere", "amp", "A"]),
                ("What is the unit of voltage?", ["volt", "V"]),
                ("What component provides electrical energy?", ["cell", "battery"]),
                ("What material is usually used for electrical wires?", ["copper"]),
            ],
            "G6_G7": [
                ("What is resistance?", ["opposition to the flow of current"]),
                ("What happens to current if resistance increases at constant voltage?", ["it decreases"]),
                ("State the relationship V = IR.", ["voltage = current × resistance"]),
                ("What is the unit of resistance?", ["ohm", "Ω"]),
            ],
            "F1_F2": [
                ("Calculate the current through a 6 Ω resistor connected to 12 V.", ["2 A"]),
                ("Calculate voltage when I = 3 A and R = 4 Ω.", ["12 V"]),
                ("What is the difference between series and parallel circuits?", ["series has one path; parallel has multiple branches"]),
                ("What happens to total resistance when resistors are added in series?", ["it increases"]),
            ],
            "F3_F4": [
                ("Calculate the resistance of a device using 24 V and 3 A.", ["8 Ω"]),
                ("Two 6 Ω resistors are connected in series. Find total resistance.", ["12 Ω"]),
                ("Two 6 Ω resistors are connected in parallel. Find total resistance.", ["3 Ω"]),
                ("Calculate power for a device operating at 12 V and 2 A.", ["24 W"]),
            ],
            "F5_F6": [
                ("Calculate the energy transferred by a 100 W device operating for 60 s.", ["6000 J"]),
                ("A resistor has R = 10 Ω and current 2 A. Find its power.", ["40 W"]),
                ("Explain why electrical power can be calculated using P = I²R.", ["substitute V = IR into P = VI"]),
                ("Calculate the total resistance of 4 Ω and 6 Ω resistors in parallel.", ["2.4 Ω"]),
            ],
        },

        ("Physics", "Motion"): {
            "G1_G3": [
                ("What does it mean when an object is moving?", ["its position is changing"]),
                ("Which is faster: a walking person or a racing car?", ["racing car"]),
                ("What can make a moving object slow down?", ["friction", "a force"]),
                ("What instrument can measure time?", ["clock", "stopwatch"]),
            ],
            "G4_G5": [
                ("What is speed?", ["distance travelled per unit time"]),
                ("Which object has greater speed: 100 m in 10 s or 100 m in 20 s?", ["100 m in 10 s"]),
                ("What is the SI unit of speed?", ["m/s", "metres per second"]),
                ("What happens to speed when an object slows down?", ["it decreases"]),
            ],
            "G6_G7": [
                ("Calculate the speed of an object travelling 100 m in 20 s.", ["5 m/s"]),
                ("How far does an object travel at 4 m/s for 10 s?", ["40 m"]),
                ("What does a distance-time graph show?", ["how distance changes with time"]),
                ("What does a horizontal line on a distance-time graph represent?", ["stationary"]),
            ],
            "F1_F2": [
                ("Calculate speed when distance = 150 m and time = 30 s.", ["5 m/s"]),
                ("Calculate distance travelled at 12 m/s for 8 s.", ["96 m"]),
                ("Calculate time taken to travel 200 m at 10 m/s.", ["20 s"]),
                ("What does the gradient of a distance-time graph represent?", ["speed"]),
            ],
            "F3_F4": [
                ("Calculate acceleration from 5 m/s to 25 m/s in 4 s.", ["5 m/s²"]),
                ("What does the gradient of a velocity-time graph represent?", ["acceleration"]),
                ("What does the area under a velocity-time graph represent?", ["displacement"]),
                ("A car travels at 20 m/s for 10 s. What distance does it cover?", ["200 m"]),
            ],
            "F5_F6": [
                ("An object starts from rest and accelerates at 3 m/s² for 8 s. Find its final velocity.", ["24 m/s"]),
                ("Using s = ut + 1/2at², find displacement for u=5 m/s, a=2 m/s², t=4 s.", ["36 m"]),
                ("An object travels at constant velocity. What is its acceleration?", ["0 m/s²"]),
                ("Explain the difference between speed and velocity.", ["speed is scalar; velocity is speed in a specified direction"]),
            ],
        },

        ("Physics", "Energy"): {
            "G1_G3": [
                ("Name one form of energy.", ["light", "heat", "sound", "movement"]),
                ("What type of energy is stored in food?", ["chemical"]),
                ("What type of energy comes from the Sun?", ["light", "solar"]),
                ("Can moving objects have energy?", ["yes"]),
            ],
            "G4_G5": [
                ("What is the SI unit of energy?", ["joule", "J"]),
                ("Name two forms of energy.", ["Answers may vary."]),
                ("What happens to energy when a lamp is switched on?", ["electrical energy is transferred to light and heat"]),
                ("What is energy transfer?", ["movement of energy from one store/form to another"]),
            ],
            "G6_G7": [
                ("State the principle of conservation of energy.", ["energy cannot be created or destroyed, only transferred"]),
                ("What is a useful energy transfer in a torch?", ["chemical to electrical to light"]),
                ("What happens to wasted energy?", ["it is usually transferred to the surroundings, often as heat"]),
                ("What is the unit of power?", ["watt", "W"]),
            ],
            "F1_F2": [
                ("Calculate work done when a 20 N force moves an object 5 m.", ["100 J"]),
                ("Calculate power when 600 J is transferred in 10 s.", ["60 W"]),
                ("What is efficiency?", ["useful output energy divided by total input energy"]),
                ("Calculate kinetic energy of a 2 kg object moving at 3 m/s.", ["9 J"]),
            ],
            "F3_F4": [
                ("Calculate gravitational potential energy of a 5 kg object raised 4 m. Take g=10 N/kg.", ["200 J"]),
                ("Calculate kinetic energy of a 4 kg object moving at 5 m/s.", ["50 J"]),
                ("A machine takes 500 J and produces 350 J useful output. Find efficiency.", ["70%"]),
                ("Calculate power when 2400 J is transferred in 30 s.", ["80 W"]),
            ],
            "F5_F6": [
                ("A motor lifts 50 kg through 10 m in 5 s. Take g=10 N/kg. Find power.", ["1000 W"]),
                ("A machine has input power 2 kW and efficiency 75%. Find useful output power.", ["1.5 kW"]),
                ("Explain why no real energy transfer is 100% efficient.", ["some energy is dissipated to the surroundings, commonly as heat or sound"]),
                ("A 2 kg object falls through 5 m. Ignoring air resistance, calculate the change in gravitational potential energy using g=9.8 N/kg.", ["98 J"]),
            ],
        },
    }

    # Use the band-specific bank where available.
    band_set = practice.get((subject, topic), {}).get(band)

    if band_set is not None:
        return [
            {
                "question": q,
                "answers": list(a),
            }
            for q, a in band_set
        ]

    # Safe fallback to the original baseline.
    source = PRACTICE[(subject, topic)]
    return [
        {
            "question": q,
            "answers": list(a),
        }
        for q, a in source
    ]

def _build_curriculum():
    result = {}

    for subject, topics in FOCUS.items():
        for topic, bands in topics.items():
            key_terms = KEY_TERMS.get(
                topic,
                [topic.lower(), "example", "method", "application", "accuracy"],
            )

            for band in BANDS:
                result[(subject, topic, band)] = {
                    "title": f"{topic}: {BAND_NAMES[band]}",
                    "objective": _make_objective(subject, topic, band),
                    "key_terms": list(key_terms),
                    "learn": _make_learn(subject, topic, band),
                    "example": _make_example(subject, topic, band),
                    "practice": _make_practice(subject, topic, band),
                    "_curriculum": True,
                    "_subject": subject,
                    "_topic": topic,
                    "_band": band,
                }

    return result


CURRICULUM_EXPANSION = _build_curriculum()

# Convert the three-part storage key used above into the structure
# expected by the existing CURRICULUM engine:
#
# CURRICULUM[(subject, topic)] = {
#     band: {...}
# }
#
_EXPANDED = {}

for (_subject, _topic, _band), _lesson in CURRICULUM_EXPANSION.items():
    _EXPANDED.setdefault((_subject, _topic), {})[_band] = _lesson

CURRICULUM_EXPANSION = _EXPANDED


if __name__ == "__main__":
    topics = sum(len(v) for v in CURRICULUM_EXPANSION.values())
    modules = sum(
        len(bands)
        for bands in CURRICULUM_EXPANSION.values()
    )

    print("CURRICULUM EXPANSION READY")
    print(f"Topics: {topics}")
    print(f"Modules: {modules}")
