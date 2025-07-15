from dotenv import load_dotenv
import os
from app import BusinessBot
load_dotenv()

#Start bot
def main():
    API_ID = os.getenv("API_ID")
    API_HASH = os.getenv("API_HASH")
    API_TOKEN = os.getenv("API_TOKEN")
    bot = BusinessBot(API_ID, API_HASH, API_TOKEN)
    bot.run()

if __name__ == '__main__':
    main()