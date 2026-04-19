import os
import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import smtplib
import json
from email.mime.text import MIMEText

# =========================
# 🔧 CONFIG
# =========================

def load_products():
    try:
        with open("products.json", "r") as f:
            return json.load(f)
    except:
        print("❌ Failed to load products.json")
        return []

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# =========================
# 🧠 SCRAPER
# =========================

def get_price(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            page = context.new_page()

            page.goto(url, timeout=60000)
            page.wait_for_load_state("networkidle")
            time.sleep(4)

            elements = page.locator(".a-offscreen").all()

            for el in elements:
                try:
                    text = el.text_content()
                    if text and "₹" in text:
                        price = float(text.replace("₹", "").replace(",", ""))
                        if 100 < price < 200000:
                            browser.close()
                            return int(price)
                except:
                    continue

            print("❌ Price not found")
            browser.close()

    except Exception:
        print("❌ Playwright error")

    return None

# =========================
# 📧 EMAIL
# =========================

def send_email(product, price):
    try:
        msg = MIMEText(f"🔥 {product['name']} dropped to ₹{price}\n{product['url']}")
        msg["Subject"] = f"Price Alert: {product['name']}"
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print(f"📧 Email sent for {product['name']}")

    except:
        print("❌ Email failed")

# =========================
# 📱 TELEGRAM
# =========================

def send_telegram(message):
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Telegram not configured")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": message})

        print("📱 Telegram sent")

    except:
        print("❌ Telegram error")

# =========================
# 🌐 SUPABASE
# =========================

def send_to_supabase(rows):
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("⚠️ Supabase not configured")
            return

        url = f"{SUPABASE_URL}/rest/v1/prices"

        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

        response = requests.post(url, json=rows, headers=headers)

        if response.status_code in (200, 201):
            print("🟢 Data sent to Supabase")
        else:
            print("❌ Supabase insert failed:", response.text)

    except:
        print("❌ Supabase error")

# =========================
# 🚀 MAIN
# =========================

def main():
    report = f"📊 Price Check ({datetime.now()})\n\n"
    products = load_products()

    if not products:
        print("⚠️ No products found")
        return

    rows = []

    for product in products:
        price = get_price(product["url"])

        if price:
            report += f"{product['name']}: ₹{price}\n"

            if price <= product["target"]:
                send_email(product, price)
        else:
            report += f"{product['name']}: ❌ Failed\n"

        # ✅ Always store row
        rows.append({
            "name": product["name"],
            "price": price if price else None,
            "target": product["target"],
            "url": product["url"],
            "timestamp": datetime.now().isoformat()
        })

    send_telegram(report)
    send_to_supabase(rows)

    print(report)

if __name__ == "__main__":
    main()