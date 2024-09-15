from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
import os
import csv

# Tender URL
TENDER_URL = "https://tenders.go.ke/tenders"


# Email configuration
SMTP_SERVER = "your_smtp_server.com"  # Replace with your SMTP server
SMTP_PORT = 465  # SSL
SENDER_EMAIL = "your_email@example.com"  # Replace with your email
SENDER_PASSWORD = "your_email_password"  # Replace with your email password
RECIPIENT_EMAIL = "recipient@example.com"  # Replace with recipient's email

# File to store previously scraped tenders
TENDER_LOG_FILE = "tenders_log.csv"

def parse_closing_date(closing_date_text):
    try:
        if "Closes in" in closing_date_text:
            parts = closing_date_text.split()
            if "day" in closing_date_text:
                days_remaining = 1 if parts[2] == "a" else int(parts[2])
            elif "month" in closing_date_text:
                days_remaining = int(parts[2]) * 30  # Approximating a month to 30 days
            else:
                days_remaining = int(parts[2])
            
            closing_date = datetime.now() + timedelta(days=days_remaining)
        else:
            closing_date = datetime.strptime(closing_date_text, '%d-%m-%Y')
    except (ValueError, IndexError) as e:
        print(f"Error parsing closing date: {closing_date_text} - {e}")
        return None
    return closing_date

def scrape_tenders():
    print("Scraping tenders...")

    # Setup WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    driver_service = Service(executable_path='D:/Desktop/tenders script/New folder/chromedriver-win64/chromedriver.exe')  # Update path
    driver = webdriver.Chrome(service=driver_service, options=chrome_options)
    
    driver.get(TENDER_URL)
    time.sleep(5)  # Wait for the page to load

    tenders = []
    while True:
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table')
        
        if table:
            for row in table.find('tbody').find_all('tr'):
                cells = row.find_all('td')
                if len(cells) >= 8:
                    tender_id = cells[0].text.strip()
                    title = cells[1].text.strip()
                    organization = cells[2].text.strip()
                    category = cells[4].text.strip()
                    status = cells[5].text.strip()
                    closing_date_text = cells[6].text.strip()

                    closing_date = parse_closing_date(closing_date_text)
                    if closing_date is None:
                        continue

                    posted_date = datetime.now().strftime('%d-%m-%Y')

                    tenders.append({
                        'id': tender_id,
                        'title': title,
                        'organization': organization,
                        'category': category,
                        'status': status,
                        'closing_date': closing_date.strftime('%d-%m-%Y'),
                        'posted_date': posted_date
                    })
        
        try:
            # Find the "Next" button and click it
            next_button = driver.find_element(By.XPATH, '//li[@class="v-pagination__next"]//button')
            if 'v-btn--disabled' in next_button.get_attribute('class'):
                break  # Exit loop if the "Next" button is disabled
            next_button.click()
            time.sleep(5)  # Wait for the next page to load
        except Exception as e:
            print(f"Error navigating pages: {e}")
            break

    driver.quit()
    print(f"Scraped {len(tenders)} tenders")
    return tenders

def save_tenders_to_log(tenders):
    file_exists = os.path.isfile(TENDER_LOG_FILE)
    with open(TENDER_LOG_FILE, 'a', newline='') as csvfile:
        fieldnames = ['id', 'title', 'organization', 'category', 'status', 'closing_date', 'posted_date']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        for tender in tenders:
            writer.writerow(tender)

def load_previous_tenders():
    previous_tenders = []
    if os.path.isfile(TENDER_LOG_FILE):
        with open(TENDER_LOG_FILE, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                previous_tenders.append(row)
    return previous_tenders

def filter_new_tenders(tenders, previous_tenders):
    new_tenders = []
    previous_ids = {t['id'] for t in previous_tenders}

    for tender in tenders:
        if tender['id'] not in previous_ids:
            new_tenders.append(tender)

    return new_tenders

def send_email_with_csv(tenders, csv_file):
    print("Preparing email...")

    subject = "Newly Posted Tenders"
    body = "Attached is the CSV file containing the new tenders posted today."

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with open(csv_file, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(csv_file)}")
    msg.attach(part)

    print("Sending email with CSV...")
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    print("Starting script to scrape and send new tenders")
    tenders = scrape_tenders()
    if tenders:
        previous_tenders = load_previous_tenders()
        new_tenders = filter_new_tenders(tenders, previous_tenders)

        if new_tenders:
            csv_file = "new_tenders.csv"
            with open(csv_file, 'w', newline='') as csvfile:
                fieldnames = ['id', 'title', 'organization', 'category', 'status', 'closing_date', 'posted_date']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(new_tenders)

            send_email_with_csv(new_tenders, csv_file)
            save_tenders_to_log(new_tenders)
            print(f"Email sent with {len(new_tenders)} new tenders posted today.")
        else:
            print("No new tenders posted today.")
    else:
        print("No tenders found.")

if __name__ == "__main__":
    main()
