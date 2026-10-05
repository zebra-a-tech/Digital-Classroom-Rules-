"""Fix the parts[] index bug in paid_access.py gate"""

with open("paid_access.py", "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("paid_access_before_index_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved: paid_access_before_index_fix.py")

# ============================================================
# The bug: parts[3] used where parts[4] is needed
# Routes look like: /student/3/session/32
#                   parts[0]='', parts[1]='student', parts[2]='3',
#                   parts[3]='session', parts[4]='32'
# ============================================================

# Replace parts[3] with parts[4] inside the session handling block
old_block = 'len(parts) >= 4\n            and route == "session"'
new_block = 'len(parts) >= 5\n            and route == "session"'

if old_block in content:
    content = content.replace(old_block, new_block)
    print("✅ Fixed: len(parts) >= 4 → >= 5 for session route")

old_extract = 'trial_session_id = int(parts[3])'
new_extract = 'trial_session_id = int(parts[4])'

if old_extract in content:
    content = content.replace(old_extract, new_extract)
    print("✅ Fixed: parts[3] → parts[4] for session ID")

# Also fix the start-session/trial block (same pattern)
old_start = (
    'len(parts) >= 4\n'
    '            and route == "start-session"\n'
    '            and parts[3].lower() == "trial"'
)
new_start = (
    'len(parts) >= 4\n'
    '            and route == "start-session"\n'
    '            and parts[3].lower() == "trial"'
)
# This one is actually correct — parts[3] = "trial" ✅
print("ℹ️  start-session/trial block: parts[3]='trial' is CORRECT (no change)")

with open("paid_access.py", "w", encoding="utf-8") as f:
    f.write(content)

# Verify
with open("paid_access.py", "r", encoding="utf-8") as f:
    verify = f.read()

print("\n🔍 VERIFICATION:")
print(f"   'len(parts) >= 5' count: {verify.count('len(parts) >= 5')}")
print(f"   'parts[4]' count: {verify.count('parts[4]')}")
print(f"   'trial_session_id = int(parts[4])': {'✅' if 'trial_session_id = int(parts[4])' in verify else '❌'}")

print("\n" + "="*70)
print("✅ GATE INDEX FIX COMPLETE")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/student/3/trial")
print("="*70 + "\n")
