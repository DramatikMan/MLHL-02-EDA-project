import telegram
import os
import sys

CHAT_ID = -680917160


def main() -> None:
    bot = telegram.Bot(token=os.environ['TG_TOKEN'])
    try:
        caption = 'Scraping succeeded.' if sys.argv[1] == '0' else 'Scraping failed.'
        bot.send_document(chat_id=CHAT_ID, caption=caption, document=open('runner.log'))
    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text='Failed to get scraping status and/or logs.')


if __name__ == '__main__':
    main()
