import requests
import json
from bs4 import BeautifulSoup


# 定义 soup，以便复用
def get_soup(url, headers):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


# 获取楼盘名字和对应的 URL 代码
def get_name_dic(url, headers):
    soup = get_soup(url, headers)
    selected = soup.select('ul.resblock-list-wrapper div.resblock-name a')
    name_dic = {}
    for item in selected:
        name_dic[item.string] = item['href'][8:]
        print('code of {} getted.'.format(item.string))
    return name_dic


# 获取楼盘中需要的信息
def get_info(url, headers):
    soup = get_soup(url, headers)
    lis = soup.select('ul.x-box li')
    infos = {}
    my_keys = ['参考价格：', '区域位置：', '绿化率：', '容积率：', '产权年限：', '开发商：', '物业公司：', '物业费：']
    for li in lis:
        if li.select('.label')[0].text in my_keys:
            label = li.select('.label')[0].text.replace('：', '')
            print(label)
            print(li.select('.label-val'))
            if li.select('.label-val'):
                value = li.select('.label-val')[0].text.strip()
            else:
                continue
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


def get_and_save(page, base_url, filename, house_class, headers):
    page_info = []
    print(page)
    list_url = '{base}{house}pg{page}'.format(base=base_url, house=house_class, page=page)
    name_dic = get_name_dic(list_url, headers)
    for name, code in name_dic.items():
        print(name)
        detail_url = base_url + code + 'xiangqing/'
        my_info = get_info(detail_url, headers)
        my_info['楼盘名称'] = name
        page_info.append(my_info)
    save_to_json(page_info, name=filename)
    print('Page {} saved'.format(page))
