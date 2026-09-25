import re

FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_import_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if import exists
has_import = "from parent_assist import register_parent_assist" in content
has_call = "register_parent_assist(app)" in content

print(f"   Has import: {has_import}")
print(f"   Has call:   {has_call}")

if has_import:
    print("✅ Import already present")
else:
    # Add the import after the last top-level import
    lines = content.split("\n")
    last_import = 0
    for i, line in enumerate(lines[:60]):
        if line.strip().startswith(("import ", "from ")) and "parent_assist" not in line:
            last_import = i

    lines.insert(last_import + 1, "from parent_assist import register_parent_assist")
    content = "\n".join(lines)
    print(f"   ✅ Added import after line {last_import + 1}")

# Make sure the call exists BEFORE app.run
if has_call:
    # Check if it's before app.run
    call_pos = content.find("register_parent_assist(app)")
    run_pos = content.find("app.run(")
    if run_pos > 0 and call_pos > run_pos:
        print("   ⚠️ Call is AFTER app.run — moving it")
        # Remove existing call
        content = content.replace("register_parent_assist(app)", "# (moved)", 1)
        # Insert before app.run
        content = content[:run_pos] + "register_parent_assist(app)\n" + content[run_pos:]
        print("   ✅ Moved call before app.run")
    else:
        print("   ✅ Call already in correct place")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open(FILE, "r", encoding="utf-8") as f:
    final = f.read()

print("\n🔍 VERIFICATION:")
print(f"   Import present: {'✅' if 'from parent_assist import register_parent_assist' in final else '❌'}")
print(f"   Call present:   {'✅' if 'register_parent_assist(app)' in final else '❌'}")

# Show the lines around the registration
lines = final.split("\n")
for i, line in enumerate(lines, 1):
    if "register_parent_assist" in line or "app = Flask" in line:
        print(f"   Line {i}: {line.strip()}")

print("\n✅ FIX COMPLETE")
print("\n📌 NOW RESTART:")
print("   python student_server.py")
