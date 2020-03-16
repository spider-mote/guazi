import random
import time
import requests
import execjs
import re

class Cookies_Pool(object):

    def __init__(self):
        self.url = 'https://www.guazi.com/www/buy'
        self.header = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"zh-CN,zh;q=0.9",
            "Connection":"keep-alive",
            "Host":"www.guazi.com",
            "Referer":"https://www.guazi.com/www/buy",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3610.2 Safari/537.36",
        }
        self.cookies_list = []

    def handle_cookies(self):
        '''维持cookies_list'''
        while True:
            if len(self.cookies_list) < 10:
                response = requests.get(url=self.url,headers=self.header)
                response.encoding = 'utf-8'
                if '正在打开中,请稍后' in response.text:
                    value_search = re.compile(r"anti\('(.*?)','(.*?)'\);")
                    string = value_search.search(response.text).group(1)
                    key = value_search.search(response.text).group(2)
                    print(string,key)
                    with open('guazi.js','r') as f:
                        f_read = f.read()
                    js = execjs.compile(f_read)
                    js_return = js.call('anti',string,key)
                    cookie_value = js_return
                    print('获取到cookies：',cookie_value)
                    self.cookies_list.append(cookie_value)
                    with open('cookies_list.text','w',encoding='utf-8') as f:
                        for t in self.cookies_list:
                            f.write(t+'\n')
            else:
                break

    def test_cookies(self):
        '''测试cookies'''
        i = 0
        while i < 10:
            time.sleep(100)
            cookies = self.cookies_list[i]
            print('测试cookies：',cookies)
            header = self.header.copy()
            header['Cookie'] = cookies
            response = requests.get(url=self.url,headers=header)
            response.encoding = 'utf-8'
            if '正在打开中,请稍后' in response.text:
                print('cookies：%s失效',cookies)
                self.cookies_list.remove(cookies)
                with open('cookies_list.text', 'w', encoding='utf-8') as f:
                    for t in self.cookies_list:
                        f.write(t+'\n')
                self.handle_cookies()
            i += 1
            if i == 10:
                i = 0

    def get_cookies(self):
        with open('cookies_list.text', 'r', encoding='utf-8') as f:
            i = f.readlines()
        cookies = random.choice(i)
        return cookies

if __name__ == '__main__':
    pool = Cookies_Pool()
    pool.handle_cookies()
    pool.test_cookies()
    cookies = pool.get_cookies()
    # print(cookies)

