"""Simplified session access check"""

with open("paid_access.py", "r", encoding="utf-8") as f:
    content = f.read()

# ============================================================
# Replace the session check block with a simplified version
# ============================================================
old_block = '''if (
            len(parts) >= 5
            and route == "session"
        ):
            try:
                trial_session_id = int(parts[4])

                conn = db()
                trial_row = conn.execute("""
                    SELECT id, student_id, session_type, expires_at, paused
                    FROM student_sessions
                    WHERE id=?
                      AND student_id=?
                      """, (trial_session_id, student_id)).fetchone()
                conn.close()

                if trial_row:
                    from datetime import datetime

                    # A paused unfinished trial remains accessible.
                    if trial_row["paused"]:
                        return None

                    expires = datetime.fromisoformat(
                        trial_row["expires_at"]
                    )

                    if datetime.now() < expires:
                        return None

            except Exception:
                pass'''

new_block = '''if (
            len(parts) >= 5
            and route == "session"
        ):
            try:
                trial_session_id = int(parts[4])

                conn = db()
                trial_row = conn.execute("""
                    SELECT id, student_id, session_type, expires_at, paused
                    FROM student_sessions
                    WHERE id=?
                      AND student_id=?
                    LIMIT 1
                """, (trial_session_id, student_id)).fetchone()
                conn.close()

                print(f"GATE SESSION CHECK: session_id={trial_session_id}, student={student_id}, found={bool(trial_row)}", flush=True)

                if trial_row:
                    from datetime import datetime

                    # Paused = allow access
                    if trial_row["paused"]:
                        print(f"GATE: allowing paused session", flush=True)
                        return None

                    # Check expiry
                    try:
                        expires = datetime.fromisoformat(trial_row["expires_at"])
                        if datetime.now() < expires:
                            print(f"GATE: allowing unexpired session (expires {expires})", flush=True)
                            return None
                        else:
                            print(f"GATE: session EXPIRED (was {expires})", flush=True)
                    except Exception as ex:
                        print(f"GATE: expiry parse error: {ex}", flush=True)
                        return None  # Allow if we can't parse

            except Exception as ex:
                print(f"GATE: session lookup error: {ex}", flush=True)
                pass'''

if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ Replaced session check block")
else:
    print("⚠️ Pattern not found")
    # Try alternate pattern
    import re
    match = re.search(
        r'if \(\s*\n\s*len\(parts\) >= 5\s*\n\s*and route == "session"\s*\n\s*\):.*?except Exception:\s*\n\s*pass',
        content,
        re.DOTALL
    )
    if match:
        content = content[:match.start()] + new_block + content[match.end():]
        print("✅ Replaced session check block (regex)")
    else:
        print("❌ Could not find session check block")

with open("paid_access.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ Done")
