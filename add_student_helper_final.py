"""Add student() helper + remove phone placeholder"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_helper_final.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# FIX 1: Check if student() exists
# ============================================================
if re.search(r'\ndef student\(sid\):', content):
    print("✅ student() function exists")
else:
    print("❌ student() is MISSING — adding it at the top")
    
    # Find the first @app.route
    first_route = content.find("@app.route")
    if first_route == -1:
        print("❌ No @app.route found")
        exit(1)
    
    helper = '''def student(sid):
    """Fetch a student record by ID."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return row


'''
    content = content[:first_route] + helper + content[first_route:]
    print("✅ Added student() before first route")

# ============================================================
# FIX 2: Remove phone placeholder
# ============================================================
auth_file = "auth.py"
try:
    with open(auth_file, "r", encoding="utf-8") as f:
        auth = f.read()
    
    with open("auth_before_phone_fix.py", "w", encoding="utf-8") as f:
        f.write(auth)
    
    if "placeholder='+263 71 234 5678'" in auth:
        auth = auth.replace(
            "placeholder='+263 71 234 5678'",
            ""
        )
        print("✅ Removed phone placeholder")
    else:
        print("✓ Phone placeholder already removed")
    
    with open(auth_file, "w", encoding="utf-8") as f:
        f.write(auth)
except FileNotFoundError:
    print("⚠️ auth.py not found")

# ============================================================
# FIX 3: Ensure Flask imports are complete
# ============================================================
top = content.split("def ")[0]
if "render_template_string" not in top:
    content = content.replace(
        "from flask import Flask, request, redirect, url_for",
        "from flask import Flask, request, redirect, url_for, render_template_string, session, jsonify",
        1
    )
    print("✅ Added missing Flask imports")

# ============================================================
# Write back
# ============================================================
with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

# Verify
print("\n🔍 VERIFICATION:")
with open(SERVER, "r", encoding="utf-8") as f:
    v = f.read()
print(f"   student() defined: {'✅' if 'def student(sid):' in v else '❌'}")
print(f"   render_template_string imported: {'✅' if 'render_template_string' in v.split('def ')[0] else '❌'}")

print("\n" + "="*70)
print("✅ FIXES APPLIED")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
