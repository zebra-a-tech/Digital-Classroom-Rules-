import sqlite3, os, datetime

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("🔧 DIGITAL CLASSROOM — SYSTEM FIX")
print("="*70)

# ---------- STEP 1: Inspect actual schema ----------
def columns_of(table):
    c.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in c.fetchall()]

print("\n📋 ACTUAL SCHEMA OF KEY TABLES:")
for tbl in ["students", "lessons", "paid_sessions", "payment_requests",
            "assignments", "assignment_questions", "student_subjects"]:
    try:
        print(f"   • {tbl}: {columns_of(tbl)}")
    except Exception as e:
        print(f"   • {tbl}: ❌ {e}")

# ---------- STEP 2: Add missing columns to students ----------
print("\n🔧 Adding missing columns to 'students'...")
stu_cols = columns_of("students")
additions = {
    "last_study_date": "TEXT",
    "exam_date": "TEXT",
    "referral_code": "TEXT",
}
for col, typ in additions.items():
    if col not in stu_cols:
        try:
            c.execute(f"ALTER TABLE students ADD COLUMN {col} {typ}")
            print(f"   ✅ Added '{col}' to students")
        except Exception as e:
            print(f"   ❌ Could not add '{col}': {e}")
    else:
        print(f"   ✓ '{col}' already exists")

# ---------- STEP 3: Create referrals table ----------
print("\n🔧 Creating 'referrals' table...")
try:
    c.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER,
            referral_code TEXT,
            status TEXT DEFAULT 'pending',
            bonus_amount REAL DEFAULT 0,
            paid_on TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("   ✅ 'referrals' table ready")
except Exception as e:
    print(f"   ❌ {e}")

# ---------- STEP 4: Add missing columns to paid_sessions ----------
print("\n🔧 Checking 'paid_sessions'...")
ps_cols = columns_of("paid_sessions")
ps_add = {
    "subject": "TEXT",
    "student_ref": "INTEGER",
}
for col, typ in ps_add.items():
    if col not in ps_cols:
        try:
            c.execute(f"ALTER TABLE paid_sessions ADD COLUMN {col} {typ}")
            print(f"   ✅ Added '{col}' to paid_sessions")
        except Exception as e:
            print(f"   ❌ {e}")
    else:
        print(f"   ✓ '{col}' exists")

# ---------- STEP 5: Add missing columns to lessons ----------
print("\n🔧 Checking 'lessons'...")
ls_cols = columns_of("lessons")
ls_add = {
    "grade_form": "TEXT",
    "subject": "TEXT",
    "topic": "TEXT",
    "content": "TEXT",
}
for col, typ in ls_add.items():
    if col not in ls_cols:
        try:
            c.execute(f"ALTER TABLE lessons ADD COLUMN {col} {typ}")
            print(f"   ✅ Added '{col}' to lessons")
        except Exception as e:
            print(f"   ❌ {e}")
    else:
        print(f"   ✓ '{col}' exists")

# ---------- STEP 6: Detect actual server file ----------
print("\n📂 SCANNING FOR SERVER FILES:")
files = [f for f in os.listdir(".") if f.endswith(".py")]
for f in files:
    print(f"   • {f}")

server_candidates = [f for f in files if "student" in f.lower() or "app" in f.lower()]
if server_candidates:
    print(f"\n   ✅ Likely server file(s): {server_candidates}")
else:
    print("\n   ⚠️ No obvious server file found (app_student.py missing?)")

# ---------- STEP 7: Sample data for testing ----------
print("\n🔧 Preparing sample test data...")

# Ensure Student 1 exists with all columns filled
c.execute("SELECT id FROM students WHERE id = 1")
if not c.fetchone():
    c.execute("""INSERT INTO students 
        (id, name, age, school, location, grade_form, subject, exam_board, tutor,
         registered_at, free_trial_used, paid_lessons, streak, last_activity_date,
         current_subject, last_study_date, exam_date, referral_code)
        VALUES (1, 'Tinashe', 15, 'Test High School', 'Harare', 'Form 3', 'Maths',
                'ZIMSEC', 'Tariro', ?, 0, 0, 0, ?, 'Maths', ?, '2026-10-30', 'TINASHE01')
    """, (datetime.date.today().isoformat(), datetime.date.today().isoformat(),
          datetime.date.today().isoformat()))
    print("   ✅ Created sample student: Tinashe (ID 1)")
else:
    print("   ✓ Student 1 already exists")

# Ensure a test lesson exists
c.execute("SELECT COUNT(*) FROM lessons")
if c.fetchone()[0] == 0:
    c.execute("""INSERT INTO lessons (grade_form, subject, topic, content)
                 VALUES ('Form 3', 'Maths', 'Decimals',
                 'A decimal is a number with a point. Example: 3.5')""")
    print("   ✅ Added sample lesson (Form 3 Maths — Decimals)")
else:
    print("   ✓ Lessons table already has data")

conn.commit()
conn.close()

print("\n" + "="*70)
print("✅ SYSTEM FIX COMPLETE")
print("="*70)
print("\n📌 NEXT STEP: Run the verification again:")
print("   python verify_all.py")
print()
