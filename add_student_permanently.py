"""Add student() function to the top of student_server.py"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_student_perm.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# Check if student() exists
# ============================================================
if re.search(r'^def student\(sid\):', content, re.MULTILINE):
    print("✅ student() exists already")
    # Find its position
    for i, line in enumerate(content.split("\n"), 1):
        if line.startswith("def student(sid):"):
            print(f"   At line {i}")
            break
else:
    print("❌ student() missing — adding it at the top")

    # Find the position after the DB setup / imports
    # Look for "DB = " line
    db_line = content.find("DB = ")
    if db_line > 0:
        # Find end of that line
        line_end = content.find("\n", db_line)
        insert_pos = line_end + 1

        student_func = '''

def student(sid):
    """Fetch a student record by ID."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return row

'''
        content = content[:insert_pos] + student_func + content[insert_pos:]
        print("✅ Added student() after DB definition")

# ============================================================
# Remove old root route
# ============================================================
old_root = re.compile(
    r'@app\.route\("/"\)\s*\n\s*def root\(\):.*?(?=\n@app\.route|\n\ndef |\Z)',
    re.DOTALL
)
if old_root.search(content):
    content = old_root.sub("# Old root route disabled\n", content, count=1)
    print("✅ Removed old / route")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ STUDENT HELPER ADDED")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
