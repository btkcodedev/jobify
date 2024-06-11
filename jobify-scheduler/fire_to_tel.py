# scrap_to_firestore_telegram.py

import requests
from bs4 import BeautifulSoup
from google.cloud import firestore
from telegram import Bot
import logging
import os
from dotenv import load_dotenv

load_dotenv()
# Setup logging
logging.basicConfig(level=logging.INFO)

# Firestore setup
db = firestore.Client()

# Telegram bot setup
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = Bot(token=TELEGRAM_TOKEN)

# Scraping function
def scrape_website(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Assuming we're scraping articles with 'article' tag and a 'data-id' attribute
    articles = soup.find_all('article')
    scraped_data = []
    for article in articles:
        data_id = article.get('data-id')
        title = article.find('h2').text.strip()
        content = article.find('p').text.strip()
        scraped_data.append({
            'id': data_id,
            'title': title,
            'content': content
        })
    return scraped_data

# Firestore interaction
def add_to_firestore(data):
    collection_ref = db.collection('articles')
    for item in data:
        doc_ref = collection_ref.document(item['id'])
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set(item)
            logging.info(f"Added new article with ID: {item['id']}")
            notify_telegram(item)

# Telegram notification
def notify_telegram(item):
    message = f"New article added:\n\nTitle: {item['title']}\nContent: {item['content']}"
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    logging.info(f"Sent notification for article ID: {item['id']}")

if __name__ == '__main__':
    URL = 'https://example.com/articles'
    scraped_data = scrape_website(URL)
    add_to_firestore(scraped_data)
