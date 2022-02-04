import os


CHROMEDRIVER_BIN_PATH = os.environ.get(
    'CHROMEDRIVER_BIN_PATH',
    '/usr/bin/chromedriver'
)

# на сколько дней первая дата вылета позже даты сбора данных
DATES_TO_SKIP = 8
# сколько последовательных дат парсится для каждого города
CONSECUTIVE_DATES_TO_PARSE = 31
