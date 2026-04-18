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
        "url": "https://www.amazon.in/dp/B0CG3H8TTN",
        "target": 4000
    },
    {
        "name": "crucial nvme SSD 512GB",
        "url": "PASTE_SSD_LINK_HERE",
        "target": 3500
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

            selectors = [
                ".a-price .a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice",
                "#corePriceDisplay_desktop_feature_div .a-offscreen",
                ".priceToPay .a-offscreen"
            ]

            for selector in selectors:
                try:
                    locator = page.locator(selector)
                    if locator.count() > 0:
                        price_text = locator.first.text_content(timeout=5000)
                        if price_text:
                            price = ''.join(filter(str.isdigit, price_text))
                            if price:
                                browser.close()
                                return int(price)
                except:
                    continue

            print("❌ Price not found for:", url)
            page.screenshot(path="debug.png")  # debug

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
            print("❌ Telegram not configured")
            return

        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }

        response = requests.post(url, data=data)

        print("📱 Telegram response:", response.text)

    except Exception as e:
        print("❌ Telegram failed:", e)

# =========================
# 🚀 MAIN
# =========================

def main():
    report = f"📊 Price Check ({datetime.now()})\n\n"

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