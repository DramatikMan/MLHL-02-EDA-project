import telegram
import os
import sys

from app.loggers import LOG_PATH


CHAT_ID = -680917160


def main() -> None:
    bot = telegram.Bot(token=os.environ['TG_TOKEN'])

    try:
        caption = 'Scraping succeeded.' if sys.argv[1] == '0' \
            else 'Scraping failed.'
        document = open(LOG_PATH)
    except Exception:
        bot.send_message(
            chat_id=CHAT_ID,
            text='Failed to get scraping status and/or logs.'
        )
    else:
        bot.send_document(
            chat_id=CHAT_ID,
            caption=caption,
            document=document
        )
        os.truncate(LOG_PATH, length=0)
        document.close()


if __name__ == '__main__':
    main()
