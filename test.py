import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

chromedriver_path = 'D:\\Python\\PyCharms\\aiogram_learn\\chromedriver\\chromedriver.exe'
url = 'https://testometrika.com/depression-and-stress/test-for-level-of-depression/'

webdriver = webdriver.Chrome(executable_path=chromedriver_path)
webdriver.get(url)


class Test:
    def __init__(self, webdriver_page):
        self.page = webdriver_page
        self.current_count = 0
        self.start()
        self.count_questions = self.get_count_questions()

    def start(self):
        time.sleep(0.5)
        self.page.find_element(By.CSS_SELECTOR, 'div.ts__start-page-wrapper'). \
            find_element(By.CSS_SELECTOR, 'div.ts__btn-bar>a').click()

    def get_count_questions(self):
        time.sleep(0.5)
        return int(self.page.find_element(By.CSS_SELECTOR, 'div.ts__background-color>section>div').\
                   find_element(By.TAG_NAME, 'h3').text.split('/')[1])

    def get_question(self):
        if self.current_count == self.count_questions:
            return self.get_results()
        print(self.current_count, self.count_questions)
        time.sleep(0.5)
        markup = InlineKeyboardMarkup()
        div = self.page.find_element(By.CSS_SELECTOR, 'div.ts__background-color>section>div')
        title = div.find_element(By.TAG_NAME, 'h4').text

        self.li_list = div.find_element(By.CSS_SELECTOR, 'ul.ts__answer-list').\
            find_elements(By.CSS_SELECTOR, 'li.ts__answer-li')
        for i in range(len(self.li_list)):
            markup.row(InlineKeyboardButton(text=self.li_list[i].find_element(By.TAG_NAME, 'span').text,
                                            callback_data=f'select {i}'))
        self.current_count += 1
        return {'title':title, 'markup':markup}

    def get_results(self):
        result = Result(self.page)
        return {'title':result.get_result(), 'markup':InlineKeyboardMarkup()}

    def select_answer(self, idx):
        self.li_list[idx].find_element(By.TAG_NAME, 'label').click()


class Result:
    def __init__(self, page):
        self.text = self.preparation_result(page)

    def preparation_result(self, page):
        time.sleep(1)
        divs = page.find_element(By.CSS_SELECTOR, 'div.result__body').\
            find_element(By.CSS_SELECTOR, 'div.result__description-wrap').\
            find_element(By.CSS_SELECTOR, 'div.result__description').\
            find_elements(By.CSS_SELECTOR, 'div.result-stenayn')

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
