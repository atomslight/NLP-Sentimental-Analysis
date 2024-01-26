import os
import base64
from selenium import webdriver
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from google.auth.transport.requests import Request
from textblob import TextBlob
import re
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set up the Gmail API credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail_api():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json')

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

def list_messages(service, user_id='me', label_ids=['INBOX'], max_results=5):
    results = service.users().messages().list(userId=user_id, labelIds=label_ids, maxResults=max_results).execute()
    messages = results.get('messages', [])
    return messages

def get_message(service, user_id='me', message_id=''):
    message = service.users().messages().get(userId=user_id, id=message_id).execute()
    return message

def extract_content(message):
    subject = ''
    sender = ''
    body = ''

    headers = message['payload']['headers']
    for header in headers:
        if header['name'] == 'Subject':
            subject = header['value']
        elif header['name'] == 'From':
            sender = header['value']

    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        for part in parts:
            if 'body' in part:
                body_data = part['body']['data']
                body += base64.urlsafe_b64decode(body_data).decode('utf-8')

    return subject, sender, body

def extract_message_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    for a in soup.find_all('a', href=True):
        if 'http' in a['href']:
            a.extract()

    message_content = soup.get_text(separator='\n').strip()
    message_content = re.sub(r'http[s]?://\S+', '', message_content)

    return message_content

def clean_msg(retrieved_text):
    # Use BeautifulSoup to clean the text
    soup = BeautifulSoup(retrieved_text, 'html.parser')
    w_cleaned_text = soup.get_text()
    # Return the cleaned text for saving to file
    return w_cleaned_text

def clean_text(input_text):
    cleaned_text = re.sub(r'\s+', ' ', input_text).strip()
    return cleaned_text

def analyze_sentiment(text):
    analysis = TextBlob(text)
    return analysis.sentiment.polarity

def save_to_file(messages, output_folder, current_datetime, source):
    # Save the extracted text with sentimental score to a txt file
    file_name = f"{output_folder}/{source.lower()}/output_{source.lower()}_{current_datetime}.txt"

    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(f"=== {source} Sentiment Analysis ===\n")
        file.write(f"Date and Time: {current_datetime}\n\n")

        for i, message in enumerate(messages, start=1):
            cleaned_msg = clean_msg(message)
            sentiment_score = analyze_sentiment(cleaned_msg)
            sentiment_label = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"

            file.write(f"Message {i}:\n{cleaned_msg}\nSentiment: {sentiment_label} (Score: {sentiment_score:.2f})\n{'=' * 30}\n")

def visualize_combined_sentiment_graph(messages, sentiment_data_list, source):
    labels = ['Positive', 'Neutral', 'Negative']
    width = 0.2  # Width of each bar

    for i, sentiment_data in enumerate(sentiment_data_list):
        # Calculate the position for each group of bars dynamically based on sentiment scores
        positions = np.arange(len(labels)) + i * width

        plt.bar(positions, [sentiment_data['positive'], sentiment_data['neutral'], sentiment_data['negative']],
                width=width, label=f"Message {i + 1}")

    plt.xticks(np.arange(len(labels)) + ((len(sentiment_data_list) - 1) * width) / 2, labels)
    plt.title(f'Combined Sentiment Analysis for All {source} Messages')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.legend()

    # Save the graph
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    graph_filename = f"output/{source.lower()}/sentiment_analysis_{current_datetime}.png"
    plt.savefig(graph_filename)

    plt.show()

def extract_message(wait, selector):
    chat = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
    chat.click()
    msg = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#main > div._3B19s > div > div._5kRIK > div.n5hs2j7m.oq31bsqd.gx1rr48f.qh5tioqs'))).text
    return msg

