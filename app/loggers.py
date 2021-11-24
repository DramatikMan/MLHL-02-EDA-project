import logging
import sys

main_task_log = logging.getLogger('main_task_log')
main_task_log.setLevel(logging.INFO)
main_task_log_stream_handler = logging.StreamHandler(stream=sys.stdout)
main_task_log_stream_handler.setFormatter(fmt=logging.Formatter(
    fmt='[%(levelname)s]:[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
main_task_log.addHandler(hdlr=main_task_log_stream_handler)

scraping_log = logging.getLogger('scraping_log')
scraping_log.setLevel(logging.INFO)
scraping_stream_handler = logging.StreamHandler(stream=sys.stdout)
scraping_stream_handler.setFormatter(fmt=logging.Formatter(
    fmt='[%(levelname)s]:[%(asctime)s] [%(city)s]:[%(date)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
scraping_log.addHandler(hdlr=scraping_stream_handler)
