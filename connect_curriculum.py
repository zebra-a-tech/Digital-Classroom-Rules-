# Connect the SQLite curriculum table to student_learning.py's CURRICULUM dict
import sqlite3
import re

LEARNING_FILE = "student_learning.py"
BACKUP_FILE = "student_learning_before_curriculum_merge.py"

# ---------- 1. Backup ----------
with open(LEARNING_FILE, "r", encoding="utf-8") as f:
    original = f.read()

with open(BACKUP_FILE, "w", encoding="utf-8") as f:
    f.write(original)

print(f"✅ Backup saved: {BACKUP_FILE}")

# ---------- 2. Check if already connected ----------
if "_load_sqlite_curriculum" in original:
    print("\n✅ SQLite curriculum is ALREADY connected")
    print("   (nothing to do)")
    exit(0)

# ---------- 3. Find where CURRICULUM is defined ----------
print("\n🔍 Looking for CURRICULUM definition...")

# Find the CURRICULUM = { ... } block
# We need to locate the line where CURRICULUM is first defined
match = re.search(r'^CURRICULUM\s*=\s*\{', original, re.MULTILINE)
if not match:
    print("   ❌ Could not find 'CURRICULUM = {' in student_learning.py")
    print("   Attempting alternate pattern...")
    # Try looking for it inside a function
    match = re.search(r'CURRICULUM\s*=\s*\{', original)
    if not match:
        print("   ❌ Still not found. Please send the top 100 lines of student_learning.py")
        exit(1)

insert_pos = match.end()

# ---------- 4. Prepare the SQLite loader ----------
loader = '''

# ============================================================
# AUTO-LOAD CURRICULUM FROM SQLITE (added by connect_curriculum.py)
# ============================================================
def _load_sqlite_curriculum():
    """Load all lessons from the 'curriculum' SQLite table
    and inject them into the module-level CURRICULUM dict."""
    import sqlite3
    try:
        conn = sqlite3.connect("digital_classroom.db")
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT grade_form, subject, topic, lesson_goal, content,
                   tutor_intro, requires_parent_assist
            FROM curriculum
        """).fetchall()
        conn.close()

        loaded = 0
        for r in rows:
            subj = (r["subject"] or "").strip()
            topic = (r["topic"] or "").strip()
            if not subj or not topic:
                continue
            key = (subj, topic)
            # Don't overwrite existing rich topics
            if key not in CURRICULUM:
                CURRICULUM[key] = {
                    "goal":       r["lesson_goal"],
                    "content":    r["content"],
                    "tutor":      r["tutor_intro"],
                    "parent":     r["requires_parent_assist"] == "YES",
                    "grade":      r["grade_form"],
                    "_from_sql":  True,
                }
            loaded += 1
        return loaded
    except Exception as e:
        print(f"⚠️ Curriculum loader error: {e}")
        return 0

_SQLITE_LESSONS_LOADED = _load_sqlite_curriculum()

'''
# The loader references CURRICULUM which is defined right above the insertion point
# So this works: CURRICULUM = { ...existing... }  <-- INSERT HERE

# ---------- 5. Insert the loader ----------
patched = original[:insert_pos] + loader + original[insert_pos:]

# ---------- 6. Write the patched file ----------
with open(LEARNING_FILE, "w", encoding="utf-8") as f:
    f.write(patched)

print("   ✅ Inserted SQLite loader into student_learning.py")

# ---------- 7. Verify the patch ----------
print("\n🔎 Verifying the patch...")

conn = sqlite3.connect("digital_classroom.db")
count = conn.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
conn.close()

print(f"   📚 Lessons in SQLite 'curriculum' table: {count}")

# Check if loader is present
with open(LEARNING_FILE, "r", encoding="utf-8") as f:
    final = f.read()
    if "_load_sqlite_curriculum" in final:
        print("   ✅ Loader function present in file")
    else:
        print("   ❌ Loader missing — something went wrong")

print("\n" + "="*70)
print("✅ CURRICULUM CONNECTION COMPLETE")
print("="*70)
print("\n📌 NEXT: Restart the student server:")
print("   python student_server.py")
print("\n📌 Then open the student portal and check /learn")
print("="*70 + "\n")
