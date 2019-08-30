import pandas as pd
import pymongo
from pylab import *
import matplotlib.pyplot as plt


def data_process(city):
    cities = {
        'bd': '保定',
        'bt': '保亭',
        'bj': '北京',
        'chengde': '承德',
        'cc': '长春',
        'cz': '滁州',
        'cs': '长沙',
        'cm': '澄迈',
        'cq': '重庆',
        'cd': '成都',
        'dl': '大连',
        'dg': '东莞',
        'dz': '儋州',
        'dongfang': '东方',
        'da': '定安',
        'dy': '德阳',
        'dali': '大理',
        'fs': '佛山',
        'gz': '广州',
        'gl': '桂林',
        'gy': '贵阳',
        'hd': '邯郸',
        'hs': '衡水',
        'hhht': '呼和浩特',
        'hz': '杭州',
        'huzhou': '湖州',
        'hf': '合肥',
        'hg': '黄冈',
        'hui': '惠州',
        'hk': '海口',
        'jz': '晋中',
        'jx': '嘉兴',
        'jn': '济南',
        'km': '昆明',
        'lf': '廊坊',
        'ly': '龙岩',
        'lg': '临高',
        'ld': '乐东',
        'ls': '陵水',
        'leshan': '乐山',
        'ms': '眉山',
        'nj': '南京',
        'nt': '南通',
        'nb': '宁波',
        'nc': '南昌',
        'nn': '南宁',
        'qhd': '秦皇岛',
        'quanzhou': '泉州',
        'qd': '青岛',
        'qy': '清远',
        'qh': '琼海',
        'qz': '琼中',
        'sjz': '石家庄',
        'sy': '沈阳',
        'sh': '上海',
        'su': '苏州',
        'sx': '绍兴',
        'sz': '深圳',
        'san': '三亚',
        'tj': '天津',
        'ty': '太原',
        'wx': '无锡',
        'weihai': '威海',
        'wh': '武汉',
        'wzs': '五指山',
        'wc': '文昌',
        'wn': '万宁',
        'xt': '邢台',
        'xz': '徐州',
        'xm': '厦门',
        'xn': '咸宁',
        'xsbn': '西双版纳',
        'xa': '西安',
        'yt': '烟台',
        'zjk': '张家口',
        'zj': '镇江',
        'zhangzhou': '漳州',
        'zz': '郑州',
        'zh': '珠海',
        'zs': '中山'
    }
    # 链接数据库
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.house
    collection = db[city]
    data = []
    for item in collection.find():
        del item['_id']
        data.append(item)

    df = pd.DataFrame(data)

    # 索引处理
    df.index.name = 'No'
    new_col = ['楼盘名称', '区域位置', '参考价格', '产权年限', '开发商', '物业公司', '物业费', '容积率', '绿化率']
    col_name = {'参考价格': '价格 (元/平)', '产权年限': '产权 (年)', '物业费': '物业费 (元/平/月)',
                '绿化率': '绿化率（%）'}
    df = df.reindex(columns=new_col).rename(columns=col_name)

    # 区域位置数据处理，去掉城市，只保留区县，对于 NA 的，直接去掉
    df = df[df['区域位置'].notnull()]
    df['区域位置'] = df['区域位置'].map(lambda x: str(x).split('-')[1])

    # 价格处理，利用正则表达式数字，价格未定、只写了总价的不具有可比性，以 NA 填充
    price_re = re.compile(r'均价 (\d+)元/平')
    # 先函数映射正则匹配，剔除缺失值，再利用函数映射提取数据
    df['价格 (元/平)'] = df['价格 (元/平)'].map(lambda x: price_re.match(x)).dropna().map(lambda x: int(x.group(1)))

    # 产权修改，产权有些有多种，但数量不多，为了节省资源，以第一个数字为准
    df['产权 (年)'] = df['产权 (年)'].map(lambda x: int(x[:2]))

    # 物业费有些是范围，有些是数字，对于范围的，我们利用 numpy 求平均值，注意缺失值处理
    # 先提取数字部分，以 '~' 分隔，并剔除缺失值
    no_na = df['物业费 (元/平/月)'].map(lambda x: x[:-6].split('~') if x[:-6] != '' else None).dropna()
    # 转换为 array 数组并求平均值
    df['物业费 (元/平/月)'] = no_na.map(lambda x: np.array(list(map(float, x))).mean())

    # 将容积率、绿化率转换为数字
    df['容积率'] = df['容积率'].map(lambda x: float(x) if x != '暂无信息' else None)
    df['绿化率（%）'] = df['绿化率（%）'].map(lambda x: float(x[:-1]) if x != '暂无信息' else None)

    df.to_csv('Processed_{}.csv'.format(city.upper()), encoding='utf-8-sig')

    # 分析与绘图
    # 显示中文
    mpl.rcParams['font.sans-serif']=['SimHei']

    # 区域楼盘数与均价
    area = df['区域位置'].value_counts()
    plt.rc('figure', figsize=(8, 6))
    plt.rc('font', size=8)
    # 设置绘图区域
    fig, axes1 = plt.subplots(1, 1)
    # 图片命名
    axes1.set_title('{}各区楼盘数量及均价图'.format(cities[city]), fontsize=16)
    # 绘制各区楼盘数量
    axes1.bar(x=area.index, height=area.values, label='各区楼盘数', color='k', alpha=0.3)
    # x 轴标签旋转 45 度
    axes1.set_xticklabels(area.index, rotation=60)
    axes1.set_xlabel('区域')
    axes1.set_ylabel('楼盘数量')
    x = np.arange(len(area))
    # y = np.array(area.values)
    # for a,b in zip(x,y):
    #     plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=10)
    # 计算各区均价
    price = df.groupby(df['区域位置'])[['价格 (元/平)']].mean().reindex(area.index)
    # 新建绘图区，与 axes1 共用 x 轴
    axes2 = axes1.twinx()
    # 绘制各区均价
    axes2.plot(price.values, label='各区均价', color='darkorange', marker='o', markersize='5', markerfacecolor='white')
    axes2.set_ylabel('均价（元/平）')
    # 设置均价值标签
    y1 = np.array(price.values)
    for a, b in zip(x, y1):
        plt.text(a, b+0.1, '%.0f' % b, fontsize=8, horizontalalignment='center', verticalalignment='bottom')
    # 绘制全市均价线
    average_price = df['价格 (元/平)'].mean()
    axes3 = axes2.twiny()
    axes3.plot(np.ones(len(area)) * average_price, 'r--', label='全市均价：%d' % average_price)
    axes3.set_xticks([])
    # 设置图例
    handles1, labels1 = axes1.get_legend_handles_labels()
    handles2, labels2 = axes2.get_legend_handles_labels()
    handles3, labels3 = axes3.get_legend_handles_labels()
    plt.legend(handles1 + handles2 + handles3, labels1 + labels2 + labels3, loc='best')
    plt.savefig('{}各区域楼盘数量及均价.png'.format(cities[city]), dpi=400, bbox_inches='tight')
    plt.close()

    # 区域产权、物业费、绿化率、容积率：
    grouped = df.groupby(df['区域位置'])
    property_years = grouped[['产权 (年)']].mean().reindex(area.index)
    property_costs = grouped[['物业费 (元/平/月)']].mean().reindex(area.index)
    volume_rate = grouped[['容积率']].mean().reindex(area.index)
    greening_rate = grouped[['绿化率（%）']].mean().reindex(area.index)
    values = [property_years, property_costs, volume_rate, greening_rate]
    plt.rc('figure', figsize=(10, 10))
    plt.rc('font', size=8)
    fig, axes = subplots(2, 2)
    k = 0
    keys = ['产权', '物业费', '容积率', '绿化率']
    for i in range(2):
        for j in range(2):
            # 绘制指标
            axes[i, j].bar(x=values[k].index, height=values[k].values.T[0], color='k', alpha=0.3)
            # x 轴标签旋转 45 度
            axes[i, j].set_xticklabels(values[k].index, rotation=90)
            axes[i, j].set_xlabel('区域')
            axes[i, j].set_ylabel(values[k].columns[0])
            axes[i, j].set_title('{}各区域楼盘平均{}对比'.format(cities[city], keys[k]))
            x = np.arange(len(values[k]))
            y = np.array(values[k].values)
            for a, b in zip(x, y):
                axes[i, j].text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom',fontsize=8)
            k += 1
    plt.subplots_adjust(hspace=0.5)
    plt.savefig('{}各区域楼盘产权、物业费、容积率及绿化率.png'.format(cities[city]), dpi=400, bbox_inches='tight')
    plt.close()
    print('Figure saved')
    return None
