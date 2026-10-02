import sqlite3
import random

DATABASE = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
TUTORS = [
    "Tariro",
    "Tendai",
    "Nyasha",
    "Tatenda",
    "Rudo",
    "Blessing",
    "Brian",
    "Grace",
    "Michael",
    "Sarah"
]

def assign_tutor():
    return random.choice(TUTORS)

def register_student(name, age, school, location, grade_form, subject, exam_board):
    db = sqlite3.connect(DATABASE)
    cursor = db.cursor()

    tutor = assign_tutor()

    cursor.execute("""
        INSERT INTO students
        (name, age, school, location, grade_form, subject, exam_board, tutor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        school,
        location,
        grade_form,
        subject,
        exam_board,
        tutor
    ))

    student_id = cursor.lastrowid

    db.commit()
    db.close()

    return student_id, tutor

if __name__ == "__main__":
    print("Digital Classroom Rules Registration Engine")
    print("-------------------------------------------")

    name = input("Student name: ")
    age = int(input("Age: "))
    school = input("School: ")
    location = input("Location: ")
    grade_form = input("Grade/Form: ")
    subject = input("Subject: ")
    exam_board = input("Exam Board (ZIMSEC/Cambridge/Don't Know): ")

    student_id, tutor = register_student(
        name,
        age,
        school,
        location,
        grade_form,
        subject,
        exam_board
    )

    print()
    print("Registration successful!")
    print(f"Student ID: DCR-{student_id:05d}")
    print(f"Permanent Tutor: {tutor}")
    print("Free Trial: AVAILABLE")
