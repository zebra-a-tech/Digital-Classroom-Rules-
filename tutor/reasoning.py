import re

SUBJECT_TOPICS = {
    "Maths": {
        "algebra": ["equation", "equations", "algebra", "unknown", "solve for x", "variable"],
        "fractions": ["fraction", "fractions", "numerator", "denominator"],
        "percentages": ["percentage", "percent", "%"],
        "multiplication": ["multiply", "multiplication", "times"],
        "division": ["divide", "division", "quotient"],
        "geometry": ["geometry", "area", "perimeter", "triangle", "rectangle", "circle", "angle"],
    },
    "English": {
        "grammar": ["grammar", "noun", "verb", "adjective", "adverb", "pronoun"],
        "tenses": ["tense", "past tense", "present tense", "future tense"],
        "sentence construction": ["sentence construction", "construct a sentence"],
        "vocabulary": ["vocabulary", "meaning of the word", "synonym", "antonym"],
    },
    "Science": {
        "human body": ["human body", "heart", "lungs", "blood", "digest"],
        "plants": ["plant", "plants", "photosynthesis"],
        "forces": ["force", "forces", "gravity", "friction"],
        "matter": ["matter", "solid", "liquid", "gas"],
    },
    "Geography": {
        "erosion": ["erosion", "soil erosion"],
        "weather": ["weather", "rainfall", "temperature", "weathering"],
        "climate": ["climate", "climatic"],
        "rivers": ["river", "rivers", "drainage"],
        "population": ["population", "migration", "population density"],
        "maps": ["map", "maps", "scale", "direction", "grid reference"],
    },
    "History": {
        "sources": ["historical source", "primary source", "secondary source"],
        "colonialism": ["colonialism", "colonial", "colonisation", "colonization"],
        "independence": ["independence", "liberation"],
    },
    "Biology": {
        "cells": ["cell", "cells", "cell structure"],
        "photosynthesis": ["photosynthesis", "chlorophyll"],
        "respiration": ["respiration", "aerobic respiration", "anaerobic respiration"],
        "human body": ["human body", "organ", "organs"],
    },
    "Chemistry": {
        "atoms": ["atom", "atoms", "electron", "proton", "neutron"],
        "elements": ["element", "elements", "periodic table"],
        "chemical symbols": ["chemical symbol", "chemical symbols"],
        "acids": ["acid", "acids", "alkali", "alkalis", "ph scale"],
    },
    "Physics": {
        "forces": ["force", "gravity", "friction"],
        "motion": ["motion", "speed", "velocity", "distance"],
        "energy": ["energy", "kinetic", "potential"],
        "electricity": ["electricity", "electric current", "voltage", "circuit"],
    },
    "Economics": {
        "scarcity": ["scarcity", "limited resources", "shortage"],
        "supply and demand": ["supply", "demand", "equilibrium"],
        "markets": ["market", "consumer", "producer"],
        "gdp": ["gdp", "gross domestic product"],
    },
    "Accounting": {
        "accounting equation": ["accounting equation", "assets", "liabilities", "capital"],
        "cash book": ["cash book", "cashbook"],
        "ledger": ["ledger", "debit", "credit"],
    },
    "Social Studies": {
        "family": ["family", "families"],
        "community": ["community", "communities"],
        "citizenship": ["citizen", "citizenship", "rights", "responsibilities"],
    },
}

