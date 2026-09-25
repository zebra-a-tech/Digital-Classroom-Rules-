# Directly inspect and fix student_server.py

FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("\n" + "="*70)
print("📄 FIRST 20 LINES OF student_server.py")
print("="*70)
for i, line in enumerate(lines[:20], 1):
    print(f"{i:3d}: {line.rstrip()}")

print("\n" + "="*70)
print("🔍 FINDING 'register_parent_assist' REFERENCES")
print("="*70)
for i, line in enumerate(lines, 1):
    if "register_parent_assist" in line or "from parent_assist" in line:
        print(f"{i:3d}: {line.rstrip()}")

# ============================================================
# FIX: Delete ALL old parent_assist imports and calls,
#      then add them cleanly at the top
# ============================================================
print("\n" + "="*70)
print("🔧 FIXING IMPORTS")
print("="*70)

# Remove all lines containing register_parent_assist or the parent_assist import
new_lines = []
for line in lines:
    s = line.strip()
    if "from parent_assist import" in s:
        continue
    if "register_parent_assist(app)" in s and "# (moved)" not in s:
        continue
    new_lines.append(line)

lines = new_lines

# Find the position right after the LAST top-level import
last_import_idx = 0
for i, line in enumerate(lines[:50]):
    if line.strip().startswith(("import ", "from ")):
        last_import_idx = i

# Insert the import
lines.insert(last_import_idx + 1, "from parent_assist import register_parent_assist\n")
print(f"   ✅ Inserted import at line {last_import_idx + 2}")

# Find the app = Flask(...) line
app_def_idx = None
for i, line in enumerate(lines):
    if "app = " in line and "Flask(" in line:
        app_def_idx = i
        break

if app_def_idx is None:
    print("   ❌ Could not find 'app = Flask(...)'")
    exit(1)

print(f"   ✅ Found 'app = Flask(...)' at line {app_def_idx + 1}")

# Find the end of that statement (could span multiple lines)
insert_after = app_def_idx
while insert_after < len(lines) and lines[insert_after].strip() and not lines[insert_after].rstrip().endswith(")"):
    insert_after += 1

# Insert the registration call
lines.insert(insert_after + 1, "\nregister_parent_assist(app)\n")
print(f"   ✅ Inserted register call at line {insert_after + 2}")

# Write back
with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(lines)

# ============================================================
# VERIFY
# ============================================================
print("\n" + "="*70)
print("✅ FIXED — SHOWING RELEVANT LINES")
print("="*70)

with open(FILE, "r", encoding="utf-8") as f:
    new_lines = f.readlines()

for i, line in enumerate(new_lines[:25], 1):
    if "register_parent_assist" in line or "from parent_assist" in line or "app = " in line or "Flask(" in line:
        print(f"{i:3d}: {line.rstrip()}")
    else:
        print(f"{i:3d}: {line.rstrip()}")

# Also check if there are any remaining bad references
print("\n" + "="*70)
print("🔍 REMAINING REFERENCES:")
print("="*70)
for i, line in enumerate(new_lines, 1):
    if "register_parent_assist" in line:
        print(f"{i:3d}: {line.rstrip()}")

print("\n" + "="*70)
print("✅ NOW RESTART THE SERVER")
print("="*70)
print("\n   python student_server.py\n")
