FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("\n" + "="*70)
print("🔧 REORDERING IMPORTS & REGISTRATION CALLS")
print("="*70 + "\n")

# ============================================================
# STEP 1: Remove ALL current parent_assist/marking/whatsapp lines
# ============================================================
CLEAN_LINES = []
for line in lines:
    s = line.strip()
    # Skip old imports and calls (we'll re-add them in the right place)
    if s.startswith("from parent_assist import"):
        continue
    if s.startswith("from marking_flow import"):
        continue
    if s.startswith("from whatsapp_webhook import"):
        continue
    if s.startswith("from student_learning import"):
        continue
    if s == "register_parent_assist(app)":
        continue
    if s == "register_marking_flow(app)":
        continue
    if s == "register_whatsapp_webhook(app)":
        continue
    if s == "register_student_learning(app)":
        continue
    if s == "# --- Student learning routes (moved here for correct registration order) ---":
        continue
    CLEAN_LINES.append(line)

print(f"   ✅ Removed old imports and calls")

# ============================================================
# STEP 2: Find where `app = Flask(...)` ends
# ============================================================
app_def_idx = None
for i, line in enumerate(CLEAN_LINES):
    if "app = " in line and "Flask(" in line:
        app_def_idx = i
        break

if app_def_idx is None:
    print("   ❌ Could not find 'app = Flask(...)'")
    exit(1)

# Find the end of that statement (multi-line safe)
insert_after = app_def_idx
while insert_after < len(CLEAN_LINES) and CLEAN_LINES[insert_after].strip() and not CLEAN_LINES[insert_after].rstrip().endswith(")"):
    insert_after += 1

print(f"   ✅ 'app = Flask(...)' ends at line {insert_after + 1}")

# ============================================================
# STEP 3: Build the block to insert right after app = Flask()
# ============================================================
# IMPORTS first, then CALLS

import_block = [
    "\n",
    "# === Digital Classroom module imports ===\n",
    "from parent_assist import register_parent_assist\n",
    "from marking_flow import register_marking_flow\n",
    "from whatsapp_webhook import register_whatsapp_webhook\n",
    "from student_learning import register_student_learning\n",
    "\n",
    "# === Register all routes ===\n",
    "register_parent_assist(app)\n",
    "register_marking_flow(app)\n",
    "register_whatsapp_webhook(app)\n",
    "register_student_learning(app)\n",
    "\n",
]

# Insert AFTER the app = Flask() line
NEW_LINES = CLEAN_LINES[:insert_after + 1] + import_block + CLEAN_LINES[insert_after + 1:]

# ============================================================
# STEP 4: Write back
# ============================================================
with open(FILE, "w", encoding="utf-8") as f:
    f.writelines(NEW_LINES)

print("\n" + "="*70)
print("✅ REORDERING COMPLETE")
print("="*70)

# Show first 30 lines
print("\n📄 FIRST 30 LINES:")
with open(FILE, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, 1):
        if i > 30:
            break
        print(f"{i:3d}: {line.rstrip()}")

print("\n📌 NEXT: Restart the server:")
print("   python student_server.py\n")
