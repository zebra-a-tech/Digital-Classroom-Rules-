import os, re

print("\n" + "="*70)
print("🔍 HUNTING FOR PLAYBOOK LOGIC & DEBUG LINE")
print("="*70 + "\n")

all_files = [f for f in os.listdir(".") if f.endswith(".py")]

# Files with PLAYBOOK DEBUG
print("1️⃣  Files containing 'PLAYBOOK DEBUG':")
found_debug = False
for f in all_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        if "PLAYBOOK DEBUG" in content:
            found_debug = True
            print(f"   ✅ {f}")
            # Show the exact line
            for i, line in enumerate(content.split("\n"), 1):
                if "PLAYBOOK DEBUG" in line:
                    print(f"      Line {i}: {line.strip()}")
    except:
        pass
if not found_debug:
    print("   ⚠️ NOT FOUND in any file")

# Files with /playbook route
print("\n2️⃣  Files containing '/playbook' route:")
for f in all_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        if "/playbook" in content:
            matches = [(i+1, l.strip()) for i, l in enumerate(content.split("\n")) 
                       if "/playbook" in l and ("@app.route" in l or "def " in l or "render_template" in l)]
            if matches:
                print(f"   ✅ {f}")
                for lineno, line in matches[:8]:
                    print(f"      Line {lineno}: {line[:110]}")
    except:
        pass

# Files with paid_content_gate
print("\n3️⃣  Files containing 'paid_content_gate':")
for f in all_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        if "paid_content_gate" in content:
            print(f"   ✅ {f}")
    except:
        pass

# Files with playbook-related templates
print("\n4️⃣  Files containing 'playbook' (case-insensitive, any context):")
count = 0
for f in all_files:
    try:
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read().lower()
        if "playbook" in content:
            count += 1
            if count <= 15:
                print(f"   • {f}")
    except:
        pass
if count > 15:
    print(f"   ... and {count - 15} more files")

print("\n" + "="*70)
print("✅ HUNT COMPLETE")
print("="*70 + "\n")
