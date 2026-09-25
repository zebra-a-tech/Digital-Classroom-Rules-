with open("paid_access.py", "r") as f:
    lines = f.readlines()

print("=" * 70)
print("PAID ACCESS GATE — showing key logic")
print("=" * 70 + "\n")

for i, line in enumerate(lines, 1):
    s = line.strip()
    if ("trial_active" in s or "paid" in s.lower() or "PLAYBOOK DEBUG" in s
        or "def " in s and "gate" in s.lower()):
        print(f"Line {i}: {s}")

print("\n" + "=" * 70)
