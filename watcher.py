import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import os

# 🔗 Product URL
URL = "https://www.amazon.in/gp/product/B0CWLSP9FG/ref=ox_sc_act_title_1?smid=AJ6SIZC8YQDZX&psc=1"

# 🎯 Target price
TARGET_PRICE = 4000

# 🔐 Environment variables (Render)
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Accept-Language": "en-IN,en;q=0.9"
}

from playwright.sync_api import sync_playwright

def get_price():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(URL, timeout=60000)

            # wait for price to load
            page.wait_for_selector(".a-price", timeout=10000)

            price_text = page.locator(".a-price .a-offscreen").first.text_content()

            browser.close()

            if price_text:
                price = price_text.replace("₹", "").replace(",", "")
                return int(float(price))

    except Exception as e:
        print("❌ Playwright error:", e)

    return None

def send_email(price):
    try:
        msg = MIMEText(f"🔥 Price dropped to ₹{price}!\n{URL}")
        msg["Subject"] = "Price Drop Alert"
        msg["From"] = EMAIL
        msg["To"] = TO_EMAIL

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)

        print("✅ Email sent!")

    except Exception as e:
        print("❌ Email failed:", e)


def main():
    price = get_price()
    print(f"{datetime.now()} - Current price: {price}")

    if price and price <= TARGET_PRICE:
        send_email(price)


if __name__ == "__main__":
    main()