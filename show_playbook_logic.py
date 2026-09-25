with open("student_server.py", "r") as f:
    lines = f.readlines()

print("=" * 70)
print("PLAYBOOK ROUTE LOGIC")
print("=" * 70 + "\n")

# Find the playbook route and show 80 lines around it
for i, line in enumerate(lines):
    if "/playbook" in line and "@app.route" in line:
        print(f"🎯 Found at line {i+1}: {line.strip()}\n")
        print("-" * 70)
        # Show 80 lines after
        start = i
        end = min(i + 80, len(lines))
        for j in range(start, end):
            marker = "▶️ " if j == i else "   "
            print(f"{marker}{j+1}: {lines[j].rstrip()}")
        print("-" * 70)
        break

# Also find PLAYBOOK DEBUG reference
print("\n🔍 Searching for 'PLAYBOOK DEBUG':")
for i, line in enumerate(lines):
    if "PLAYBOOK DEBUG" in line:
        print(f"   Line {i+1}: {line.strip()}")

# And the paid_content_gate function
print("\n🔍 Searching for 'paid_content_gate':")
for i, line in enumerate(lines):
    if "paid_content_gate" in line:
        print(f"   Line {i+1}: {line.strip()}")

print("\n" + "=" * 70)
