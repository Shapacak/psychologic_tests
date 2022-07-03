import time

import requests
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pprint import pprint

chromedriver_path = 'D:\\Python\\PyCharms\\aiogram_learn\\chromedriver\\chromedriver.exe'
webdriver = webdriver.Chrome(executable_path=chromedriver_path)


class SiteTests:
    base_url = 'https://testometrika.com/'
    url = 'https://testometrika.com/tests/?PAGEN_1='
    current_page = 1
    current_cursor_tests = 0
    current_tests_list = []
    current_test = None

    @staticmethod
    def start():
        response = SiteTests.get_response()
        if response:
            SiteTests.create_tests_list(response)

    @staticmethod
    def get_response():
        response = requests.get(SiteTests.url + str(SiteTests.current_page))
        if response.status_code != 200:
            return None
        else:
            return response.text

    @staticmethod
    def create_tests_list(response):
        if len(SiteTests.current_tests_list) > 50:
            SiteTests.current_tests_list = []
            SiteTests.current_cursor_tests = 0
        soup = BS(response, 'lxml')
        divs = soup.find('div', class_='container').\
            find('div', class_='test-list__wrap').find_all('div',class_='col-xs-12')
        for i in range(len(divs)):
            btn = InlineKeyboardButton(text=divs[i].find('span', class_='test-list__test__title').text, callback_data=f'test {i}')
            link = SiteTests.base_url + divs[i].find('a').attrs['href']
            SiteTests.current_tests_list.append([link, btn])

    @staticmethod
    def loading_next_tests():
        SiteTests.current_page += 1
        response = SiteTests.get_response()
        SiteTests.create_tests_list(response)

    @staticmethod
    def loading_previous_tests():
        SiteTests.current_page -= 1
        response = SiteTests.get_response()
        SiteTests.create_tests_list(response)

    @staticmethod
    def display_tests():
        if SiteTests.current_tests_list:
            markup = InlineKeyboardMarkup()
            for i in range(SiteTests.current_cursor_tests, SiteTests.current_cursor_tests+5):
                markup.row(SiteTests.current_tests_list[i][1])
            return markup

    @staticmethod
    def next_tests():
        if SiteTests.current_cursor_tests+5 >= len(SiteTests.current_tests_list):
            SiteTests.loading_next_tests()
        SiteTests.current_cursor_tests += 5

    @staticmethod
    def previous_tests():
        if SiteTests.current_cursor_tests-5 >= 0:
            SiteTests.current_cursor_tests -= 5
        elif SiteTests.current_cursor_tests-5 < 0 & SiteTests.current_page <= 2:
            SiteTests.current_cursor_tests = 0
        elif SiteTests.current_cursor_tests-5 < 0 & SiteTests.current_page > 2:
            SiteTests.loading_previous_tests()

    @staticmethod
    def select_test(idx):
        webdriver.get(SiteTests.current_tests_list[idx][0])
        SiteTests.current_test = Test(webdriver)

    @staticmethod
    def get_question():
        return SiteTests.current_test.get_question()

    @staticmethod
    def select_answer(idx):
        SiteTests.current_test.select_answer(idx)


class Test:
    def __init__(self, webdriver_page):
        self.page = webdriver_page
        self.current_count = 0
        self.count_questions = 0
        self.current_div = None
        self.li_list = None
        self.start()
        self.get_count_questions()

    def start(self):
        try:
            WebDriverWait(self.page, 1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.ts__btn-bar>a'))).click()
        except Exception:
            print('Не получилось братан')

    def get_count_questions(self):
        if not self.current_div:
            self.set_current_div()
            self.count_questions = int(self.current_div.find_element(By.TAG_NAME, 'h3').text.split('/')[1])

    def set_current_div(self):
        try:
            self.current_div = WebDriverWait(self.page, 1).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ts__background-color>section>div')))
        except Exception:
            print('Div не получается найти')

    def get_question(self):
        if self.current_count == self.count_questions:
            return self.get_results()

        print(self.current_count, self.count_questions)

        markup = InlineKeyboardMarkup()
        title = self.current_div.find_element(By.TAG_NAME, 'h4').text
        self.li_list = self.current_div.find_element(By.CSS_SELECTOR, 'ul.ts__answer-list').\
            find_elements(By.CSS_SELECTOR, 'li.ts__answer-li')
        for i in range(len(self.li_list)):
            markup.row(InlineKeyboardButton(text=self.li_list[i].find_element(By.TAG_NAME, 'span').text,
                                            callback_data=f'select {i}'))
        self.current_count += 1
        return {'title':title, 'markup':markup}

    def get_results(self):
        result = Result(self.page)
        return {'title':result.get_result(), 'markup':InlineKeyboardMarkup().
            add(InlineKeyboardButton(text='К тестам', callback_data='return'))}

    def select_answer(self, idx):
        self.li_list[idx].find_element(By.TAG_NAME, 'label').click()
        if self.check_change_page():
            self.set_current_div()

    def check_change_page(self):
        if WebDriverWait(webdriver, 1).until(
                EC.invisibility_of_element(self.current_div.find_element(By.TAG_NAME, 'h4'))):
            return True
        else:
            print('check change page не работает')
            return False


class Result:
    def __init__(self, page):
        self.text = self.preparation_result(page)

    def preparation_result(self, page):
        try:
            div = WebDriverWait(page, 2).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,
                                                'div.result__body>div>div>div>div.result__description')))
        except Exception:
            print('Результаты не получилось получить)')
            div = None

        divs = div.find_elements(By.CSS_SELECTOR, 'div.result-stenayn')

        if len(divs[0].find_elements(By.CSS_SELECTOR,'div.result__stenayn-text-card')) == 0:
            return self.for_simple_div(divs)
        else:
            return self.for_text_card(divs)

    def for_text_card(self, divs):
        res = ''
        for div in divs:
            res += div.find_element(By.CSS_SELECTOR, 'div.result__stenayn-text-card').text
        return res

    def for_simple_div(self, divs):
        res = ''
        for div in divs:
            res += div.text
        return res

    def get_result(self):
        return self.text
