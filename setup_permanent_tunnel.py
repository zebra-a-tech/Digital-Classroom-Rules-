import os
import subprocess
import sys

print("\n" + "="*70)
print("🌐 PERMANENT CLOUDFLARE TUNNEL SETUP")
print("="*70 + "\n")

CF_PATH = os.path.expanduser("~/digital_classroom/cloudflared")

if not os.path.exists(CF_PATH):
    print("❌ cloudflared not found. Please run setup_cloudflare_tunnel.py first.")
    sys.exit(1)

print("✅ cloudflared binary found\n")

# ============================================================
# STEP 1: Guide for manual login
# ============================================================
print("="*70)
print("📝 STEP 1 — LOGIN TO CLOUDFLARE")
print("="*70)
print("""
We need to log you into Cloudflare first.

Run this command:

   cd ~/digital_classroom
   ./cloudflared tunnel login

This will:
   1. Open a URL in your browser
   2. Ask you to log in to Cloudflare
   3. Ask you to authorize a domain

If you don't have a Cloudflare account yet:
   → Go to https://dash.cloudflare.com/sign-up
   → Sign up for FREE
   → Come back and run the login command

Do you have a domain name? (like "digitalclassroom.co.zw")
""")

response = input("Do you have a domain? (yes/no): ").strip().lower()

if response == "no":
    print("""
==================================================
📌 NO DOMAIN? Here are your options:
==================================================

Option 1: Get a FREE domain
   • Go to https://www.freenom.com
   • Register a free domain like: digitalclassroom.tk
   • Point it to Cloudflare
   • Cost: $0

Option 2: Use Cloudflare's free subdomain
   • Cloudflare gives you a free subdomain: yourname.pages.dev
   • But this is only for Pages, not tunnels

Option 3: Skip the permanent tunnel for now
   • Use the quick tunnel (URL changes on restart)
   • We can upgrade to permanent later

Option 4: Use a different provider
   • Railway.app (free, stable URL)
   • Render.com (free, stable URL)
   • Fly.io (free, stable URL)

RECOMMENDED: Get a free domain from Freenom, then come back.

==================================================
""")
    sys.exit(0)

# ============================================================
# STEP 2: Create permanent tunnel
# ============================================================
print("\n" + "="*70)
print("📝 STEP 2 — CREATE PERMANENT TUNNEL")
print("="*70)
print("""
Now run these commands ONE AT A TIME:

   1. Create the tunnel:
      ./cloudflared tunnel create digital-classroom

   2. Create a DNS route (replace yourdomain.com):
      ./cloudflared tunnel route dns digital-classroom classroom.yourdomain.com

   3. Create the config file:

      cat > ~/.cloudflared/config.yml << 'EOF'
      tunnel: digital-classroom
      credentials-file: ~/.cloudflared/<TUNNEL-ID>.json

      ingress:
        - hostname: classroom.yourdomain.com
          service: http://localhost:5001
        - service: http_status:404
      EOF

      (Replace <TUNNEL-ID> with the actual ID from step 1)

   4. Run the tunnel:
      ./cloudflared tunnel run digital-classroom

   5. Your permanent URL will be:
      https://classroom.yourdomain.com

   6. Use this URL in Meta:
      https://classroom.yourdomain.com/whatsapp/webhook

==================================================
""")

# ============================================================
# STEP 3: Alternative — use free Railway.app
# ============================================================
print("="*70)
print("🚂 ALTERNATIVE — RAILWAY.APP (Free, stable URL)")
print("="*70)
print("""
If you don't want to mess with domains, use Railway.app:

Pros:
   ✅ Free $5/month credit (enough for small Flask app)
   ✅ Stable URL: yourname.up.railway.app
   ✅ 24/7 uptime (no phone needed)
   ✅ Auto-deploy from GitHub

Cons:
   ❌ Need to move code off your phone
   ❌ Need a GitHub account

Steps:
   1. Create GitHub account (free)
   2. Push your code to GitHub
   3. Sign up at railway.app
   4. Click "New Project" → "Deploy from GitHub"
   5. Select your repo
   6. Railway deploys automatically
   7. Get stable URL: https://yourname.up.railway.app

==================================================
""")

# ============================================================
# STEP 4: Alternative — use Render.com
# ============================================================
print("="*70)
print("🎨 ALTERNATIVE — RENDER.COM (Free tier)")
print("="*70)
print("""
Render.com gives you a free web service:

Pros:
   ✅ Free tier (with 15-min sleep)
   ✅ Stable URL: yourname.onrender.com
   ✅ Auto-deploy from GitHub

Cons:
   ❌ Sleeps after 15 min of inactivity
   ❌ Cold start takes 30 seconds
   ❌ Not good for real-time WhatsApp

==================================================
""")

print("\n📌 QUICK DECISION GUIDE:")
print("""
For WhatsApp + Meta, you need a STABLE URL.
Best free options:

   ⭐ 1. Cloudflare Permanent Tunnel + Free Domain (Freenom)
   ⭐ 2. Railway.app (easiest, most reliable)
   ⭐ 3. Render.com (free but slow)

AVOID:
   ❌ ngrok free (URL changes every restart)
   ❌ Cloudflare Quick Tunnel (URL changes on restart)

""")

print("="*70)
print("📌 NEXT STEP:")
print("="*70)
print("""
Choose ONE:

   A) Get a free domain from freenom.com → set up permanent Cloudflare tunnel
   B) Sign up for Railway.app → deploy from GitHub
   C) Use the temporary tunnel for now → test WhatsApp → upgrade later

Reply with A, B, or C and I will give you the exact commands.
""")
print("="*70 + "\n")
