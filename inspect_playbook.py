with open("student_playbook.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print("\n" + "="*70)
print("🔍 INSPECTING student_playbook.py — PLAYBOOK ROUTE (lines 855-960)")
print("="*70 + "\n")

# Show the playbook main route logic
for i in range(855, min(965, len(lines))):
    print(f"{i+1:4d}: {lines[i].rstrip()}")

print("\n" + "="*70)
print("🔍 INSPECTING student_playbook.py — TOPIC ROUTE (lines 945-1050)")
print("="*70 + "\n")

for i in range(945, min(1055, len(lines))):
    print(f"{i+1:4d}: {lines[i].rstrip()}")

print("\n" + "="*70)
