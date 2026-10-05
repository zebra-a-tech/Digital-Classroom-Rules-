import os, re

patterns = [
    r'password\s*=\s*["\'][^"\']+["\']',
    r'secret_key\s*=\s*["\'][^"\']+["\']',
    r'admin_pass\w*\s*=\s*["\'][^"\']+["\']',
    r'FOUNDER_KEY\s*=\s*["\'][^"\']+["\']'
]

print("=== SEARCHING FOR HARDCODED SECRETS & PASSWORDS ===")
for root, dirs, files in os.walk("."):
    if "venv" in root or ".git" in root or "__pycache__" in root:
        continue
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    for num, line in enumerate(f, 1):
                        for p in patterns:
                            if re.search(p, line, re.I):
                                print(f"{path}:{num} -> {line.strip()}")
            except Exception:
                pass
print("=== SEARCH COMPLETE ===")
