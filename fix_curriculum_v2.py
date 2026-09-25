import sqlite3

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("📚 DIGITAL CLASSROOM — CURRICULUM FIX V2")
print("="*70)

# ---------- 1. Create a proper shared CURRICULUM table ----------
print("\n1️⃣  Creating shared 'curriculum' table...")
c.execute("""
    CREATE TABLE IF NOT EXISTS curriculum (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        grade_form TEXT NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT NOT NULL,
        lesson_goal TEXT,
        content TEXT,
        tutor_intro TEXT,
        requires_parent_assist TEXT DEFAULT 'NO',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(grade_form, subject, topic)
    )
""")
print("   ✅ 'curriculum' table ready")

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

# ---------- 3. Insert lessons into curriculum ----------
print("\n2️⃣  Loading curriculum content...")

inserted = 0
skipped = 0

for grade, subjects in CURRICULUM.items():
    for subject in subjects:
        topics = STARTER_TOPICS.get(subject, ["Introduction"])
        for topic in topics:
            parent_assist = "YES" if needs_parent_assist(grade) else "NO"

            goal = (
                f"🎯 Today's Goal: By the end of this lesson, you will understand "
                f"{topic} in {subject} and be able to answer exam questions on it."
            )
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
            except sqlite3.IntegrityError:
                skipped += 1

print(f"   ✅ Inserted: {inserted} new lessons")
print(f"   ✓ Skipped (already existed): {skipped}")

conn.commit()

# ---------- 4. Verify ----------
print("\n3️⃣  CURRICULUM COVERAGE:")
print(f"\n   {'Grade':<10} | Lessons")
print("   " + "-" * 30)
for grade in CURRICULUM:
    c.execute("SELECT COUNT(*) FROM curriculum WHERE grade_form = ?", (grade,))
    count = c.fetchone()[0]
    print(f"   {grade:<10} | {count}")

print(f"\n   {'Subject':<20} | Lessons")
print("   " + "-" * 35)
for subj in STARTER_TOPICS:
    c.execute("SELECT COUNT(*) FROM curriculum WHERE subject = ?", (subj,))
    count = c.fetchone()[0]
    print(f"   {subj:<20} | {count}")

c.execute("SELECT COUNT(*) FROM curriculum WHERE requires_parent_assist = 'YES'")
pa = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM curriculum WHERE requires_parent_assist = 'NO'")
np = c.fetchone()[0]

print(f"\n   👨‍👩‍👧 Parent-assist lessons (Grade 1-4): {pa}")
print(f"   🧑 Self-study lessons (Grade 5+): {np}")

c.execute("SELECT COUNT(*) FROM curriculum")
total = c.fetchone()[0]
print(f"\n   📚 TOTAL curriculum lessons: {total}")

conn.close()

print("\n" + "="*70)
print("✅ CURRICULUM LOADED SUCCESSFULLY")
print("="*70)
print("\n📌 NEXT: Update your Flask routes to read from 'curriculum' table.")
print("📌 NEXT: Phase 2 — Fill in real lesson bodies per topic.\n")
