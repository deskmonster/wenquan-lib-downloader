from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import re
import jwt
import os
import json
import time
import requests
from retrying import retry

'''作者觉得还能抢救一下.'''

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:60.0) Gecko/20100101 Firefox/60.0",
}
cookies = []
base_url = 'https://lib-nuanxin.wqxuetang.com/read/pdf/'
jwt_secret = "g0NnWdSE8qEjdMD8a1aq12qEYphwErKctvfd3IktWHWiOBpVsgkecur38aBRPn2w"

# def init():
#     global headers, cookies
#     headers = {'referer': 'https://lib-nuanxin.wqxuetang.com/read/pdf/3209350',
#                'sec-fetch-mode': 'no-cors',
#                'sec-fetch-site': 'same-origin',
#                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
#     cookies = [
#         {
#             "domain": ".wqxuetang.com",
#             "expirationDate": 2202632891.458739,
#             "hostOnly": False,
#             "httpOnly": False,
#             "name": "_gid",
#             "path": "/",
#             "sameSite": "unspecified",
#             "secure": False,
#             "session": False,
#             "storeId": "0",
#             "value": "355981004881",
#             "id": 1
#         },
#         {
#             "domain": ".wqxuetang.com",
#             "expirationDate": 2202632891.458763,
#             "hostOnly": False,
#             "httpOnly": False,
#             "name": "_gidv",
#             "path": "/",
#             "sameSite": "unspecified",
#             "secure": False,
#             "session": False,
#             "storeId": "0",
#             "value": "546263cba4f3167ea71eb410d88fd72f",
#             "id": 2
#         },
#         {
#             "domain": ".wqxuetang.com",
#             "hostOnly": False,
#             "httpOnly": False,
#             "name": "Hm_lpvt_a84b27ffd87daa3273555205ef60df89",
#             "path": "/",
#             "sameSite": "unspecified",
#             "secure": False,
#             "session": True,
#             "storeId": "0",
#             "value": "1580552936",
#             "id": 3
#         },
#         {
#             "domain": ".wqxuetang.com",
#             "expirationDate": 1612088936,
#             "hostOnly": False,
#             "httpOnly": False,
#             "name": "Hm_lvt_a84b27ffd87daa3273555205ef60df89",
#             "path": "/",
#             "sameSite": "unspecified",
#             "secure": False,
#             "session": False,
#             "storeId": "0",
#             "value": "1580521546,1580529669,1580552891,1580552936",
#             "id": 4
#         },
#         {
#             "domain": ".wqxuetang.com",
#             "hostOnly": False,
#             "httpOnly": False,
#             "name": "PHPSESSID",
#             "path": "/",
#             "sameSite": "unspecified",
#             "secure": False,
#             "session": True,
#             "storeId": "0",
#             "value": "q7kcc7usslg9tm62vmkbrjv8us",
#             "id": 5
#         }
#     ]


# def set_up_chrome():
#     global chrome
#     options = webdriver.ChromeOptions()
#     prefs = {
#         'profile.default_content_setting_values': {
#             'images': 2,
#             'javascript': 2  # 2即为禁用的意思
#         }
#     }
#     options.add_argument('--no-sandbox')
#     options.add_argument('--headless')  # 无头参数
#     options.add_argument('--disable-gpu')
#     options.add_experimental_option('prefs', prefs)
#     chrome = webdriver.Chrome(options=options)
#     chrome.implicitly_wait(20)

@retry()
def json_call(book_id):
    url = 'https://lib-nuanxin.wqxuetang.com/v1/read/k?bid=' + book_id
    r = requests.Session()
    r.headers.update(HEADERS)
    r = r.get(url, headers={
        'referer': url,
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user': 'bapkg/com.bookask.wqxuetang baver/1.1.1',
    })
    r.raise_for_status()
    result = r.json()
    print(result)
    return result['data']


def get_img(book_id, title, pages):
    jwtkey = json_call(book_id)
    attempt = 0
    for page in range(1, int(pages)+1):
        while attempt <= 5:
            try:
                cur_time = time.time()
                jwttoken = jwt.encode({
                    "p": page,
                    "t": int(cur_time * 1000),
                    "b": str(book_id),
                    "w": 1000,
                    "k": json.dumps(jwtkey),
                    "iat": int(cur_time)
                }, jwt_secret, algorithm='HS256').decode('ascii')
                img = requests.Session()
                img = img.get('https://lib-nuanxin.wqxuetang.com/page/img/%s/%s?k=%s' % (
                        book_id, page, jwttoken), headers={
                        'referer': base_url+book_id,
                        'sec-fetch-mode': 'no-cors',
                        'sec-fetch-site': 'same-origin',
                    },timeout=30)
                img.raise_for_status()
                if img.headers.get('pragma') != 'catch':
                    raise Exception('Try again')
                with open(os.path.join(title, os.path.basename('{num}.jpg'.format(num=str(page)))), 'wb') as file:
                    for chunk in img.iter_content(100000):
                        file.write(chunk)
            except:
                print('{} is error,retrying'.format(str(page)))
                time.sleep(4)
                jwtkey = json_call(book_id,)
                attempt += 1
                if attempt == 6:
                    with open('download.log', 'a') as lgs:
                        lgs.write('{} of {} is wrong\n'.format(str(page), title))

            else:
                print('{} is downloaded'.format(page))
                attempt = 0
                break


@retry(stop_max_attempt_number=5)
def starter(title, book_id, pages):
    os.makedirs(title, exist_ok=True)
    get_img(book_id, title, pages)


if __name__ == '__main__':
    with open('title_list.json') as ti:
        title_list = json.load(ti)
    with open('id_list.json') as bi:
        id_list = json.load(bi)
    with open('page_list.json') as pg:
        page_list = json.load(pg)
    for t, i, p in zip(title_list, id_list, page_list):
        try:
            starter(t, i, p)
            print('{} is downloaded'.format(t))
        except:
            print('{} is wrong'.format(t))
            with open('book.log', 'a') as logs:
                logs.write('{} is wrong.\n'.format(t))
            continue
