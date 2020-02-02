from selenium import webdriver
import re
import json
import time
title_list = []
url_list = []


options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        'javascript': 2  # 2即为禁用的意思
    }
}
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # 无头参数
options.add_argument('--disable-gpu')
options.add_experimental_option('prefs', prefs)
chrome = webdriver.Chrome(options=options)
chrome.implicitly_wait(10)
page = 1
book_title_list = []
book_id_list = []
while page <= 134:
    while len(book_title_list) != int(10) or len(book_id_list) != int(10):
        chrome.get('https://lib-nuanxin.wqxuetang.com/search?p={page}&t=1&year=2019&_t=1580470943872'.format(page=page))
        time.sleep(5)
        book_id_list = chrome.find_elements_by_css_selector('.item-cover img')
        book_title_list = chrome.find_elements_by_css_selector('h3')
        del book_title_list[-2:]
        book_title_list_length = len(book_title_list);book_id_list_length = len(book_id_list)
        print(book_title_list_length)
        print(book_id_list_length)
    for t, i in zip(book_title_list, book_id_list):
        title_list.append(t.get_attribute('title'))
        book_id = re.sub(r'https.*/', "", i.get_attribute('src'))
        book_ids = re.search(r'\d*', book_id)
        book_urls = 'https://lib-nuanxin.wqxuetang.com/read/pdf/{book_ids}'.format(book_ids=book_ids.group())
        url_list.append(book_urls)
    book_id_list = []; book_title_list = []
    print(url_list)
    print(title_list)
    print(len(title_list))
    print(len(url_list))
    print('the {num}th page'.format(num=page))
    page += 1
chrome.get('https://lib-nuanxin.wqxuetang.com/search?p={page}&t=1&year=2019&_t=1580470943872'.format(page=page))
time.sleep(5)
book_id_list = chrome.find_elements_by_css_selector('.item-cover img')
book_title_list = chrome.find_elements_by_css_selector('h3')
del book_title_list[-2:]
book_title_list_length = len(book_title_list);
book_id_list_length = len(book_id_list)
print(book_title_list_length)
print(book_id_list_length)
for t, i in zip(book_title_list, book_id_list):
    title_list.append(t.get_attribute('title'))
    book_id = re.sub(r'https.*/', "", i.get_attribute('src'))
    book_ids = re.search(r'\d*', book_id)
    book_urls = 'https://lib-nuanxin.wqxuetang.com/read/pdf/{book_ids}'.format(book_ids=book_ids.group())
    url_list.append(book_urls)
with open('url_list.json', 'w') as w:
    json.dump(url_list, w)
with open('title_list.json', 'w') as w:
    json.dump(title_list, w)
