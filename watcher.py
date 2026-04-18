import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText

URL = "https://www.amazon.in/gp/product/B0CWLSP9FG/ref=ox_sc_act_title_1?smid=AJ6SIZC8YQDZX&psc=1"  # replace if needed
TARGET_PRICE = 5500

EMAIL = "akashreddy0506@gmail.com"
PASSWORD = "jpzglqjueorhluqt"
TO_EMAIL = "akashreddy0506@gmail.com"

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
    msg = MIMEText(f"🔥 Price dropped to ₹{price}!\n{URL}")
    msg["Subject"] = "Price Drop Alert"
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

def main():
    price = get_price()
    print("Current price:", price)

    if price and price <= TARGET_PRICE:
        send_email(price)

if __name__ == "__main__":
    main()