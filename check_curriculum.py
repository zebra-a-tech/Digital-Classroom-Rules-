import sqlite3

conn = sqlite3.connect("digital_classroom.db")
c = conn.cursor()

print("\n" + "="*70)
print("📚 CURRICULUM COVERAGE CHECK")
print("="*70)

grades = ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7",
          "Form 1","Form 2","Form 3","Form 4","Form 5","Form 6"]

subjects = ["Maths","English","Science","Social Studies","Geography",
            "History","Biology","Chemistry","Physics","Economics","Accounting"]

print("\n📊 LESSONS PER GRADE:")
for g in grades:
    c.execute("SELECT COUNT(*) FROM lessons WHERE grade_form = ?", (g,))
    count = c.fetchone()[0]
    status = "✅" if count > 0 else "❌ MISSING"
    print(f"   {status} {g}: {count} lessons")

print("\n📊 LESSONS PER SUBJECT:")
for s in subjects:
    c.execute("SELECT COUNT(*) FROM lessons WHERE subject = ?", (s,))
    count = c.fetchone()[0]
    status = "✅" if count > 0 else "❌ MISSING"
    print(f"   {status} {s}: {count} lessons")

print("\n📊 COMPLETE CURRICULUM GRID (Grade × Subject):")
print(f"   {'Grade':<10} | " + " | ".join(f"{s[:8]:<8}" for s in subjects))
print("   " + "-" * 110)
for g in grades:
    row = f"   {g:<10} | "
    for s in subjects:
        c.execute("SELECT COUNT(*) FROM lessons WHERE grade_form = ? AND subject = ?", (g, s))
        count = c.fetchone()[0]
        row += f"{('✅' if count > 0 else '❌'):<8} | "
    print(row)

# Check grade 1-4 parent-assisted setup
print("\n📊 GRADE 1-4 PARENT-ASSISTANCE CHECK:")
for g in ["Grade 1","Grade 2","Grade 3","Grade 4"]:
    c.execute("SELECT COUNT(*) FROM lessons WHERE grade_form = ?", (g,))
    count = c.fetchone()[0]
    print(f"   {g}: {count} lessons — need parent-assist flag?")

conn.close()
print("\n" + "="*70 + "\n")
