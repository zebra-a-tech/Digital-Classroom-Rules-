"""Move student() to the top of student_server.py"""

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_student_top.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if student() is defined
if "\ndef student(sid):" not in content:
    print("❌ student() not found — nothing to move")
    exit(1)

# Extract the student() function definition
import re

# Match: def student(sid): ... up to the next "def " or "@app.route"
match = re.search(r'\ndef student\(sid\):\n(.*?)(?=\n\ndef |\n\n@app\.route|\n\nDB =|\Z)', content, re.DOTALL)

if not match:
    print("❌ Could not extract student() function")
    exit(1)

student_func = "def student(sid):\n" + match.group(1)

# Remove it from its current position
content = content.replace("\n" + student_func, "\n")

# Now insert it right after the imports (before the first @app.route)
first_route = content.find("@app.route")
if first_route > 0:
    content = content[:first_route] + student_func + "\n\n" + content[first_route:]
    print("✅ Moved student() to the top")
else:
    print("❌ Could not find insertion point")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ DONE — restart the server:")
print("   python student_server.py")