DEFINITIONS = {
    ("Maths", "algebra"): (
        "An equation is a mathematical statement showing that two expressions "
        "are equal. It often contains an unknown represented by a letter such as x."
    ),
    ("Maths", "fractions"): (
        "A fraction represents a part of a whole. The numerator is the top number "
        "and the denominator is the bottom number."
    ),
    ("Maths", "percentages"): (
        "A percentage is a part expressed out of 100. For example, 25% means 25 out of 100."
    ),
    ("Maths", "multiplication"): (
        "Multiplication is a way of finding the total of equal groups. "
        "For example, 4 × 3 means 4 groups of 3, giving 12."
    ),
    ("Maths", "division"): (
        "Division means sharing a quantity into equal groups or finding how many "
        "times one number fits into another."
    ),
    ("Maths", "geometry"): (
        "Geometry is the branch of mathematics concerned with shapes, sizes, "
        "angles, measurements and space."
    ),
    ("Geography", "erosion"): (
        "Erosion is the wearing away and removal of soil or rock by agents such "
        "as moving water, wind, ice or waves."
    ),
    ("Geography", "weather"): (
        "Weather is the condition of the atmosphere at a particular place and "
        "time, including temperature, rainfall, wind and humidity."
    ),
    ("Geography", "climate"): (
        "Climate is the long-term pattern of weather experienced in a place, "
        "usually measured over many years."
    ),
    ("Biology", "photosynthesis"): (
        "Photosynthesis is the process by which green plants make food using "
        "light energy. The plant uses carbon dioxide and water, and oxygen is released."
    ),
    ("Biology", "cells"): (
        "A cell is the basic structural and functional unit of a living organism."
    ),
    ("Biology", "respiration"): (
        "Respiration is the process by which cells release energy from food."
    ),
    ("Chemistry", "atoms"): (
        "An atom is the smallest unit of an element that retains the properties "
        "of that element. It contains protons, neutrons and electrons."
    ),
    ("Chemistry", "elements"): (
        "An element is a pure substance made from only one type of atom."
    ),
    ("Physics", "force"): (
        "A force is a push or pull that can change the motion, direction or shape "
        "of an object."
    ),
    ("Physics", "motion"): (
        "Motion is a change in the position of an object over time."
    ),
    ("Physics", "energy"): (
        "Energy is the ability to do work or cause change."
    ),
    ("Physics", "electricity"): (
        "Electricity involves the movement or presence of electric charge. "
        "Electric current is the flow of electric charge."
    ),
    ("Economics", "scarcity"): (
        "Scarcity means that resources are limited while human wants are unlimited."
    ),
    ("Economics", "gdp"): (
        "GDP, or Gross Domestic Product, is the total monetary value of final goods "
        "and services produced within an economy during a specified period."
    ),
    ("Accounting", "accounting equation"): (
        "The accounting equation states that Assets = Capital + Liabilities."
    ),
    ("Accounting", "ledger"): (
        "A ledger is a record where transactions are classified into individual accounts."
    ),
    ("History", "colonialism"): (
        "Colonialism is a system in which one country establishes control over "
        "another territory or people."
    ),
    ("History", "independence"): (
        "Independence means a country has gained the ability to govern itself "
        "without external political control."
    ),
    ("Social Studies", "citizenship"): (
        "Citizenship is the status of belonging to a country, together with the "
        "rights and responsibilities associated with that status."
    ),
}

def normalize(text):
    text = str(text or "").lower()
    text = re.sub(r"\s+", " ", text).strip()
    return text

def detect_question(text):
    text = normalize(text)

    if re.search(r"\b(what is|what are|define|definition of|meaning of)\b", text):
        return "definition"

    if re.search(r"\b(solve|calculate|work out|find|evaluate)\b", text):
        return "problem"

    if re.search(r"\b(explain|how does|how do|why does|why do)\b", text):
        return "explanation"

    if "difference between" in text or "compare" in text:
        return "comparison"

    return "general"

