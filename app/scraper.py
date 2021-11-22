import time
from datetime import date

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class Scraper:
    __slots__ = 'destination', 'on_date', '__driver', '_HTML'
    __driver: WebDriver
    _HTML: str

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

    def __init__(self, destination: str, on_date: date) -> None:
        self.destination = destination

        if (month_num := on_date.month) < 10:
            month = f'0{str(month_num)}'
        else:
            month = str(month_num)

        if (day_num := on_date.day) < 10:
            day = f'0{str(day_num)}'
        else:
            day = str(day_num)

        self.on_date = f'{str(on_date.year)[-2:]}{month}{day}'

    def check_and_handle_captcha(self, cp: str) -> None:
        if self.__driver.find_elements(By.ID, 'px-captcha'):
            print(f'--- CAPTCHA encountered at checkpoint {cp} ---')

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

            print('--- CAPTCHA handled successfully ---')

    def check_and_handle_notification_prompt(self, cp: str) -> None:
        if self.__driver.find_elements(By.ID, 'price-alerts-modal'):
            print(
                '--- NOTIFICATION PROMPT '
                f'encountered at checkpoint {cp} ---'
            )
            self.__driver \
                .find_element(By.ID, 'price-alerts-modal') \
                .find_element(By.TAG_NAME, 'header') \
                .find_element(By.TAG_NAME, 'button') \
                .click()
            print('--- NOTIFICATION PROMPT handled successfully ---')

    def check_and_handle_covid_prompt(self, cp: str) -> None:
        if self.__driver.execute_script('''
            const collection = document.getElementsByClassName(
                'usabilla__overlay'
            );

            return (
                (collection.length > 0) &&
                (collection[0].style.display == 'block')
            );
        '''):
            print(f'--- COVID PROMPT encountered at checkpoint {cp} ---')
            self.__driver.switch_to.frame(
                self.__driver.execute_script('''
                    return document.querySelector(
                        'iframe[title="Usabilla Feedback Form"]'
                    );
                ''')
            )
            self.__driver.find_element(By.ID, 'close').click()
            self.__driver.switch_to.default_content()
            print('--- COVID PROMPT handled successfully ---')

    def check_and_handle_blockers(self, cp: str) -> None:
        self.check_and_handle_captcha(cp=cp)
        self.check_and_handle_notification_prompt(cp=cp)
        self.check_and_handle_covid_prompt(cp=cp)

    def get_HTML(self) -> None:
        URL = f'{self.BASE_URL}/{self.destination}/{self.on_date}'

        self.__driver.get(URL)
        time.sleep(2)
        self.check_and_handle_blockers(cp='1')

        # ждём, пока пропадёт индикатор продолжающейся загрузки
        while self.__driver.execute_script('''
            return document.querySelector(
                "div[class^='SummaryInfo_progressTextContainer']"
            );
        ''') is not None:
            time.sleep(10)

        self.check_and_handle_blockers(cp='2')

        # отключаем "комбинации авиакомпаний"
        self.__driver.execute_script('''
            return document.querySelector(
                'input[aria-label="Комбинации авиакомпаний"]'
            );
        ''').click()
        time.sleep(5)

        # переходим на в низ страницы
        self.__driver.execute_script(
            'window.scrollTo(0, document.body.scrollHeight);'
        )
        # кликаем на кнопку "Показать больше"
        self.__driver.execute_script('''
            const matches = [];
            document.querySelectorAll('button').forEach(
                e => e.textContent == 'Показать больше'
                ? matches.push(e)
                : null
            );

            return matches[0];
        ''').click()

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

        self._HTML: str = self.__driver.execute_script('''
            return document.querySelector(
                "div[class^='FlightsResults_dayViewItems']"
            );
        ''').get_attribute('innerHTML')

    def run(self) -> None:
        self.__driver: WebDriver = webdriver.Chrome(
            options=self.options,
            service=Service('/usr/bin/chromedriver')
        )

        try:
            self.get_HTML()
        finally:
            self.__driver.quit()

    @property
    def HTML(self) -> str:
        return self._HTML
