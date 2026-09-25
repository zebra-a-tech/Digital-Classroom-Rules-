FILE = "student_server.py"

print("\n" + "="*70)
print("🔍 CHECKING register vs app.run() ORDER")
print("="*70 + "\n")

with open(FILE, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"📄 Total lines: {len(lines)}\n")

print("📍 KEY LINES:")
print("-" * 70)
for i, line in enumerate(lines, 1):
    s = line.strip()
    if "register_student_learning" in s:
        print(f"   Line {i}: {s}")
    if "app.run(" in s:
        print(f"   Line {i}: {s}")
    if "register_paid_access" in s:
        print(f"   Line {i}: {s}")

print("\n" + "="*70)
print("✅ CHECK COMPLETE")
print("="*70 + "\n")
