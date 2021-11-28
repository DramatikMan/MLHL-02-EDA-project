import logging
import os
import sys


LOG_PATH = f'{os.environ["PWD"]}/runner.log'


# main runner script events logging
main_task_log = logging.getLogger('main_task_log')
main_task_log.setLevel(logging.INFO)
main_task_log_formatter = logging.Formatter(
    fmt='[%(levelname)s]:[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# stdout output handler
main_task_log_stdout_handler = logging.StreamHandler(stream=sys.stdout)
main_task_log_stdout_handler.setFormatter(fmt=main_task_log_formatter)
main_task_log.addHandler(hdlr=main_task_log_stdout_handler)
# file output handler
# main_task_log_file_handler = logging.FileHandler(filename=LOG_PATH)
# main_task_log_file_handler.setFormatter(fmt=main_task_log_formatter)
# main_task_log.addHandler(hdlr=main_task_log_file_handler)

# scraper runs logging
scraping_log = logging.getLogger('scraping_log')
scraping_log.setLevel(logging.INFO)
scraping_log_formatter = logging.Formatter(
    fmt='[%(levelname)s]:[%(asctime)s] [%(city)s @ %(date)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# stdout output handler
scraping_log_stdout_handler = logging.StreamHandler(stream=sys.stdout)
scraping_log_stdout_handler.setFormatter(fmt=scraping_log_formatter)
scraping_log.addHandler(hdlr=scraping_log_stdout_handler)
# file output handler
# scraping_log_file_handler = logging.FileHandler(filename=LOG_PATH)
# scraping_log_file_handler.setFormatter(fmt=scraping_log_formatter)
# scraping_log.addHandler(hdlr=scraping_log_file_handler)
