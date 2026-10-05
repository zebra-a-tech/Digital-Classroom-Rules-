"""Add the missing render_template_string import."""

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_render_import.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if render_template_string is imported
if "render_template_string" in content.split("def ")[0]:
    print("✅ render_template_string already imported at top")
else:
    print("❌ render_template_string is NOT imported — adding it")
    
    # Find the flask import line
    old_import = "from flask import Flask, request, redirect, url_for"
    
    if old_import in content:
        # Add render_template_string to the existing flask import
        new_import = "from flask import Flask, request, redirect, url_for, render_template_string, session"
        content = content.replace(old_import, new_import, 1)
        print("✅ Added render_template_string to flask import")
    else:
        # Fallback: add a new import line
        lines = content.split("\n")
        last_import = 0
        for i, line in enumerate(lines[:30]):
            if line.strip().startswith(("import ", "from ")):
                last_import = i
        lines.insert(last_import + 1, "from flask import render_template_string, session")
        content = "\n".join(lines)
        print("✅ Added new import line")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open(SERVER, "r", encoding="utf-8") as f:
    verify = f.read()

first_lines = verify.split("def ")[0]
checks = {
    "render_template_string": "render_template_string" in first_lines,
    "session": "session" in first_lines,
}

print("\n🔍 VERIFICATION (top of file):")
for k, v in checks.items():
    print(f"   {'✅' if v else '❌'} {k}")

# Show first 15 lines
print("\n📄 First 15 lines:")
for i, line in enumerate(verify.split("\n")[:15], 1):
    print(f"   {i}: {line}")

print("\n" + "="*70)
print("✅ RENDER_TEMPLATE_STRING IMPORT ADDED")
print("="*70)
print("\n📌 RESTART THE SERVER:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
