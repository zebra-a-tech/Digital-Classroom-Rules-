"""Connect auth.py to student_server.py — small focused script."""

import re
import os

# ============================================================
# STEP 1: Verify auth.py exists
# ============================================================
if not os.path.exists("auth.py"):
    print("❌ auth.py not found. Please run the previous script first.")
    exit(1)

print("✅ auth.py found")

# ============================================================
# STEP 2: Load student_server.py
# ============================================================
SERVER = "student_server.py"

if not os.path.exists(SERVER):
    print(f"❌ {SERVER} not found.")
    exit(1)

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

print(f"✅ {SERVER} loaded ({len(content)} bytes)")

# ============================================================
# STEP 3: Backup
# ============================================================
with open("student_server_before_auth.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved: student_server_before_auth.py")

# ============================================================
# STEP 4: Check if already connected
# ============================================================
if "register_auth_routes" in content:
    print("✅ Auth is already connected")
    print("   Restart the server to test:")
    print("   python student_server.py")
    exit(0)

# ============================================================
# STEP 5: Add import line
# ============================================================
if "from auth import" not in content:
    lines = content.split("\n")
    last_import = 0
    for i, line in enumerate(lines[:80]):
        if line.strip().startswith(("import ", "from ")):
            last_import = i
    
    lines.insert(last_import + 1, "from auth import register_auth_routes, login_required, current_user")
    content = "\n".join(lines)
    print(f"✅ Added import at line {last_import + 2}")

# ============================================================
# STEP 6: Add secret key
# ============================================================
if "app.secret_key" not in content:
    app_match = re.search(r"app\s*=\s*Flask\s*\([^)]*\)", content)
    if app_match:
        insert_pos = app_match.end()
        secret_setup = (
            "\n\n# Session secret for login system\n"
            "app.secret_key = 'dcr-secret-key-2026-change-later'\n"
            "import datetime as _dt\n"
            "app.permanent_session_lifetime = _dt.timedelta(days=7)\n"
        )
        content = content[:insert_pos] + secret_setup + content[insert_pos:]
        print("✅ Added app.secret_key")

# ============================================================
# STEP 7: Register auth routes before app.run()
# ============================================================
if "register_auth_routes(app)" not in content:
    run_pos = content.rfind("app.run(")
    if run_pos > 0:
        content = content[:run_pos] + "register_auth_routes(app)\n\n" + content[run_pos:]
        print("✅ Registered auth routes before app.run()")
    else:
        print("❌ Could not find app.run() in student_server.py")
        exit(1)

# ============================================================
# STEP 8: Write back
# ============================================================
with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ student_server.py updated")

# ============================================================
# STEP 9: Verify
# ============================================================
print("\n" + "="*60)
print("🔍 VERIFICATION")
print("="*60)

with open(SERVER, "r", encoding="utf-8") as f:
    verify = f.read()

checks = {
    "Import added": "from auth import" in verify,
    "Secret key added": "app.secret_key" in verify,
    "Auth routes registered": "register_auth_routes(app)" in verify,
    "Register route": "register_auth_routes" in verify,
}

for k, v in checks.items():
    print(f"   {'✅' if v else '❌'} {k}")

print("\n" + "="*60)
print("✅ DONE — Now restart the server")
print("="*60)
print("\nRun this command:")
print("   python student_server.py")
print("\nThen open in browser:")
print("   http://127.0.0.1:5001/")
print()
