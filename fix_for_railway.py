FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_railway.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if already patched
if "RAILWAY_PORT_FIX" in content:
    print("✅ Already patched")
    exit(0)

# Find the app.run line
old_run = 'app.run(host="127.0.0.1",port=5001,debug=False)'
new_run = '''# RAILWAY_PORT_FIX
import os as _railway_os
_port = int(_railway_os.environ.get("PORT", 5001))
_host = "0.0.0.0" if _railway_os.environ.get("RAILWAY_ENVIRONMENT") else "127.0.0.1"
app.run(host=_host, port=_port, debug=False)'''

if old_run in content:
    content = content.replace(old_run, new_run)
    print("✅ Patched app.run for Railway")
elif 'app.run(host="127.0.0.1", port=5001' in content:
    # Alternative spacing
    content = content.replace(
        'app.run(host="127.0.0.1", port=5001, debug=False)',
        new_run
    )
    print("✅ Patched with alternative spacing")
else:
    # Search for any app.run
    import re
    match = re.search(r'app\.run\([^)]+\)', content)
    if match:
        content = content[:match.start()] + new_run + content[match.end():]
        print(f"✅ Patched: {match.group()}")
    else:
        print("❌ Could not find app.run()")
        exit(1)

# Also need to handle database initialization on Railway
# Add DB initialization at startup
if "RAILWAY_DB_INIT" not in content:
    # Find where app = Flask is
    import re
    app_match = re.search(r'app\s*=\s*Flask\s*\([^)]*\)', content)
    if app_match:
        db_init = '''

# RAILWAY_DB_INIT — ensure database exists on startup
import os as _db_os
if not _db_os.path.exists("digital_classroom.db"):
    print("⚠️ Database not found — will be created by app")
'''
        content = content[:app_match.end()] + db_init + content[app_match.end():]
        print("✅ Added database init check")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ student_server.py is Railway-ready")
