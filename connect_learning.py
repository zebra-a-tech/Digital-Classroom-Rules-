# This script modifies student_server.py to import and register student_learning
import re

FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Check if already connected
if "register_student_learning" in content:
    print("\n✅ student_learning is ALREADY registered in student_server.py")
    # Show where
    for i, line in enumerate(content.split("\n"), 1):
        if "register_student_learning" in line:
            print(f"   Line {i}: {line.strip()}")
else:
    print("\n🔧 Adding student_learning integration...")

    # 1. Add import after existing imports
    import_line = "from student_learning import register_student_learning\n"

    # Find a good insertion point (after the last import line at the top)
    lines = content.split("\n")
    last_import_idx = 0
    for i, line in enumerate(lines[:50]):
        s = line.strip()
        if s.startswith("import ") or s.startswith("from "):
            last_import_idx = i

    # Insert the import
    lines.insert(last_import_idx + 1, import_line)
    content = "\n".join(lines)

    # 2. Register the blueprint after `app = Flask(...)`
    # Find `app = Flask(__name__)`
    app_def = re.search(r'(app\s*=\s*Flask\s*\([^)]*\))', content)
    if app_def:
        insert_pos = app_def.end()
        registration = "\nregister_student_learning(app)\n"
        content = content[:insert_pos] + registration + content[insert_pos:]
        print("   ✅ Added import: from student_learning import register_student_learning")
        print("   ✅ Registered: register_student_learning(app)")
    else:
        print("   ❌ Could not find 'app = Flask(...)' in student_server.py")

    # Write back
    with open(FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("\n✅ student_server.py patched")

print("\n" + "="*70)
print("📌 NEXT: Restart student_server.py to see the new routes:")
print("   python student_server.py")
print("="*70 + "\n")
