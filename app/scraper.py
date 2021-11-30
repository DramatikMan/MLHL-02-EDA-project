import logging
import signal
import time
from datetime import date
from typing import Any, Optional

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .loggers import scraping_log


class Scraper:
    __slots__ = (
        '_destination', '_dest_string',
        '_on_date', '_on_date_string',
        '_HTML',
        '__driver',
        '__log'
    )

    options = Options()
    options.headless = True
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-web-security')
    options.add_argument('--no-sandbox')
    options.add_argument('--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"')  # noqa: E501
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)

    BASE_URL = 'https://www.skyscanner.ru/transport/flights/mosc'

    def __init__(self, destination: tuple[str, str], on_date: date) -> None:
        name, airport = destination
        self._destination = name
        self._dest_string = airport.lower()
        self._on_date = on_date.isoformat()

        if (month_num := on_date.month) < 10:
            month = f'0{str(month_num)}'
        else:
            month = str(month_num)

        if (day_num := on_date.day) < 10:
            day = f'0{str(day_num)}'
        else:
            day = str(day_num)

        self._on_date_string = f'{str(on_date.year)[-2:]}{month}{day}'

    @property
    def HTML(self) -> Optional[str]:
        return self._HTML

    @staticmethod
    def captcha_timeout_handler(signum: int, frame: Any) -> None:
        raise TimeoutError('Timed out while handling CAPTCHA.')

    def check_and_handle_captcha(self, checkpoint: str) -> None:
        if self.__driver.find_elements(By.ID, 'px-captcha'):
            self.__log.info(f'CAPTCHA encountered at checkpoint {checkpoint}.')
            signal.alarm(60)

            while self.__driver.find_elements(
                By.CLASS_NAME,
                'px-loader-wrapper'
            ):
                time.sleep(2)

            while self.__driver.find_elements(By.ID, 'px-captcha'):
                captcha: WebElement = self.__driver.find_element(
                    By.ID,
                    'px-captcha'
                )
                ActionChains(self.__driver) \
                    .move_to_element(captcha) \
                    .click_and_hold(captcha) \
                    .pause(10) \
                    .release() \
                    .perform()

                time.sleep(10)

            signal.alarm(0)
            self.__log.info('CAPTCHA handled successfully.')

    def check_and_handle_notification_prompt(self, checkpoint: str) -> None:
        if self.__driver.find_elements(By.ID, 'price-alerts-modal'):
            self.__log.info(
                f'NOTIFICATION PROMPT encountered at checkpoint {checkpoint}.'
            )
            self.__driver \
                .find_element(By.ID, 'price-alerts-modal') \
                .find_element(By.TAG_NAME, 'header') \
                .find_element(By.TAG_NAME, 'button') \
                .click()
            self.__log.info('NOTIFICATION PROMPT handled successfully.')

    def check_and_handle_covid_prompt(self, checkpoint: str) -> None:
        if self.__driver.execute_script('''
            const collection = document.getElementsByClassName(
                'usabilla__overlay'
            );

            return (
                (collection.length > 0) &&
                (collection[0].style.display == 'block')
            );
        '''):
            self.__log.info(
                f'COVID PROMPT encountered at checkpoint {checkpoint}.'
            )
            self.__driver.switch_to.frame(
                self.__driver.execute_script('''
                    return document.querySelector(
                        'iframe[title="Usabilla Feedback Form"]'
                    );
                ''')
            )
            self.__driver.find_element(By.ID, 'close').click()
            self.__driver.switch_to.default_content()
            self.__log.info('COVID PROMPT handled successfully.')

    def check_and_handle_blockers(self, checkpoint: str) -> None:
        self.check_and_handle_captcha(checkpoint=checkpoint)
        self.check_and_handle_notification_prompt(checkpoint=checkpoint)
        self.check_and_handle_covid_prompt(checkpoint=checkpoint)

    def get_HTML(self) -> None:
        URL = f'{self.BASE_URL}/{self._dest_string}/{self._on_date_string}'

        self.__driver.get(URL)
        time.sleep(2)
        self.check_and_handle_blockers(checkpoint='1')

        # ждём, пока пропадёт индикатор продолжающейся загрузки
        while self.__driver.execute_script('''
            return document.querySelector(
                "div[class^='SummaryInfo_progressTextContainer']"
            );
        ''') is not None:
            time.sleep(10)

        self.check_and_handle_blockers(checkpoint='2')

        # отключаем "комбинации авиакомпаний"
        self.__driver.execute_script('''
            return document.querySelector(
                'input[aria-label="Комбинации авиакомпаний"]'
            );
        ''').click()
        time.sleep(5)

        # переходим в низ страницы
        self.__driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);'
        )

        self.check_and_handle_blockers(checkpoint='3')

        if self.__driver.execute_script('''
            return document.querySelector(
                "div[class^='FlightsResults_dayViewItems']"
            );
        ''') is None:
            self._HTML: Optional[str] = None
            self.__log.info('No flights found.')
        else:
            self.check_and_handle_blockers(checkpoint='4')

            # кликаем на кнопку "Показать больше", если она есть
            if (show_more_button := self.__driver.execute_script('''
                const matches = [];
                document.querySelectorAll('button').forEach(
                    e => e.textContent == 'Показать больше'
                    ? matches.push(e)
                    : null
                );

                return matches[0];
            ''')) is not None:
                show_more_button.click()

            self.check_and_handle_blockers(checkpoint='5')
            time.sleep(2)

            # прокручиваемся вниз, пока не будут видны все результаты
            element_count = 0

            while (current_count := self.__driver.execute_script('''
                return document.querySelector(
                    "div[class^='FlightsResults_dayViewItems']"
                ).childElementCount;
            ''')) > element_count:
                element_count = current_count
                self.__driver.execute_script(
                    'window.scrollTo(0, document.body.scrollHeight);'
                )
                time.sleep(2)

            self._HTML = self.__driver.execute_script('''
                return document.querySelector(
                    "div[class^='FlightsResults_dayViewItems']"
                );
            ''').get_attribute('innerHTML')

    def run(self) -> None:
        self.__log = logging.LoggerAdapter(
            scraping_log,
            extra=dict(city=self._destination, date=self._on_date)
        )

        self.__log.info('--- Starting scraper run.')
        attempt_count, try_limit = 0, 5
        signal.signal(signal.SIGALRM, self.captcha_timeout_handler)

        while attempt_count < try_limit:
            attempt_count += 1

            self.__driver: WebDriver = webdriver.Chrome(
                options=self.options,
                service=Service('/usr/bin/chromedriver')
            )

            try:
                self.get_HTML()
            except Exception as ex:
                self.__log.error('Failed at attempt 'f'#{attempt_count}.')
                self.__log.error(str(ex))

                if attempt_count < try_limit:
                    self.__log.info('Retrying...')
            else:
                break
            finally:
                self.__driver.quit()

        self.__log.info('--- Scraper run done.')
