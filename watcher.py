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
        "url": "https://www.amazon.in/gp/product/B0CWLSP9FG/ref=ox_sc_act_title_1?smid=AJ6SIZC8YQDZX&psc=1",
        "target": 5500
    },
    {
        "name": "crucial nvme SSD 512GB",
        "url": "https://www.amazon.in/Crucial-Internal-Laptop-Desktop-Compatible/dp/B0GMPWGV88/ref=sr_1_6?crid=10VK5J9JRYTEG&dib=eyJ2IjoiMSJ9.KkkpK5xoP9DOBtuPNnePO33GifZozY3KAxRE2z8gYyyYkxGXcPWu3-tjLsAjk_BOp0IhvbkQI40JWsPCMx-nuZjU0_dJyqRtsG-pyBKvDuDk26TSaXkow5MQDufQ58d_bWqVQWXsKzwikRFT78XXGRJRzMZlCzo6k5tOVuNYxNSgJjjajQdpHlOUuY6Zsijv_eN8Cv0dm4bNw2lovjJi3KWJ7YWQfNj0WSB-tRhjfrc.sJM9y73M9rLyIDMqQbk3KcDxAcX5Ynh1aTWK0GTbW6s&dib_tag=se&keywords=nvme+ssd+512gb&qid=1776537146&sprefix=nvme+ssd+5%2Caps%2C386&sr=8-6",
        "target": 5500
    },
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
            time.sleep(3)

            selectors = [
                ".a-price .a-offscreen",
                "#priceblock_ourprice",
                "#priceblock_dealprice"
            ]

            for selector in selectors:
                try:
                    price_text = page.locator(selector).first.text_content(timeout=5000)
                    if price_text:
                        price = price_text.replace("₹", "").replace(",", "")
                        browser.close()
                        return int(float(price))
                except:
                    continue

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
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        requests.post(url, data=data)
    except Exception as e:
        print("❌ Telegram failed:", e)

# =========================
# 🚀 MAIN LOGIC
# =========================

def main():
    report = f"📊 Price Check ({datetime.now()})\n\n"

    for product in PRODUCTS:
        price = get_price(product["url"])

        if price:
            report += f"{product['name']}: ₹{price}\n"

            # Email ONLY if below target
            if price <= product["target"]:
                send_email(product, price)

        else:
            report += f"{product['name']}: ❌ Failed\n"

    # Telegram always sends full report
    send_telegram(report)

    print(report)

if __name__ == "__main__":
    main()