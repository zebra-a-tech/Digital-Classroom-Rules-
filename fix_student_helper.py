"""Add the missing student() helper function."""

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_student_helper.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if student() already exists
if "\ndef student(" in content or "\ndef student(" in content.replace("\n", "\n"):
    print("✅ student() function already exists")
else:
    print("❌ student() function is missing — adding it")

    # Find a good place to insert: right after the imports/DB setup
    import re
    # Look for the DB initialization or first route
    marker = "@app.route"
    pos = content.find(marker)

    if pos > 0:
        # Insert the helper function right before the first @app.route
        helper = '''
def student(sid):
    """Fetch a student record by ID."""
    import sqlite3
    conn = sqlite3.connect("digital_classroom.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return row


'''
        content = content[:pos] + helper + content[pos:]
        print("✅ Added student() helper function")
    else:
        print("❌ Could not find insertion point")
        exit(1)

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ student() HELPER FUNCTION ADDED")
print("="*70)
print("\n📌 RESTART THE SERVER:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")

# Quick verification
import subprocess
result = subprocess.run(
    ["python", "-c", "import student_server; print('OK')"],
    capture_output=True, text=True, timeout=5
)
if "OK" in result.stdout or result.returncode == 0:
    print("✅ student_server.py imports cleanly")
else:
    err = result.stderr.strip().split("\n")[-1] if result.stderr else "Unknown error"
    print(f"⚠️  Import check: {err}")
