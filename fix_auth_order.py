import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_order_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Find positions
auth_pos = content.find("register_auth_routes(app)")
run_pos = content.find("app.run(")

print(f"   register_auth_routes at position: {auth_pos}")
print(f"   app.run at position: {run_pos}")

if auth_pos == -1:
    print("❌ register_auth_routes not found in file")
    exit(1)

if run_pos == -1:
    print("❌ app.run not found in file")
    exit(1)

if auth_pos < run_pos:
    print("✅ register_auth_routes is BEFORE app.run — correct!")
    exit(0)

print("⚠️ register_auth_routes is AFTER app.run — fixing...")

# Remove the current registration line
content = content.replace("register_auth_routes(app)", "# (moved)", 1)

# Insert it before app.run
new_run_pos = content.find("app.run(")
content = content[:new_run_pos] + "register_auth_routes(app)\n\n" + content[new_run_pos:]

# Write back
with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Moved register_auth_routes BEFORE app.run")

# Verify
with open(SERVER, "r", encoding="utf-8") as f:
    verify = f.read()

auth_pos = verify.find("register_auth_routes(app)")
run_pos = verify.find("app.run(")

print(f"\n   New positions:")
print(f"   register_auth_routes: {auth_pos}")
print(f"   app.run: {run_pos}")

if auth_pos < run_pos:
    print("   ✅ Order is now correct")
else:
    print("   ❌ Still wrong")
