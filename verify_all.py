import sqlite3, datetime, os, sys

DB = "digital_classroom.db"

print("\n" + "="*70)
print("🔍 DIGITAL CLASSROOM — FULL SYSTEM VERIFICATION")
print("="*70)

# ---------- CHECK DB EXISTS ----------
if not os.path.exists(DB):
    print(f"❌ DATABASE NOT FOUND at {DB}")
    sys.exit(1)
print(f"✅ Database found: {DB}")

conn = sqlite3.connect(DB)
c = conn.cursor()

# ---------- LIST ALL TABLES ----------
print("\n📋 TABLES IN DATABASE:")
c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in c.fetchall()]
for t in tables:
    print(f"   • {t}")

# ---------- TEST 1: STUDENT EXISTS ----------
print("\n" + "-"*70)
print("TEST 1: Student Record")
try:
    c.execute("SELECT student_id, name, grade_form, subject FROM students LIMIT 3")
    rows = c.fetchall()
    if rows:
        for r in rows:
            print(f"   ✅ Student {r[0]}: {r[1]} | Grade: {r[2]} | Subject: {r[3]}")
    else:
        print("   ⚠️ No students found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 2: PAYMENT REQUESTS ----------
print("\n" + "-"*70)
print("TEST 2: Payment Requests")
try:
    c.execute("SELECT id, student_id, amount, status FROM payment_requests ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    if rows:
        for r in rows:
            print(f"   • Request #{r[0]} | Student {r[1]} | ${r[2]} | Status: {r[3]}")
    else:
        print("   ⚠️ No payment requests found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 3: PAID SESSIONS ----------
print("\n" + "-"*70)
print("TEST 3: Paid Sessions")
try:
    c.execute("SELECT id, student_id, subject, started_at, expires_at, active FROM paid_sessions ORDER BY id DESC LIMIT 5")
    rows = c.fetchall()
    if rows:
        for r in rows:
            status = "🟢 ACTIVE" if r[5] == 1 else "🔴 EXPIRED"
            print(f"   • Session #{r[0]} | Student {r[1]} | {r[2]} | {status}")
            print(f"     Start: {r[3]} | Expire: {r[4]}")
    else:
        print("   ⚠️ No paid sessions found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 4: LESSONS COVERAGE ----------
print("\n" + "-"*70)
print("TEST 4: Lesson Coverage (by Grade & Subject)")
try:
    c.execute("SELECT grade_form, subject, COUNT(*) FROM lessons GROUP BY grade_form, subject ORDER BY grade_form, subject")
    rows = c.fetchall()
    if rows:
        for r in rows:
            print(f"   ✅ {r[0]:<12} | {r[1]:<15} | {r[2]} lessons")
    else:
        print("   ⚠️ No lessons found — check if the lessons table is populated")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 5: HOMEWORK & ASSIGNMENTS ----------
print("\n" + "-"*70)
print("TEST 5: Homework & Assignments")
try:
    c.execute("SELECT COUNT(*) FROM assignments")
    a_count = c.fetchone()[0]
    print(f"   • Assignments: {a_count}")
    c.execute("SELECT COUNT(*) FROM assignment_questions")
    q_count = c.fetchone()[0]
    print(f"   • Questions: {q_count}")
    if a_count == 0:
        print("   ⚠️ No homework assignments found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 6: TESTS & EXAMS ----------
print("\n" + "-"*70)
print("TEST 6: Tests & Exams")
for tbl in ["academic_tests", "academic_exams"]:
    try:
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"   • {tbl}: {c.fetchone()[0]} records")
    except Exception as e:
        print(f"   ❌ {tbl}: {e}")

# ---------- TEST 7: PROGRESS TRACKING ----------
print("\n" + "-"*70)
print("TEST 7: Progress Tracking")
for tbl in ["learning_progress", "playbook_progress"]:
    try:
        c.execute(f"SELECT COUNT(*) FROM {tbl}")
        print(f"   • {tbl}: {c.fetchone()[0]} records")
    except Exception as e:
        print(f"   ❌ {tbl}: {e}")

# ---------- TEST 8: STREAK & COUNTDOWN ----------
print("\n" + "-"*70)
print("TEST 8: Streak & Exam Countdown Columns")
c.execute("PRAGMA table_info(students)")
cols = [r[1] for r in c.fetchall()]
print(f"   Student columns: {', '.join(cols)}")
for col in ["streak", "last_study_date", "exam_date"]:
    if col in cols:
        print(f"   ✅ Column '{col}' exists")
    else:
        print(f"   ❌ Column '{col}' MISSING — needs to be added")

# ---------- TEST 9: REFERRAL SYSTEM ----------
print("\n" + "-"*70)
print("TEST 9: Referral System")
if "referrals" in tables:
    print("   ✅ 'referrals' table exists")
    c.execute("SELECT COUNT(*) FROM referrals")
    print(f"   • Records: {c.fetchone()[0]}")
else:
    print("   ❌ 'referrals' table MISSING")

if "referral_code" in cols:
    print("   ✅ 'referral_code' column exists in students")
else:
    print("   ❌ 'referral_code' column MISSING in students")

# ---------- TEST 10: MISSING LESSONS SCAN ----------
print("\n" + "-"*70)
print("TEST 10: Missing Lessons Scan")
grades = ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7",
          "Form 1","Form 2","Form 3","Form 4","Form 5","Form 6"]
core_subjects = ["Maths","English","Science","Social Studies"]
missing = []
try:
    for g in grades:
        for s in core_subjects:
            c.execute("SELECT COUNT(*) FROM lessons WHERE grade_form=? AND subject=?", (g, s))
            if c.fetchone()[0] == 0:
                missing.append(f"{g} — {s}")
    if missing:
        print("   ⚠️ MISSING LESSONS:")
        for m in missing:
            print(f"      ❌ {m}")
    else:
        print("   ✅ All core grade/subject combinations have lessons")
except Exception as e:
    print(f"   ❌ Error: {e}")

# ---------- TEST 11: PAID ROUTE BYPASS ----------
print("\n" + "-"*70)
print("TEST 11: Paid Routes Registered")
try:
    with open("app_student.py", "r") as f:
        content = f.read()
    checks = {
        "register_paid_access(app)": "register_paid_access(app)" in content,
        "Payment gate BEFORE app.run": content.find("register_paid_access(app)") < content.find("app.run("),
        "Paid session check route": "paid_session" in content or "paid_sessions" in content,
        "/student/ route present": "/student/" in content,
        "/playbook route present": "playbook" in content,
    }
    for k, v in checks.items():
        print(f"   {'✅' if v else '❌'} {k}")
except FileNotFoundError:
    print("   ⚠️ app_student.py not found in this folder")

# ---------- TEST 12: TIME ZONE ----------
print("\n" + "-"*70)
print("TEST 12: System Time (Africa/Harare)")
print(f"   • Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   • UTC time:     {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------- SUMMARY ----------
print("\n" + "="*70)
print("✅ VERIFICATION COMPLETE")
print("="*70)
print("\n📌 NEXT STEPS:")
print("   1. Fix every ❌ you see above.")
print("   2. Populate any missing lessons.")
print("   3. Test paid flow end-to-end: PENDING → VERIFIED → START → EXPIRE.")
print("   4. Re-run: python verify_all.py")
print()

conn.close()
