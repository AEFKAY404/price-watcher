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

def get_price():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    price_tag = soup.select_one(".a-price .a-offscreen")

    if price_tag:
        price_text = price_tag.get_text().strip()
       

        price = price_text.replace("₹", "").replace(",", "").strip()
        return int(float(price))  # <-- FIX HERE

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