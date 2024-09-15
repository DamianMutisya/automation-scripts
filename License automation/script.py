import csv
import datetime
import smtplib
from email.mime.text import MIMEText
import schedule
import time

# Define the email settings
email_sender = 'your_email@example.com'  # Replace with your email
email_recipient = 'recipient@example.com'  # Replace with recipient's email
email_subject = 'Certificate Expiration Reminder'
smtp_server = 'your_smtp_server.com'  # Replace with your SMTP server
smtp_port = 465  # Use 465 for SSL
smtp_username = 'your_email@example.com'  # Replace with your email
smtp_password = 'your_email_password'  # Replace with your email password

# Function to send email
smtp_port = 465  # Use 465 for SSL
smtp_username = 'your_email@example.com'  # Replace with your email
smtp_password = 'your_email_password'  # Replace with your email password

# Function to send email
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = email_sender
    msg['To'] = email_recipient
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
            smtp.login(smtp_username, smtp_password)
            smtp.send_message(msg)
        print("Email sent successfully")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

# Function to check the certificates and send reminders
def check_certificates():
    print("Starting certificate check...")
    certificates = []
    try:
        with open('company_documents.csv', 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                certificates.append({
                    'Document': row['Document'],
                    'Company': row['Company'],
                    'Registration Date': datetime.datetime.strptime(row['Registration Date'], '%d/%m/%Y').date(),
                    'Deadline Date': datetime.datetime.strptime(row['Deadline Date'], '%d/%m/%Y').date()
                })
    except FileNotFoundError:
        print("Error: 'company_documents.csv' file not found.")
        return

    for cert in certificates:
        expiration_date = cert['Deadline Date']
        days_left = (expiration_date - datetime.date.today()).days
        if days_left == 0:
            body = f"Alert: The {cert['Document']} for {cert['Company']} has expired today ({expiration_date.strftime('%Y-%m-%d')}). Please renew it immediately."
            send_email(email_subject, body)
        elif days_left < 0:
            body = f"Alert: The {cert['Document']} for {cert['Company']} expired on {expiration_date.strftime('%Y-%m-%d')}. Please renew it as soon as possible."
            send_email(email_subject, body)
        elif days_left <= 15:
            body = f"Warning: The {cert['Document']} for {cert['Company']} is almost expiring in {days_left} days on {expiration_date.strftime('%Y-%m-%d')}. Please take action."
            send_email(email_subject, body)
        elif days_left <= 30:
            body = f"Reminder: The {cert['Document']} for {cert['Company']} is expiring in {days_left} days on {expiration_date.strftime('%Y-%m-%d')}."
            send_email(email_subject, body)

    print("Certificate check completed successfully.")

# Schedule the task to run at 13:40
schedule.every().day.at("13:40").do(check_certificates)

print("Script started. Waiting for scheduled time...")

# Keep the script running
while True:
    schedule.run_pending()
    time.sleep(1)