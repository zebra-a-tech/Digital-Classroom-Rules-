FILE = "student_learning.py"

print("\n" + "="*70)
print("🔍 INSPECTING student_learning.py")
print("="*70 + "\n")

with open(FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"📄 Total lines: {len(lines)}\n")

print("🔧 FUNCTIONS DEFINED:")
print("-" * 70)
for i, line in enumerate(lines):
    if line.strip().startswith("def "):
        print(f"   Line {i+1}: {line.strip()}")

print("\n📚 CURRICULUM REFERENCES:")
print("-" * 70)
for i, line in enumerate(lines):
    if "curriculum" in line:
        print(f"   Line {i+1}: {line.strip()[:100]}")

print("\n" + "="*70)
print("✅ INSPECTION COMPLETE")
print("="*70 + "\n")
