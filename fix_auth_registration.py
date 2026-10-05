"""Ensure register_auth_routes is called"""

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

if "register_auth_routes(app)" in content:
    print("✅ register_auth_routes already called")
else:
    print("❌ register_auth_routes NOT called — adding it")
    
    # Add it right after the other registrations
    marker = "register_student_learning(app)"
    if marker in content:
        content = content.replace(
            marker,
            marker + "\nregister_auth_routes(app)",
            1
        )
        print("✅ Added register_auth_routes(app)")
    else:
        # Fallback: add before app.run
        run_pos = content.rfind("app.run(")
        if run_pos > 0:
            content = content[:run_pos] + "register_auth_routes(app)\n\n" + content[run_pos:]
            print("✅ Added before app.run")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ DONE")