def w_app_extract():
    # Create a new instance of the Chrome driver
    driver = webdriver.Chrome()

    # Open WhatsApp Web
    driver.get('https://web.whatsapp.com/')
    driver.maximize_window()
    # Allow some time for the user to scan the QR code
    time.sleep(10)

    # Perform any additional actions or automation as needed
    wait = WebDriverWait(driver, 180)

    # Extract messages as before
    first_chat_msg = extract_message(wait, '#pane-side > div:nth-child(3) > div > div > div:nth-child(1) > div > div > div > div._8nE1Y')
    sec_chat_msg = extract_message(wait, 'div:nth-child(3) > div > div > div:nth-child(11)')
    third_chat_msg = extract_message(wait, '#pane-side > div:nth-child(3) > div > div > div:nth-child(10) > div > div > div > div._8nE1Y')
    fourth_chat_msg = extract_message(wait, '#pane-side > div:nth-child(3) > div > div > div:nth-child(9)')

    # Print the raw extracted text
    print("\nRaw Extracted Text:")
    print("1", first_chat_msg)
    print("2", sec_chat_msg)
    print("3", third_chat_msg)
    print("4", fourth_chat_msg)

    # Visualize combined sentiment distribution for all messages
    visualize_combined_sentiment_graph_whatsapp([first_chat_msg, sec_chat_msg, third_chat_msg, fourth_chat_msg])

    driver.quit()
def visualize_combined_sentiment_graph_whatsapp(messages):
    labels = ['Positive', 'Neutral', 'Negative']
    width = 0.2  # Width of each bar

    for i, message in enumerate(messages):
        sentiment_data = {'positive': 0, 'neutral': 0, 'negative': 0}

        cleaned_msg = clean_msg(message)
        sentiment_score = analyze_sentiment(cleaned_msg)

        if sentiment_score > 0:
            sentiment_data['positive'] += sentiment_score
        elif sentiment_score < 0:
            sentiment_data['negative'] += sentiment_score
        else:
            sentiment_data['neutral'] += sentiment_score

        positions = np.arange(len(labels)) + i * width

        plt.bar(positions, [sentiment_data['positive'], sentiment_data['neutral'], sentiment_data['negative']],
                width=width, label=f"Message {i + 1}")

    plt.xticks(np.arange(len(labels)) + ((len(messages) - 1) * width) / 2, labels)
    plt.title('Combined Sentiment Analysis for WhatsApp Messages')
    plt.xlabel('Sentiment')
    plt.ylabel('Count')
    plt.legend()

    # Save the graph
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    graph_filename = f"output/WhatsApp/sentiment_analysis_{current_datetime}.png"
    plt.savefig(graph_filename)

    plt.show()
    save_to_file(messages, "output", current_datetime,"WhatsApp")

if __name__ == '__main__':
    creds = authenticate_gmail_api()
    service = build('gmail', 'v1', credentials=creds)
    counter = 1  # Initialize a counter variable

    # Process Gmail messages
    messages = list_messages(service)
    sentiment_data_list_gmail = []
    gmail_output_messages = []  # Create a list to store Gmail messages for saving to file
    for message in messages:
        message_id = message['id']
        gmail_message = get_message(service, message_id=message_id)

        subject, sender, body = extract_content(gmail_message)
        message_content = extract_message_content(body)
        cleaned_message_content = clean_text(message_content)

        sentiment_data = {'positive': 0, 'neutral': 0, 'negative': 0}

        sentiment_score = analyze_sentiment(cleaned_message_content)
        # Extract and clean the message content
        message_content = extract_message_content(body)
        cleaned_message_content = clean_text(message_content)

        if sentiment_score > 0:
            sentiment_data['positive'] += sentiment_score
        elif sentiment_score < 0:
            sentiment_data['negative'] += sentiment_score
        else:
            sentiment_data['neutral'] += sentiment_score
        # Perform sentiment analysis
        sentiment_score = analyze_sentiment(cleaned_message_content)
        sentiment_label = "Positive" if sentiment_score > 0 else "Negative" if sentiment_score < 0 else "Neutral"

        sentiment_data_list_gmail.append(sentiment_data)
        # Append the message details to the list
        gmail_output_messages.append(
            f"{counter}. Subject: {subject}\nSender: {sender}\nMessage Content:\n\n{cleaned_message_content}\n{'=' * 30}\nSentiment: {sentiment_label} (Score: {sentiment_score:.2f})\n")

        counter += 1  # Increment the counter for the next message

    # Visualize combined sentiment distribution for all Gmail messages
    visualize_combined_sentiment_graph(gmail_output_messages, sentiment_data_list_gmail, "Gmail")
    # Save the Gmail output messages to a file
    save_to_file(gmail_output_messages, "output", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), "Gmail")

    w_app_extract()
