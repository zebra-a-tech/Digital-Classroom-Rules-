import sqlite3, datetime

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n🔧 Aligning test data for a clean end-to-end test...")

# Align the PENDING payment subject to match the student's actual subject
c.execute("SELECT subject, grade_form FROM students WHERE id = 1")
s = c.fetchone()
if s:
    student_subject = s[0]
    student_grade = s[1]
    print(f"   Student 1 is doing {student_subject} ({student_grade})")

    # Update the newest PENDING request to match
    c.execute("""
        UPDATE payment_requests
        SET subject = ?
        WHERE id = (SELECT MAX(id) FROM payment_requests WHERE status = 'PENDING')
    """, (student_subject,))
    print(f"   ✅ Updated PENDING request to subject: {student_subject}")

# Show current state
print("\n📊 CURRENT STATE:")
c.execute("""
    SELECT id, subject, amount, status FROM payment_requests
    WHERE status = 'PENDING' ORDER BY id DESC
""")
for r in c.fetchall():
    print(f"   • Request #{r[0]} | {r[1]} | ${r[2]} | {r[3]}")

conn.commit()
conn.close()
print("\n✅ Ready for testing.\n")
