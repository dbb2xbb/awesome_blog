import json
import copy
from bs4 import BeautifulSoup
import re
from urllib import request
import traceback


def get_html_content(url='http://www.baidu.com'):
    try:
        with request.urlopen(url) as f:
            data = f.read()
            # print('data:{}'.format(data.decode('utf-8')))
            return data
    except:
        traceback.print_exc()

def parse_html_content(content):
    alist = []
    soup = BeautifulSoup(content, "html.parser", from_encoding='utf-8')
    tbody = soup.find_all('tr')
    for idx,tr in enumerate(tbody):
        if idx > 0:
            anime_info = {
                'year':0,
                'name':[]
            }
            anime_info['year'] = tr.contents[0].text.replace('\n','')
            for a in tr.find_all('a'):
                anime_info['name'].append(a.string)

            alist.append(anime_info)

    return json.dumps(alist)

def show_res(alist):
    print(alist)

def main():
    url = ''
    cnt = get_html_content(url=url)
    res = parse_html_content(cnt)
    show_res(res)

if __name__ == '__main__':
    main()




