import requests
import pymysql
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
        # print('code of {} getted.'.format(item.string))
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
            # print(label)
            # print(li.select('.label-val'))
            if li.select('.label-val'):
                value = li.select('.label-val')[0].text.strip()
            else:
                continue
        else:
            continue
        infos[label] = value
        # print('info getted')
    return infos


# 创建数据库或表
def create_db(name, head):
    # 连接数据库
    try:
        db = pymysql.connect(host='localhost', user='root', password='yeswedid631,,', port=3306, db='house')
        cursor = db.cursor()
    except pymysql.err.InternalError:
        db = pymysql.connect(host='localhost', user='root', password='yeswedid631,,', port=3306)
        cursor = db.cursor()
        cursor.execute('CREATE DATABASE house DEFAULT CHARACTER SET utf8')
    # 创建城市表
    sql = 'CREATE TABLE IF NOT EXISTS {} ({})'.format(name, head)
    cursor.execute(sql)
    db.close()


def save_to_db(data, name='data'):
    # 表头
    keys = ', '.join(data.keys())
    # 构造插入的占位符，使用 , 分隔，数量等于字典的长度
    values = ','.join(['%s'] * len(data))
    # 连接数据库
    db = pymysql.connect(host='localhost', user='root', password='yeswedid631,,', port=3306, db='house')
    cursor = db.cursor()
    # 加上 ON DUPLICATE KEY UPDATE，表明如果主键已经存在，则执行更新操作
    sql = 'INSERT INTO {table}({keys}) VALUES({values}) ON DUPLICATE KEY UPDATE'.format(table=name,
                                                                                        keys=keys, values=values)
    # update = 'id = %s, name = %s, age = %s'
    update = ','.join([" {key} = %s".format(key=key) for key in data])
    # 完整的 SQL 语句
    sql += update
    try:
        if cursor.execute(sql, tuple(data.values()) * 2):
            print('Data saved')
            db.commit()
    except:
        print('Failed to save data')
        db.rollback()
    db.close()
    return None


def get_and_save(page, base_url, filename, house_class, headers):
    # print(page)
    list_url = '{base}{house}pg{page}'.format(base=base_url, house=house_class, page=page)
    name_dic = get_name_dic(list_url, headers)
    for name, code in name_dic.items():
        # print(name)
        detail_url = base_url + code + 'xiangqing/'
        my_info = get_info(detail_url, headers)
        my_info['楼盘名称'] = name
        save_to_db(my_info, name=filename)
