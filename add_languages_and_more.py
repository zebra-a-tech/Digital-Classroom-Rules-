import sqlite3

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("📚 ADDING SHONA, NDEBELE & MISSING SUBJECTS")
print("="*70 + "\n")

MISSING_SUBJECTS = {
    "Shona": ["Alphabet", "Greetings", "Numbers", "Family", "Nouns",
              "Verbs", "Sentences", "Reading", "Writing", "Culture"],
    "Ndebele": ["Alphabet", "Greetings", "Numbers", "Family", "Nouns",
                "Verbs", "Sentences", "Reading", "Writing", "Culture"],
    "Heritage Studies": ["Zimbabwe History", "Culture", "Citizenship",
                         "Environment", "National Symbols"],
    "Computer Studies": ["Basic Computer", "Typing", "Internet", "Software",
                         "Hardware", "Programming Basics"],
    "Agriculture": ["Crops", "Livestock", "Soil", "Farming Tools",
                    "Weather and Farming", "Farm Management"],
    "Commerce": ["Trade", "Business", "Money", "Banking", "Marketing"],
    "Religious Studies": ["World Religions", "African Traditional Religion",
                          "Christianity", "Islam", "Ethics"],
}

GRADE_SUBJECTS = {
    "Grade 1": ["Shona", "Ndebele"],
    "Grade 2": ["Shona", "Ndebele"],
    "Grade 3": ["Shona", "Ndebele", "Heritage Studies"],
    "Grade 4": ["Shona", "Ndebele", "Heritage Studies"],
    "Grade 5": ["Shona", "Ndebele", "Heritage Studies", "Computer Studies"],
    "Grade 6": ["Shona", "Ndebele", "Heritage Studies", "Computer Studies"],
    "Grade 7": ["Shona", "Ndebele", "Heritage Studies"],
    "Form 1": ["Shona", "Ndebele", "Heritage Studies", "Computer Studies",
               "Agriculture", "Commerce"],
    "Form 2": ["Shona", "Ndebele", "Heritage Studies", "Computer Studies",
               "Agriculture", "Commerce"],
    "Form 3": ["Shona", "Ndebele", "Computer Studies", "Agriculture",
               "Commerce", "Religious Studies"],
    "Form 4": ["Shona", "Ndebele", "Computer Studies", "Agriculture",
               "Commerce", "Religious Studies"],
    "Form 5": ["Shona", "Ndebele", "Computer Studies", "Agriculture"],
    "Form 6": ["Shona", "Ndebele", "Computer Studies", "Agriculture"],
}

def needs_parent_assist(grade):
    return grade in ["Grade 1", "Grade 2", "Grade 3", "Grade 4"]

inserted = 0
skipped = 0

for grade, subjects in GRADE_SUBJECTS.items():
    print(f"   {grade}:")
    for subject in subjects:
        topics = MISSING_SUBJECTS.get(subject, ["Introduction"])
        count = 0
        for topic in topics:
            c.execute("""
                SELECT COUNT(*) FROM curriculum
                WHERE grade_form = ? AND subject = ? AND topic = ?
            """, (grade, subject, topic))
            if c.fetchone()[0] > 0:
                skipped += 1
                continue

            parent_assist = "YES" if needs_parent_assist(grade) else "NO"
            goal = f"🎯 Today's Goal: By the end of this lesson, you will understand {topic} in {subject} and be able to answer exam questions on it."
            content = (
                f"📖 {subject} — {topic} ({grade})\n\n"
                f"Welcome! In this lesson, we cover the key ideas, vocabulary, and "
                f"exam skills for {topic}.\n\n"
                f"Your mission: write down 3 key points in your notebook, then send "
                f"a photo for marking.\n\n"
                f"📄 Real Exam Question: [See practice section]"
            )
            if parent_assist == "YES":
                tutor_intro = (
                    f"👋 Hey! I'm your tutor. Today we're diving into {topic} — "
                    f"one of the most important topics in {subject}. "
                    f"A parent or guardian should sit with you for this lesson."
                )
            else:
                tutor_intro = (
                    f"👋 Hey! I'm your tutor. Today we're diving into {topic} — "
                    f"one of the most important topics in {subject}. "
                    f"Let's master this together!"
                )
            try:
                c.execute("""
                    INSERT INTO curriculum
                    (grade_form, subject, topic, lesson_goal, content,
                     tutor_intro, requires_parent_assist)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (grade, subject, topic, goal, content, tutor_intro, parent_assist))
                inserted += 1
                count += 1
            except sqlite3.IntegrityError:
                skipped += 1
        print(f"      ✅ {subject}: {count} new lessons")

conn.commit()

c.execute("SELECT COUNT(*) FROM curriculum")
total = c.fetchone()[0]
print(f"\n📚 Total lessons: {total}")
print(f"🆕 Inserted: {inserted}")
print(f"✓ Skipped: {skipped}")

c.execute("SELECT COUNT(*) FROM curriculum WHERE requires_parent_assist = 'YES'")
print(f"👨‍👩‍👧 Parent-assist: {c.fetchone()[0]}")

conn.close()

print("\n" + "="*70)
print("✅ DONE")
print("="*70 + "\n")
