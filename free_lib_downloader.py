from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
import os
import json
import time
import requests

'''作者觉得还能抢救一下.'''

headers = {}
cookies = []
attempt = 0


def init():
    global headers, cookies
    headers = {'referer': 'https://lib-nuanxin.wqxuetang.com/read/pdf/3209350',
               'sec-fetch-mode': 'no-cors',
               'sec-fetch-site': 'same-origin',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
    cookies = [
        {
            "domain": ".wqxuetang.com",
            "expirationDate": 2202632891.458739,
            "hostOnly": False,
            "httpOnly": False,
            "name": "_gid",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": False,
            "storeId": "0",
            "value": "355981004881",
            "id": 1
        },
        {
            "domain": ".wqxuetang.com",
            "expirationDate": 2202632891.458763,
            "hostOnly": False,
            "httpOnly": False,
            "name": "_gidv",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": False,
            "storeId": "0",
            "value": "546263cba4f3167ea71eb410d88fd72f",
            "id": 2
        },
        {
            "domain": ".wqxuetang.com",
            "hostOnly": False,
            "httpOnly": False,
            "name": "Hm_lpvt_a84b27ffd87daa3273555205ef60df89",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": True,
            "storeId": "0",
            "value": "1580552936",
            "id": 3
        },
        {
            "domain": ".wqxuetang.com",
            "expirationDate": 1612088936,
            "hostOnly": False,
            "httpOnly": False,
            "name": "Hm_lvt_a84b27ffd87daa3273555205ef60df89",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": False,
            "storeId": "0",
            "value": "1580521546,1580529669,1580552891,1580552936",
            "id": 4
        },
        {
            "domain": ".wqxuetang.com",
            "hostOnly": False,
            "httpOnly": False,
            "name": "PHPSESSID",
            "path": "/",
            "sameSite": "unspecified",
            "secure": False,
            "session": True,
            "storeId": "0",
            "value": "q7kcc7usslg9tm62vmkbrjv8us",
            "id": 5
        }
    ]


def set_up_chrome():
    global chrome
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
    chrome.implicitly_wait(20)


def get_img(urls, title):
    attempts = 0
    os.makedirs(title, exist_ok=True)
    headers['referer'] = urls
    chrome.get(urls)
    # for i in cookies:
    #     chrome.add_cookie(i)
    # time.sleep(10)
    ratio = chrome.find_element_by_class_name('page-head-tol').text
    length = re.sub(r'.*/ ', "", ratio)
    print('This book has {length} pages'.format(length=length))
    length = int(length) + 1
    for num in range(1, length):
        while attempts <= 10:
            try:
                res = chrome.find_element_by_css_selector('.page-img-box[index="{ind}"] > img'.format(ind=num))
                src = res.get_attribute('src')
                print(src)
                img = requests.get(src, headers=headers, timeout=30)
                with open(os.path.join(title, os.path.basename('{num}.jpg'.format(num=str(num)))), 'wb') as file:
                    for chunk in img.iter_content(100000):
                        file.write(chunk)
            except:
                print('error for downloading,try again')
                attempts += 1
                if attempts == 11:
                    with open('download.log', 'w') as lgs:
                        lgs.writelines('{} of {} is wrong'.format(str(num), title))
                chrome.refresh()
                button = chrome.find_element_by_id('input')
                button.send_keys(Keys.CONTROL, 'a')
                button.send_keys(num)
                ActionChains(chrome).move_by_offset(0, 0).click().perform()
                time.sleep(5)
            else:
                attempts = 0
                print('{num} is downloaded'.format(num=str(num)))
                break
        num += 1
        button = chrome.find_element_by_id('input')
        button.send_keys(Keys.CONTROL, 'a')
        button.send_keys(num)
        ActionChains(chrome).move_by_offset(0, 0).click().perform()
        time.sleep(3)
    print('done')
    return length


init()
set_up_chrome()
with open('title_list.json') as tl:
    title_list = json.load(tl)
with open('url_list.json') as ul:
    url_list = json.load(ul)
for u, t in zip(url_list, title_list):
    while attempt <= 10:
        try:
            get_img(u, t)
        except:
            with open('book.log', 'a') as logs:
                logs.write('{} is wrong.\n'.format(t))
            print('error for getting url,retrying')
            attempt += 1
            time.sleep(30)
        else:
            attempt = 0
            break
