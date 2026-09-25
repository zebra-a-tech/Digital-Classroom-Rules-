import os, re

print("\n" + "="*70)
print("🔍 FINDING THE ACTIVE STUDENT SERVER")
print("="*70 + "\n")

# Look for files that define Flask app and use port 5001
for f in sorted(os.listdir(".")):
    if not f.endswith(".py") or "backup" in f.lower():
        continue
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
    except:
        continue

    has_flask = "Flask(__name__)" in content or "app = Flask" in content
    has_port_5001 = "5001" in content
    has_curriculum = "curriculum" in content
    has_lessons = "FROM lessons" in content or "INSERT INTO lessons" in content

    if has_flask or has_port_5001:
        print(f"📄 {f}")
        print(f"   Flask app:      {'✅' if has_flask else '❌'}")
        print(f"   Port 5001:      {'✅' if has_port_5001 else '❌'}")
        print(f"   Uses curriculum:{'✅' if has_curriculum else '❌'}")
        print(f"   Uses lessons:   {'⚠️' if has_lessons else '❌'}")
        print()

print("="*70)
print("✅ SCAN COMPLETE")
print("="*70 + "\n")
