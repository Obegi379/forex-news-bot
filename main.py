import os
import requests
import xml.etree.ElementTree as ET
from telegram import Bot
from telegram.error import TelegramError
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_rss_feed(rss_url):
    """Fetch and parse the RSS feed"""
    try:
        logger.info("Fetching RSS feed from Forex Factory...")
        response = requests.get(rss_url, timeout=10)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        logger.info("RSS feed fetched successfully")
        return root
    except requests.RequestException as e:
        logger.error(f"Error fetching RSS feed: {e}")
        raise
    except ET.ParseError as e:
        logger.error(f"Error parsing RSS feed: {e}")
        raise

def extract_top_event(root):
    """Extract the top event from the RSS feed"""
    try:
        event = root.find('./channel/item')
        if event is None:
            logger.warning("No events found in RSS feed")
            return None
        
        title = event.find('title')
        description = event.find('description')
        pub_date = event.find('pubDate')
        
        if title is None or description is None or pub_date is None:
            logger.warning("Missing required fields in event")
            return None
        
        return {
            'title': title.text,
            'description': description.text,
            'pub_date': pub_date.text
        }
    except Exception as e:
        logger.error(f"Error extracting event: {e}")
        return None

def send_to_telegram(bot_token, chat_id, event):
    """Send the event to Telegram"""
    try:
        if not event:
            logger.warning("No event to send")
            return False
        
        bot = Bot(token=bot_token)
        message = f"*{event['title']}*\n\n{event['description']}\n\n📅 {event['pub_date']}"
        
        logger.info(f"Sending message to Telegram chat {chat_id}...")
        bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
        logger.info("Message sent successfully!")
        return True
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return False

def main():
    """Main function to orchestrate the workflow"""
    try:
        # Get environment variables
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
        rss_url = "https://www.forexfactory.com/feeds/economic-calendar.rss"
        
        # Validate environment variables
        if not bot_token or not chat_id:
            logger.error("Missing required environment variables: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
            return False
        
        # Fetch and process
        root = fetch_rss_feed(rss_url)
        event = extract_top_event(root)
        success = send_to_telegram(bot_token, chat_id, event)
        
        return success
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)