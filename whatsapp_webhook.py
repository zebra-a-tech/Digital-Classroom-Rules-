"""WhatsApp Cloud API webhook for Digital Classroom Rules.

Receives incoming WhatsApp messages from Meta, routes them to
the right handler, and sends replies back via WhatsApp Cloud API.
"""

import os
import json
import sqlite3
import requests
from datetime import datetime
from flask import request, jsonify
# WhatsApp tutoring bridge — same brain as the web tutor.
try:
    from learning_bridge import ask_tutor as _ask_tutor
    _HAS_BRIDGE = True
except Exception as _bridge_err:
    _ask_tutor = None
    _HAS_BRIDGE = False
    print('whatsapp: learning_bridge unavailable:', _bridge_err)

DB = "digital_classroom.db"

WHATSAPP_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID = os.environ.get("WHATSAPP_PHONE_ID", "")
VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "digital_classroom_verify_2026")

GRAPH_URL = "https://graph.facebook.com/v18.0"


def _db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def send_whatsapp_message(to_number, text):
    """Send a text message via WhatsApp Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        print("⚠️ WhatsApp credentials not set — skipping send")
        return False

    url = f"{GRAPH_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=10)
        print(f"📤 Sent to {to_number}: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"❌ WhatsApp send error: {e}")
        return False


def log_incoming(from_number, message_text, message_type="text", raw_payload=None):
    """Log an incoming message."""
    try:
        conn = _db()
        conn.execute("""
            INSERT INTO whatsapp_messages
            (from_number, message_text, message_type, direction, raw_payload)
            VALUES (?, ?, ?, 'incoming', ?)
        """, (from_number, message_text, message_type,
              json.dumps(raw_payload)[:2000] if raw_payload else None))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Log error: {e}")


def find_student_by_phone(phone_number):
    """Match a WhatsApp number to a student."""
    try:
        normalized = phone_number.replace("+", "").replace(" ", "").strip()
        conn = _db()
        student = conn.execute("""
            SELECT s.* FROM students s
            INNER JOIN whatsapp_users w ON w.student_id = s.id
            WHERE w.phone_number LIKE ?
        """, (f"%{normalized[-9:]}%",)).fetchone()
        conn.close()
        return student
    except Exception as e:
        print(f"⚠️ Lookup error: {e}")
        return None


def register_whatsapp_user(phone_number, student_id=None, name=None):
    """Register a phone number as a WhatsApp user."""
    try:
        conn = _db()
        existing = conn.execute(
            "SELECT * FROM whatsapp_users WHERE phone_number = ?", (phone_number,)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE whatsapp_users
                SET last_seen = ?, student_id = COALESCE(?, student_id),
                    name = COALESCE(?, name), is_registered = 1
                WHERE phone_number = ?
            """, (datetime.now().isoformat(), student_id, name, phone_number))
        else:
            conn.execute("""
                INSERT INTO whatsapp_users (phone_number, student_id, name, is_registered)
                VALUES (?, ?, ?, 1)
            """, (phone_number, student_id, name))

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Register error: {e}")


