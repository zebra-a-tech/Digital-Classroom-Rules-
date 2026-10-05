import os, flask

os.environ["TURSO_DATABASE_URL"] = "https://digital-classroom-zebra-a-tech.aws-us-west-2.turso.io"
os.environ["TURSO_AUTH_TOKEN"] = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTExMjM5NDcsImlkIjoiMDFhMTA2ZjktMDAwMS03M2YxLWI0NmYtNmYxNjc4ZGE0MDc0Iiwia2lkIjoieVBETDhuc3QzaG85UnczMGNHSmdTRlJmbXlFbGJINE1OUGR1bzhrVkpEcyIsInJpZCI6ImMwNWEyOWM4LTZkNzMtNDkyMS1iMDM5LTRlNDllMjk1Yjg1MSJ9.YPcBpbC5pySAC3pnQx6YRnAw-E8CnB3WzgNBw--5ZbUEIZEDCd9bLoCXIBV9-I3JEyzsRZ7tbssj_86FLjEPBA"

import turso_db
import student_server as srv

app = [v for v in vars(srv).values() if isinstance(v, flask.Flask)][0]
app.testing = True
c = app.test_client()
conn = turso_db.connect()

# Find student
stu = conn.execute("SELECT id, name, current_subject, free_trial_used FROM students LIMIT 1").fetchone()
sid = stu["id"]
print(f"=== Testing with Student ID {sid} ({stu['name']}) ===")
print(f"Subject: {stu['current_subject']} | Free trial used flag: {stu['free_trial_used']}")

# Ensure student has an active trial session for testing
c.get(f"/student/{sid}/start-session/trial", follow_redirects=True)

routes = [
    f"/student/{sid}/trial",
    f"/student/{sid}/trial-lesson",
    f"/student/{sid}/learning",
    f"/student/{sid}/learn?subject={stu['current_subject'] or 'English'}",
    f"/student/{sid}/playbook"
]

for r_url in routes:
    resp = c.get(r_url, follow_redirects=True)
    body = resp.get_data(as_text=True)
    title = body.split("<title>")[1].split("</title>")[0].strip() if "<title>" in body else "No Title"
    
    # Check what is inside
    blocked = "Unlock" in body or "Payment" in body or "trial has expired" in body.lower() or resp.status_code != 200
    print(f"\nRoute: {r_url}")
    print(f"  Final URL: {resp.request.path} (HTTP {resp.status_code})")
    print(f"  Title: {title}")
    if blocked:
        print(f"  ⚠️ BLOCKED: Page redirected or paywalled!")
        # Print a short snippet to see why
        print("  Snippet:", " ".join(body[:200].split()))
    else:
        print("  ✅ ACCESSIBLE")
