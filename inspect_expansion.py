FILE = "curriculum_expansion.py"

print("\n" + "="*70)
print("🔍 INSPECTING curriculum_expansion.py")
print("="*70 + "\n")

with open(FILE, "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()
    lines = content.split("\n")

print(f"📄 Total lines: {len(lines)}\n")

# Count CURRICULUM_EXPANSION entries
print("📊 CURRICULUM_EXPANSION STRUCTURE:")
print("-" * 70)

# Find all subject/topic keys
import re
keys = re.findall(r'\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*\)', content)
print(f"   Total (subject, topic) pairs: {len(keys)}")

# Group by subject
from collections import Counter
subjects = Counter(k[0] for k in keys)
print("\n   By subject:")
for subj, count in subjects.most_common():
    print(f"      {subj:<20} : {count}")

print("\n" + "="*70)
print("✅ INSPECTION COMPLETE")
print("="*70 + "\n")
