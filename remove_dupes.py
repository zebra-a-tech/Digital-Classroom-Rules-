"""Remove duplicate routes and register_auth_routes calls"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_dupe_removal.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# FIX 1: Remove ALL @app.route("/") definitions
# ============================================================
content = re.sub(
    r'@app\.route\("/"\)\s*\n\s*def root\(\):.*?(?=\n@app\.route|\n\ndef |\Z)',
    '# Old root route removed\n',
    content,
    flags=re.DOTALL
)
print("✅ Removed old root() route(s)")

# ============================================================
# FIX 2: Ensure register_auth_routes is called only ONCE
# ============================================================
# Remove ALL existing calls
content = re.sub(
    r'^register_auth_routes\(app\)\s*$',
    '',
    content,
    flags=re.MULTILINE
)

# Add exactly ONE call before app.run
run_pos = content.rfind("app.run(")
if run_pos > 0:
    content = content[:run_pos] + "register_auth_routes(app)\n\n" + content[run_pos:]
    print("✅ Added exactly ONE register_auth_routes call before app.run")

# ============================================================
# Write back
# ============================================================
with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

# ============================================================
# Verify
# ============================================================
with open(SERVER, "r", encoding="utf-8") as f:
    verify = f.read()

print("\n🔍 VERIFICATION:")
print(f"   register_auth_routes calls: {verify.count('register_auth_routes(app)')}")
print(f"   @app.route('/') routes: {verify.count('@app.route(\"/\")')}")

# Test import
import subprocess
result = subprocess.run(
    ["python", "-c", "import student_server; print('OK')"],
    capture_output=True, text=True, timeout=8
)
if "OK" in result.stdout or result.returncode == 0:
    print("\n✅ student_server.py imports cleanly")
else:
    err = result.stderr.strip().split("\n")[-1] if result.stderr else "Check failed"
    print(f"\n⚠️  Import check: {err}")

print("\n" + "="*70)
print("✅ DUPLICATE ROUTES REMOVED")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/")
print("="*70 + "\n")
