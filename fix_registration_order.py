import re

FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Find the app = Flask(...) line
app_def_match = re.search(r'app\s*=\s*Flask\s*\([^)]*\)', content)
if not app_def_match:
    print("❌ Could not find 'app = Flask(...)'")
    exit(1)

# Remove existing (late) registration
content = content.replace(
    "from student_learning import register_student_learning",
    "# (moved) from student_learning import register_student_learning"
)
content = content.replace(
    "register_student_learning(app)",
    "# (moved) register_student_learning(app)"
)

# Insert right after app = Flask(...)
insertion = (
    "\n# --- Student learning routes (moved here for correct registration order) ---\n"
    "from student_learning import register_student_learning\n"
    "register_student_learning(app)\n"
)
pos = app_def_match.end()
content = content[:pos] + insertion + content[pos:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ student_server.py fixed")
print("   • Removed late registration")
print("   • Inserted registration right after 'app = Flask(...)'")
print("\n📌 NEXT: Restart the server with:")
print("   python student_server.py\n")