def detect_subject_topic(message):
    text = normalize(message)
    matches = []

    # Specialist subjects get priority when a keyword is shared
    # with a broader subject. This prevents questions such as
    # "What is photosynthesis?" from being classified only as Science.
    specialist_keywords = {
        "Biology": {
            "photosynthesis", "chlorophyll", "cell", "cells",
            "respiration", "mitosis", "meiosis", "organism"
        },
        "Chemistry": {
            "atom", "atoms", "electron", "electrons", "proton",
            "protons", "neutron", "neutrons", "periodic table",
            "chemical symbol", "chemical symbols"
        },
        "Physics": {
            "voltage", "current", "resistance", "velocity",
            "acceleration", "kinetic", "potential energy",
            "electric circuit", "electricity"
        }
    }

    for subject, topics in SUBJECT_TOPICS.items():
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in text:
                    score = len(keyword)

                    # Strong bonus for specialist subject terminology.
                    if keyword in specialist_keywords.get(subject, set()):
                        score += 1000

                    matches.append((score, subject, topic, keyword))

    if not matches:
        return None, None

    matches.sort(key=lambda item: (item[0], len(item[2])), reverse=True)
    _, subject, topic, _ = matches[0]
    return subject, topic


def answer_question(subject, topic, message, grade=None):
    key = (subject, topic)

    # Use the built-in reasoning definitions first.
    if key in DEFINITIONS:
        return DEFINITIONS[key]

    # Then use the structured tutor lessons so recognized topics
    # can still be taught even when no short definition exists.
    try:
        from tutor.intelligence import find_lesson

        lesson = find_lesson(subject, topic)
        if lesson:
            parts = []

            explanation = lesson.get("explanation")
            example = lesson.get("example")

            if explanation:
                parts.append(str(explanation))

            if example:
                parts.append("Example: " + str(example))

            if parts:
                return "\n\n".join(parts)
    except Exception:
        pass

    # Simple algebra problem solving remains available.
    if subject == "Maths" and topic == "algebra":
        m = re.search(
            r"(?:(\\d+)?)x\\s*([+-])\\s*(\\d+)\\s*=\\s*(\\d+)",
            normalize(message)
        )

        if m:
            coefficient = int(m.group(1) or "1")
            operation = m.group(2)
            constant = int(m.group(3))
            total = int(m.group(4))

            if operation == "+":
                value = (total - constant) / coefficient
                return (
                    f"Let's solve it step by step.\n\n"
                    f"{coefficient}x + {constant} = {total}\n"
                    f"{coefficient}x = {total - constant}\n"
                    f"x = {value:g}"
                )

            if operation == "-":
                value = (total + constant) / coefficient
                return (
                    f"Let's solve it step by step.\n\n"
                    f"{coefficient}x - {constant} = {total}\n"
                    f"{coefficient}x = {total + constant}\n"
                    f"x = {value:g}"
                )

    return None


def reason_about_question(
    current_subject,
    message,
    grade=None,
    learner_name="Learner"
):
    detected_subject, topic = detect_subject_topic(message)

    if not detected_subject:
        return None

    answer = answer_question(
        detected_subject,
        topic,
        message,
        grade=grade
    )

    # The learner is asking about the current subject.
    if detected_subject == current_subject:
        if answer:
            return (
                f"📚 {learner_name}, this is a {detected_subject} question.\n\n"
                f"👨‍🏫 {answer}\n\n"
                f"If you'd like, I can give you an example or a practice question."
            )

        return None

    # The learner is asking about another subject.
    # NEVER block the learner. If we know the topic, teach it.
    if answer:
        return (
            f"📚 {learner_name}, this question is about "
            f"{detected_subject}, while your current subject is "
            f"{current_subject}.\n\n"
            f"👨‍🏫 That's okay — I can still help you with it.\n\n"
            f"{answer}\n\n"
            f"Would you like to continue with this {detected_subject} topic? "
            f"You can also keep your current subject as {current_subject}."
        )

    # Recognized topic but no prepared explanation:
    # guide the learner instead of refusing or inventing an answer.
    return (
        f"📚 {learner_name}, that looks like a "
        f"{detected_subject} question, while your current subject is "
        f"{current_subject}.\n\n"
        f"That's okay — you can ask me about {detected_subject}. "
        f"Please give me the exact question or tell me what part "
        f"of {topic} you want explained, and I'll work through it with you."
    )

