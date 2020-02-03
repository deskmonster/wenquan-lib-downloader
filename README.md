# wenquan-school-downloader
## wenquan_lib_info.py
该脚本用以爬取图书馆的目录，生成相关json数据用以wenquan_lib_downloader.py调用。
使用时修改`chrome.get('https://lib-nuanxin.wqxuetang.com/search?p={page}&t=1&year=2019&_t=1580470943872'.format(page=page))`
中的<2019>为你想要爬取的年份。
## wenquan_lib_downloader.py
该脚本用以爬取图书图片.
### 本爬虫尚为测试版，会有各种bug。
