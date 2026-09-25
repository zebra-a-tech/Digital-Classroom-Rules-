import re

FILE = "student_server.py"

print("\n" + "="*70)
print("🔍 INSPECTING student_server.py")
print("="*70 + "\n")

with open(FILE, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

print(f"📄 Total lines: {len(lines)}\n")

# Find all @app.route decorators and what they call
print("🗺️  ROUTES DEFINED IN student_server.py:")
print("-" * 70)
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("@app.route"):
        route = stripped
        # Find the function definition on the next few lines
        for j in range(i+1, min(i+5, len(lines))):
            if lines[j].strip().startswith("def "):
                func = lines[j].strip()
                print(f"   {route}")
                print(f"      → {func}\n")
                break

# Find references to curriculum, lessons, playbook, learn
print("\n📚 KEYWORD REFERENCES:")
print("-" * 70)
keywords = ["curriculum", "FROM lessons", "playbook", "student_learning",
            "student_academy", "import ", "get_lesson", "lesson_data"]
for kw in keywords:
    count = sum(1 for l in lines if kw in l)
    print(f"   {kw:<25} : {count} occurrences")

# Show what the file imports
print("\n📦 IMPORTS:")
print("-" * 70)
for line in lines:
    s = line.strip()
    if s.startswith("import ") or s.startswith("from "):
        print(f"   {s}")
    if s.startswith("def ") and "app" in s.lower():
        pass
    # Stop scanning imports after first 50 lines
    if line.strip().startswith("@app.route"):
        break

print("\n" + "="*70)
print("✅ INSPECTION COMPLETE")
print("="*70 + "\n")
