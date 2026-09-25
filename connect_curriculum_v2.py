import re

LEARNING_FILE = "student_learning.py"
BACKUP_FILE = "student_learning_backup_v2.py"

# Backup again (v2)
with open(LEARNING_FILE, "r", encoding="utf-8") as f:
    original = f.read()
with open(BACKUP_FILE, "w", encoding="utf-8") as f:
    f.write(original)
print(f"✅ Backup saved: {BACKUP_FILE}")

# Already patched?
if "_load_sqlite_curriculum" in original:
    print("✅ Already connected. Nothing to do.")
    exit(0)

# Find the END of the CURRICULUM = { ... } block by counting braces
lines = original.split("\n")
curriculum_start = None
for i, line in enumerate(lines):
    if re.match(r'^\s*CURRICULUM\s*=\s*\{', line):
        curriculum_start = i
        break

if curriculum_start is None:
    print("❌ Could not find CURRICULUM definition.")
    exit(1)

# Count braces from the CURRICULUM start line
brace_depth = 0
curriculum_end = None
for i in range(curriculum_start, len(lines)):
    brace_depth += lines[i].count("{")
    brace_depth -= lines[i].count("}")
    if brace_depth == 0 and i > curriculum_start:
        curriculum_end = i
        break

if curriculum_end is None:
    print("❌ Could not find end of CURRICULUM block.")
    exit(1)

print(f"   ✅ CURRICULUM block: lines {curriculum_start+1} to {curriculum_end+1}")

# Prepare loader text — will be inserted AFTER curriculum_end
loader = """

# ============================================================
# AUTO-LOAD CURRICULUM FROM SQLITE (added by connect_curriculum_v2.py)
# ============================================================
def _load_sqlite_curriculum():
    \"\"\"Load all lessons from the 'curriculum' SQLite table and merge into CURRICULUM.\"\"\"
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
"""

# Insert loader right after curriculum_end
new_lines = lines[:curriculum_end + 1] + [loader] + lines[curriculum_end + 1:]
patched = "\n".join(new_lines)

with open(LEARNING_FILE, "w", encoding="utf-8") as f:
    f.write(patched)

print("✅ Inserted loader AFTER the CURRICULUM block")
print("\n📌 NEXT: Restart server:")
print("   python student_server.py\n")
