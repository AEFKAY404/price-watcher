import os
import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText

# =========================
# 🔧 CONFIG
# =========================

PRODUCTS = [
    {
        "name": "crucial RAM 8GB",
        "url": "https://www.amazon.in/dp/product/B0CWLSP9FG",
        "target": 5500
    },
    {
        "name": "crucial nvme SSD 512GB",
        "url": "https://www.amazon.in/dp/product/B09W31WDWB",
        "target": 5500
    }
]

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

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

            # Grab ALL visible prices on page
            elements = page.locator(".a-offscreen").all()

            for el in elements:
                try:
                    text = el.text_content()
                    if text and "₹" in text:
                        price = float(text.replace("₹", "").replace(",", ""))
                        
                        # Filter unrealistic values
                        if 100 < price < 100000:
                            browser.close()
                            return int(price)
                except:
                    continue

            print("❌ No valid price found:", url)
            browser.close()

    except Exception as e:
        print("❌ Playwright error:", e)

    return None

# =========================
# 📧 EMAIL (only on drop)
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

    except Exception as e:
        print("❌ Email failed:", e)

# =========================
# 📱 TELEGRAM (always)
# =========================

def send_telegram(message):
    try:
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("⚠️ Telegram not configured")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        response = requests.post(url, data=data)

        if response.status_code == 200:
            print("📱 Telegram sent")
        else:
            print("❌ Telegram failed")

    except Exception as e:
        print("❌ Telegram error")
        

# =========================
# 🚀 MAIN
# =========================

def main():
    report = f"📊 Price Check ({datetime.now()})\n\n"
    send_telegram("TEST MESSAGE")
    for product in PRODUCTS:
        price = get_price(product["url"])

        if price:
            report += f"{product['name']}: ₹{price}\n"

            if price <= product["target"]:
                send_email(product, price)
        else:
            report += f"{product['name']}: ❌ Failed\n"

    send_telegram(report)

    print(report)

if __name__ == "__main__":
    main()