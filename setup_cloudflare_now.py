import os
import subprocess
import sys

print("\n" + "="*70)
print("☁️  DOWNLOADING CLOUDFLARED")
print("="*70 + "\n")

CF_PATH = os.path.expanduser("~/digital_classroom/cloudflared")
CF_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64"

# ============================================================
# STEP 1: Download if not present
# ============================================================
if os.path.exists(CF_PATH):
    print(f"✅ cloudflared already exists at {CF_PATH}")
else:
    print(f"📥 Downloading cloudflared...")
    print(f"   URL: {CF_URL}")
    print(f"   Target: {CF_PATH}\n")

    # Try wget first
    result = subprocess.run(
        ["wget", "-O", CF_PATH, CF_URL],
        capture_output=True, text=True
    )

    if result.returncode != 0 or not os.path.exists(CF_PATH) or os.path.getsize(CF_PATH) < 1000000:
        print(f"   ⚠️ wget failed or file too small. Trying curl...")
        result = subprocess.run(
            ["curl", "-L", "-o", CF_PATH, CF_URL],
            capture_output=True, text=True
        )

    if os.path.exists(CF_PATH):
        size_mb = os.path.getsize(CF_PATH) / 1024 / 1024
        print(f"   ✅ Downloaded: {size_mb:.1f} MB")
    else:
        print(f"   ❌ Download failed")
        print(f"   Try manually:")
        print(f"     wget {CF_URL} -O cloudflared")
        sys.exit(1)

# ============================================================
# STEP 2: Make executable
# ============================================================
print("\n🔧 Making executable...")
subprocess.run(["chmod", "+x", CF_PATH])
print("   ✅ Ready")

# ============================================================
# STEP 3: Verify
# ============================================================
print("\n🔍 Verifying installation...")
result = subprocess.run([CF_PATH, "--version"], capture_output=True, text=True)
if result.returncode == 0:
    print(f"   ✅ {result.stdout.strip()}")
else:
    print(f"   ⚠️ Version check: {result.stderr.strip()}")

# ============================================================
# STEP 4: Print next steps
# ============================================================
print("\n" + "="*70)
print("✅ CLOUDFLARED READY")
print("="*70)
print("""
📌 NOW DO THIS — in this exact order:

1️⃣  Make sure the student server is running.
    Open a NEW Termux session and run:

       cd ~/digital_classroom
       python student_server.py

2️⃣  In THIS terminal, start the tunnel:

       cd ~/digital_classroom
       ./cloudflared tunnel --url http://localhost:5001

3️⃣  You will see output like this:

       +---------------------------------------------------------+
       |  Your quick Tunnel has been created! Visit it at:       |
       |  https://random-words-here.trycloudflare.com            |
       +---------------------------------------------------------+

    📋 COPY THAT URL.

4️⃣  Test it in your browser:

       https://random-words-here.trycloudflare.com/student/1/home

    If it loads, the tunnel works!

5️⃣  Configure Meta:

       Webhook URL:  https://random-words-here.trycloudflare.com/whatsapp/webhook
       Verify Token: digital_classroom_verify_2026

6️⃣  Meta will verify the webhook. Once verified, send 'Hi' on WhatsApp.

📌 IMPORTANT:
   • The quick tunnel URL changes each time you restart it
   • For a permanent URL, you need a Cloudflare account + domain
   • Both are free but require 10 minutes of setup

📌 TO MAKE IT PERMANENT (optional):
   1. Sign up free at https://dash.cloudflare.com/sign-up
   2. Get a free domain (try https://www.freenom.com)
   3. Run: ./cloudflared tunnel login
   4. Then: ./cloudflared tunnel create digital-classroom
   5. Then: ./cloudflared tunnel route dns digital-classroom classroom.yourdomain.tk
   6. Then: ./cloudflared tunnel run digital-classroom

📌 META API IS FREE:
   You do NOT pay Meta anything for the first 1,000 conversations/month.
   WhatsApp Cloud API is free.
   You just need a Meta Business account (free) and Developer account (free).
""")
print("="*70 + "\n")