def route_message(phone_number, text):
    """Return a response string for an incoming message."""
    text = (text or "").strip()
    lower = text.lower()

    student = find_student_by_phone(phone_number)

    # ---------- Unregistered users ----------
    if not student:
        if lower in ("hi", "hello", "hey", "start", "mhoro", "sawubona", "menu"):
            return (
                "👋 Welcome to Digital Classroom Rules!\n\n"
                "I am your personal tutor. To get started, please tell me your *first name*."
            )
        elif len(text.split()) <= 3 and text.replace(" ", "").isalpha():
            name = text.strip()
            register_whatsapp_user(phone_number, name=name)
            return (
                f"Nice to meet you, *{name}*! 🎉\n\n"
                "Now, tell me your *grade or form*.\n"
                "Example: Grade 7, Form 3"
            )
        else:
            return "🤔 I don't recognise you yet. Type *Hi* to start registration."

    # ---------- Registered users ----------
    sid = student["id"]
    name = student["name"]

    if lower in ("hi", "hello", "hey", "menu", "start"):
        return (
            f"👋 Welcome back, *{name}*!\n\n"
            "What would you like to do?\n\n"
            "📘 *LESSONS* — start a lesson\n"
            "📝 *HOMEWORK* — see your assignments\n"
            "💰 *PAY* — unlock a paid session ($1)\n"
            "📊 *PROGRESS* — see your stats\n"
            "💡 *STUDY TIPS* — get study advice\n"
            "❓ *HELP* — full list of commands"
        )
    elif lower in ("lessons", "learn", "playbook"):
        return f"📘 Your lessons are ready, *{name}*. Open them at /student/{sid}/playbook on the web."
    elif lower == "homework":
        return f"📝 Your assignments are waiting. Open them at /student/{sid}/homework on the web."
    elif lower == "pay":
        return (
            "💰 *Unlock Full Access for $1*\n\n"
            "Send $1 via:\n"
            "📱 EcoCash: Lucky Munyanyiwa — 0790 026 436\n"
            "📱 Mukuru: Lucky Munyanyiwa — +263 719 809 683\n\n"
            "After payment, reply *PAID* and I will verify."
        )
    elif lower in ("progress", "stats"):
        return (
            f"📊 *Your Progress*\n\n"
            f"🔥 Streak: {student['streak'] or 0} days\n"
            f"📚 Paid lessons: {student['paid_lessons'] or 0}\n"
            f"📖 Grade: {student['grade_form']}"
        )
    elif lower in ("study tips", "tips"):
        return (
            "💡 *Study Tips*\n\n"
            "1. 25 min study, 5 min break\n"
            "2. Read questions twice\n"
            "3. Teach a friend\n"
            "4. Sleep 8 hours\n"
            "5. Practice past papers"
        )
    elif lower == "help":
        return (
            "❓ *Commands:*\n\n"
            "📘 LESSONS\n📝 HOMEWORK\n💰 PAY\n📊 PROGRESS\n"
            "💡 STUDY TIPS\n👤 SPEAK\n🔗 SHARE\n\n"
            f"Full web: /student/{sid}/home"
        )
    elif lower == "paid":
        return (
            "✅ Payment claim received!\n\n"
            "Lucky will verify within 1 minute. Watch this chat for confirmation."
        )
    elif lower in ("speak", "human"):
        return "👤 Connecting you to *Lucky* (the founder). Please type your message below."
    else:
        # ------------------------------------------------------------
        # WhatsApp tutoring bridge — same brain as the web tutor.
        # Grade-aware, subject-safe, tutor-memory-aware.
        # ------------------------------------------------------------
        if _HAS_BRIDGE and _ask_tutor:
            try:
                result = _ask_tutor(sid, text)
                note  = (result or {}).get("note") or ""
                reply = (result or {}).get("response") or ""
                if note:
                    return f"{note}\n\n{reply}"
                return reply or "I couldn't work out an answer for that. Try rephrasing."
            except Exception as _e:
                print(f"whatsapp: ask_tutor failed: {_e}")
                return (
                    "I had trouble understanding that just now. "
                    "Try asking again in a simpler way, or type *HELP*."
                )
        return f"🤔 I didn't understand, *{name}*. Type *HELP* to see all commands."


def register_whatsapp_webhook(app):
    """Register WhatsApp webhook routes."""

    @app.route("/whatsapp/webhook", methods=["GET"])
    def whatsapp_verify():
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ WhatsApp webhook verified")
            return challenge or "", 200
        print(f"❌ WhatsApp verification failed: mode={mode} token={token}")
        return "Forbidden", 403

    @app.route("/whatsapp/webhook", methods=["POST"])
    def whatsapp_receive():
        data = request.get_json(silent=True) or {}
        try:
            for entry in data.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for msg in value.get("messages", []):
                        from_number = msg.get("from")
                        msg_type = msg.get("type", "text")
                        if msg_type == "text":
                            text = msg.get("text", {}).get("body", "")
                        else:
                            text = f"[{msg_type} message]"
                        print(f"📨 From {from_number}: {text}")
                        log_incoming(from_number, text, msg_type, msg)
                        reply = route_message(from_number, text)
                        send_whatsapp_message(from_number, reply)
        except Exception as e:
            print(f"❌ Webhook error: {e}")
        return jsonify({"status": "ok"}), 200
