import os, re

print("\n" + "="*70)
print("🔍 FINDING FILES THAT QUERY THE 'lessons' TABLE")
print("="*70 + "\n")

files = [f for f in os.listdir(".") if f.endswith(".py")]
hits = []

for f in files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
            if "FROM lessons" in content or "INSERT INTO lessons" in content:
                lines = content.split("\n")
                matches = [(i+1, l.strip()) for i, l in enumerate(lines) if "lessons" in l.lower()]
                hits.append((f, matches))
    except Exception as e:
        pass

if not hits:
    print("   ⚠️ No files reference the 'lessons' table")
else:
    for f, matches in hits:
        print(f"📄 {f}")
        for lineno, line in matches[:5]:
            print(f"   line {lineno}: {line[:100]}")
        print()

print("="*70)
print("✅ SCAN COMPLETE")
print("="*70)
print("\n📌 NEXT: We will update these files to read from 'curriculum' instead.\n")
