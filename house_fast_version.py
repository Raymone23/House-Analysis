import requests
import json
import threading
from bs4 import BeautifulSoup
from time import ctime
from atexit import register
from Data_Process import data_process


# 定义 soup，以便复用
def get_soup(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


# 获取楼盘名字和对应的 URL 代码
def get_name_dic(url):
    soup = get_soup(url)
    selected = soup.select('ul.resblock-list-wrapper div.resblock-name a')
    name_dic = {}
    for item in selected:
        name_dic[item.string] = item['href'][8:]
        print('code of {} getted.'.format(item.string))
    return name_dic


# 获取楼盘中需要的信息
def get_info(url):
    soup = get_soup(url)
    lis = soup.select('ul.x-box li')
    infos = {}
    my_keys = ['参考价格：', '区域位置：', '绿化率：', '容积率：', '产权年限：', '开发商：', '物业公司：', '物业费：']
    for li in lis:
        if li.select('.label')[0].text in my_keys:
            label = li.select('.label')[0].text.replace('：', '')
            value = li.select('.label-val')[0].text.strip()
        else:
            continue
        infos[label] = value
        print('info getted')
    return infos


def save_to_json(data, name='data'):
    results = json.dumps(data, ensure_ascii=False)
    with open(name + '.json', 'a+', encoding='utf-8') as f:
        f.write(results)
        f.write('\n')
    return None


def get_and_save(page, base_url, filename):
    page_info = []
    print(page)
    list_url = '{base}{house}pg{page}'.format(base=base_url, house=MY_HOUSE_CLASS, page=page)
    name_dic = get_name_dic(list_url)
    for name, code in name_dic.items():
        detail_url = base_url + code + 'xiangqing/'
        my_info = get_info(detail_url)
        my_info['楼盘名称'] = name
        page_info.append(my_info)
    save_to_json(page_info, name=filename)
    print('Page {} saved'.format(page))


# 固定变量
HOUSE_CLASS = {
    '全部': '',
    '住宅': 'nht1',
    '别墅': 'nht2',
    '写字楼': 'nht3',
    '商业': 'nht4',
    '底商': 'nht5',
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                           (KHTML, likeGecko) Chrome/76.0.3809.100 Safari/537.36'
}

# 可变变量
cities = {
    '重庆': 'cq',
    '成都': 'cd',
}
CITY = cities['重庆']
MY_HOUSE_CLASS = HOUSE_CLASS['住宅']
PAGES = range(1, 51)


def main():
    # 文件初始化
    with open(CITY + '.json', 'w', encoding='utf-8') as f:
        pass
    base_url = 'https://{}.fang.lianjia.com/loupan/'.format(CITY)
    print('Started at:{}'.format(ctime()))
    for page in PAGES:
        threading.Thread(target=get_and_save, args=(page, base_url, CITY)).start()



@register
def _atexit():
    print('All done at {}'.format(ctime()))
    data_process(CITY)


if __name__ == '__main__':
    # 选择城市
    # CITY = cities[input('选择你的城市：')]
    main()
