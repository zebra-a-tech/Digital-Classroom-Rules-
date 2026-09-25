import sqlite3

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("📚 LOADING CORE CURRICULUM — PHASE 1")
print("="*70)

# ---------- 1. Ensure lessons table has required columns ----------
print("\n1️⃣  Checking lessons table schema...")
cols = [r[1] for r in c.execute("PRAGMA table_info(lessons)").fetchall()]
print(f"   Current columns: {cols}")

for col in ["requires_parent_assist", "grade_form", "subject", "lesson_topic",
            "lesson_goal", "content", "tutor_intro"]:
    if col not in cols:
        c.execute(f"ALTER TABLE lessons ADD COLUMN {col} TEXT")
        print(f"   ✅ Added column: {col}")

# ---------- 2. Curriculum structure ----------
CURRICULUM = {
    "Grade 1": ["Maths", "English", "Science", "Social Studies"],
    "Grade 2": ["Maths", "English", "Science", "Social Studies"],
    "Grade 3": ["Maths", "English", "Science", "Social Studies"],
    "Grade 4": ["Maths", "English", "Science", "Social Studies"],
    "Grade 5": ["Maths", "English", "Science", "Social Studies"],
    "Grade 6": ["Maths", "English", "Science", "Social Studies"],
    "Grade 7": ["Maths", "English", "Science"],
    "Form 1": ["Maths", "English", "Science", "Geography", "History"],
    "Form 2": ["Maths", "English", "Science", "Geography", "History"],
    "Form 3": ["Maths", "English", "Science", "Geography", "History",
               "Biology", "Chemistry", "Physics", "Economics"],
    "Form 4": ["Maths", "English", "Science", "Geography", "History",
               "Biology", "Chemistry", "Physics", "Economics", "Accounting"],
    "Form 5": ["Maths", "Biology", "Chemistry", "Physics", "Economics"],
    "Form 6": ["Maths", "Biology", "Chemistry", "Physics", "Economics"],
}

# ---------- 3. Starter topics ----------
STARTER_TOPICS = {
    "Maths": ["Numbers", "Operations", "Fractions", "Decimals", "Algebra",
              "Geometry", "Measurement", "Statistics"],
    "English": ["Grammar", "Comprehension", "Composition", "Vocabulary",
                "Punctuation", "Literature"],
    "Science": ["Living Things", "Matter", "Energy", "Forces",
                "The Human Body", "The Environment"],
    "Social Studies": ["My Family", "My Community", "Zimbabwe", "The World",
                       "Citizenship", "Maps and Globes"],
    "Geography": ["Maps and Mapwork", "Weather and Climate", "Landforms",
                  "Rivers", "Population", "Resources"],
    "History": ["Early Zimbabwe", "Great Zimbabwe", "Colonial Rule",
                "Liberation Struggle", "Independence"],
    "Biology": ["Cells", "Nutrition", "Respiration", "Reproduction",
                "Genetics", "Ecology"],
    "Chemistry": ["Atoms", "Bonding", "Acids and Bases", "Reactions",
                  "Organic Chemistry", "Electrolysis"],
    "Physics": ["Motion", "Forces", "Energy", "Waves", "Electricity",
                "Magnetism"],
    "Economics": ["Scarcity", "Demand and Supply", "Markets",
                  "National Income", "Trade", "Development"],
    "Accounting": ["Accounting Equation", "Double Entry", "Ledgers",
                   "Trial Balance", "Trading Account", "Balance Sheet"],
}

def needs_parent_assist(grade):
    return grade in ["Grade 1", "Grade 2", "Grade 3", "Grade 4"]

# ---------- 4. Insert lessons ----------
print("\n2️⃣  Inserting lessons for every grade and subject...")

inserted = 0
existing = 0

for grade, subjects in CURRICULUM.items():
    for subject in subjects:
        topics = STARTER_TOPICS.get(subject, ["Introduction"])
        for topic in topics:
            c.execute("""
                SELECT COUNT(*) FROM lessons
                WHERE grade_form = ? AND subject = ? AND lesson_topic = ?
            """, (grade, subject, topic))

            if c.fetchone()[0] > 0:
                existing += 1
                continue

            parent_assist = "YES" if needs_parent_assist(grade) else "NO"

            goal = f"🎯 Today's Goal: By the end of this lesson, you will understand {topic} in {subject} and be able to answer exam questions on it."

            content = (
                f"📖 {subject} — {topic} ({grade})\n\n"
                f"Welcome! In this lesson, we cover the key ideas, vocabulary, and exam skills for {topic}.\n\n"
                f"Your mission: write down 3 key points in your notebook, then send a photo for marking.\n\n"
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

            c.execute("""
                INSERT INTO lessons
                (grade_form, subject, lesson_topic, lesson_goal, content,
                 tutor_intro, requires_parent_assist)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (grade, subject, topic, goal, content, tutor_intro, parent_assist))

            inserted += 1

print(f"   ✅ Inserted: {inserted} new lessons")
print(f"   ✓ Skipped (already existed): {existing}")

# ---------- 5. Verify ----------
conn.commit()

print("\n3️⃣  Verifying curriculum coverage...")
print(f"\n   {'Grade':<10} | Lessons")
print("   " + "-" * 30)
for grade in CURRICULUM:
    c.execute("SELECT COUNT(*) FROM lessons WHERE grade_form = ?", (grade,))
    count = c.fetchone()[0]
    print(f"   {grade:<10} | {count}")

print(f"\n   {'Subject':<20} | Lessons")
print("   " + "-" * 35)
for subj in STARTER_TOPICS:
    c.execute("SELECT COUNT(*) FROM lessons WHERE subject = ?", (subj,))
    count = c.fetchone()[0]
    print(f"   {subj:<20} | {count}")

c.execute("SELECT COUNT(*) FROM lessons WHERE requires_parent_assist = 'YES'")
pa = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM lessons WHERE requires_parent_assist = 'NO'")
np = c.fetchone()[0]
print(f"\n   👨‍👩‍👧 Parent-assist lessons (Grade 1-4): {pa}")
print(f"   🧑 Self-study lessons (Grade 5+): {np}")

conn.close()

print("\n" + "="*70)
print("✅ PHASE 1 COMPLETE — CURRICULUM SKELETON LOADED")
print("="*70)
print("\n📌 NEXT: Run 'python check_curriculum.py' to confirm.")
print("📌 NEXT: We then fill lesson BODIES for each topic.\n")
