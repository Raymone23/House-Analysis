import threading
from time import ctime
from atexit import register
from all_city.house_city_common_sql import *
from all_city.Data_Process_sql import data_process

# 房屋类型
HOUSE_CLASS = {
    '全部': '',
    '住宅': 'nht1',
    '别墅': 'nht2',
    '写字楼': 'nht3',
    '商业': 'nht4',
    '底商': 'nht5',
}

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                           (KHTML, likeGecko) Chrome/76.0.3809.100 Safari/537.36'
}

# 城市字典
CITIES = {
    '保定': 'bd',
    '保亭': 'bt',
    '北京': 'bj',
    '承德': 'chengde',
    '长春': 'cc',
    '滁州': 'cz',
    '长沙': 'cs',
    '澄迈': 'cm',
    '重庆': 'cq',
    '成都': 'cd',
    '大连': 'dl',
    '东莞': 'dg',
    '儋州': 'dz',
    '东方': 'dongfang',
    '定安': 'da',
    '德阳': 'dy',
    '大理': 'dali',
    '佛山': 'fs',
    '广州': 'gz',
    '桂林': 'gl',
    '贵阳': 'gy',
    '邯郸': 'hd',
    '衡水': 'hs',
    '呼和浩特': 'hhht',
    '杭州': 'hz',
    '湖州': 'huzhou',
    '合肥': 'hf',
    '黄冈': 'hg',
    '惠州': 'hui',
    '海口': 'hk',
    '晋中': 'jz',
    '嘉兴': 'jx',
    '济南': 'jn',
    '昆明': 'km',
    '廊坊': 'lf',
    '龙岩': 'ly',
    '临高': 'lg',
    '乐东': 'ld',
    '陵水': 'ls',
    '乐山': 'leshan',
    '眉山': 'ms',
    '南京': 'nj',
    '南通': 'nt',
    '宁波': 'nb',
    '南昌': 'nc',
    '南宁': 'nn',
    '秦皇岛': 'qhd',
    '泉州': 'quanzhou',
    '青岛': 'qd',
    '清远': 'qy',
    '琼海': 'qh',
    '琼中': 'qz',
    '石家庄': 'sjz',
    '沈阳': 'sy',
    '上海': 'sh',
    '苏州': 'su',
    '绍兴': 'sx',
    '深圳': 'sz',
    '三亚': 'san',
    '天津': 'tj',
    '太原': 'ty',
    '无锡': 'wx',
    '威海': 'weihai',
    '武汉': 'wh',
    '五指山': 'wzs',
    '文昌': 'wc',
    '万宁': 'wn',
    '邢台': 'xt',
    '徐州': 'xz',
    '厦门': 'xm',
    '咸宁': 'xn',
    '西双版纳': 'xsbn',
    '西安': 'xa',
    '烟台': 'yt',
    '张家口': 'zjk',
    '镇江': 'zj',
    '漳州': 'zhangzhou',
    '郑州': 'zz',
    '珠海': 'zh',
    '中山': 'zs',
}
PAGES = range(1, 51)

# 数据表表头
LIST = ["参考价格", "区域位置", "开发商", "绿化率", "容积率", "产权年限", "物业公司", "物业费", "楼盘名称"]
HEAD = ' VARCHAR(255), '.join(LIST) + ' VARCHAR(255), PRIMARY KEY(楼盘名称)'


def main():
    my_house_class = HOUSE_CLASS['住宅']
    base_url = 'https://{}.fang.lianjia.com/loupan/'.format(city)
    print('Started at:{}'.format(ctime()))
    create_db(city, HEAD)
    for page in PAGES:
        threading.Thread(target=get_and_save, args=(page, base_url, city, my_house_class, HEADERS)).start()



@register
def _atexit():
    print('All done at {}'.format(ctime()))
    data_process(city)


if __name__ == '__main__':
    # 选择城市
    while True:
        try:
            inputs = input('选择你的城市：')
            city = CITIES[inputs]
        except KeyError:
            print('没有该城市数据，请重新输入!')
        else:
            break
    main()

