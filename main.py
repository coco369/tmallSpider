import re
import json
import time
import requests
from bs4 import BeautifulSoup
import pymongo



old_ids = []  # 存放访问过的id值
new_ids = []  # 存放未访问过id的字典
datas = []  # 存放最终数据字典
headers = {
    "Referer": "https://www.tmall.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-site",
    "accept": "*/*",
    "cookie": ''
    }


def add_visited_id(id):
    """
    添加未访问的id
    :param id
    """
    old_ids.append(id)


def delete_visit_id():
    """
    删除访问后的id
    """
    new_ids.pop(0)


def spider_first(url):
    """
    爬取第一个传入的网页信息
    :param url
    :return data
    """
    response = requests.get(url, headers=headers)
    page_txt = response.text
    soup = BeautifulSoup(page_txt, 'html.parser')
    title = soup.find('title')
    title_res = title.get_text()
    data = {'title': title_res[:-12]}
    id = get_id(url)
    add_visited_id(id)
    get_other_ids(id)
    data.update(get_price_and_count(id))
    data.update(get_grade_and_rate(id))
    return data


def spider_not_first(id, value):
    """
    爬取非第一个网页的信息
    :param id
    :param value
    :return data
    """
    add_visited_id(id)
    get_other_ids(id)
    data = {}
    data.update(get_not_first_title(value))
    data.update(get_grade_and_rate(id))
    data.update(get_price_and_count(id))
    delete_visit_id()
    return data


def get_id(url):
    """
    url中提取id信息
    :param url
    :return id
    """
    index = re.search(r'&id=[0-9]+', url).span()
    return url[index[0] + 4:index[1]]


def get_other_ids(id):
    """
    爬取页面相关链接并存入待爬取队列中
    :param id
    """
    if id is None:
        print("id错误")
        return
    url = 'https://aldcdn.tmall.com/recommend.htm?itemId=' + id + '&categoryId=50019790&sellerId=1714128138&shopId=104736810&brandId=3506680&refer=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fspm%3Da230r.1.14.13.58404068ssb0Wo%26id%3D559983439811%26cm_id%3D140105335569ed55e27b%26abbucket%3D7%26skuId%3D3493501272522&brandSiteId=2&rn=&appId=03054&isVitual3C=false&isMiao=false&count=12&callback=jsonpAld03054'
    response = requests.get(url, headers=headers)
    # print(response.text)
    jsons = text_to_json(response.text)
    for js in jsons['list']:
        if get_id(js['url']) not in old_ids:
            new_ids.append({get_id(js['url']): js['title']})


def get_not_first_title(value):
    """
    根据值生成标题字典
    :param value
    :return title
    """
    return {'title': value}


def text_to_json(text):
    """
    字符串转json
    :param text
    :return json
    """
    index = re.search(r'{.*}', text).span()
    context = text[index[0]:index[1]]
    js = json.loads(context)
    return js


def get_price_and_count(id):
    """
    爬取价格和销量信息
    :param id
    :returns price and count
    """
    url = 'https://mdskip.taobao.com/core/initItemDetail.htm?isUseInventoryCenter=true&cartEnable=true&service3C=true&isApparel=false&isSecKill=false&tmallBuySupport=true&isAreaSell=true&tryBeforeBuy=false&offlineShop=false&itemId=' + id + '&showShopProm=false&isPurchaseMallPage=false&itemGmtModified=1574743866000&isRegionLevel=true&household=false&sellerPreview=false&queryMemberRight=true&addressLevel=4&isForbidBuyItem=false&callback=setMdskip&timestamp=1574745288144&isg=dBNhyB-PqRe4oV4TBOfadurza77T2IOf1RVzaNbMiICPOdCeSwBPWZpLX7TwCnGV3sgM83Jt3efYBq8syyUB7-EhuzWn9Mp9td8pR&isg2=BM7OkeroH-VgS6tWh8WCyQG7H6RQ57n_AdmaQvgWAVGGW221Y92vWaZak8eS-Yph&ref=https%3A%2F%2Fs.taobao.com%2Fsearch%3Fq%3D%25E7%2594%25B5%25E8%25A7%2586%26imgfile%3D%26js%3D1%26stats_click%3Dsearch_radio_all%253A1%26initiative_id%3Dstaobaoz_20191126%26ie%3Dutf8'
    response = requests.get(url, headers=headers)
    print(response.text)
    print(response.status_code)
    js = text_to_json(response.text)
    # print(js['defaultModel']['sellCountDO']['sellCount'])
    (key, value), = js['defaultModel']['itemPriceResultDO']['priceInfo'].items()
    # print(value['promotionList'][0]['price'])
    try:
        price = {'price': value['promotionList'][0]['price'],
                 'sellCount': js['defaultModel']['sellCountDO']['sellCount']}
    except:     # 有些json格式不一样
        try:
            price = {'price': value['price'],
                 'sellCount': js['defaultModel']['sellCountDO']['sellCount']}
        except:    # 聚划算的json格式不一样
            price = {'price': value['suggestivePromotionList'][0]['price'],
                 'sellCount': js['defaultModel']['sellCountDO']['sellCount']}
    return price


def get_grade_and_rate(id):
    """
    爬取评价数和评分信息
    :param id
    :returns gradeAvg and rateTotal
    """
    url = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=' + id + '&spuId=888470564&sellerId=1714128138&groupId&_ksTS=1574745874292_239&callback=jsonp240'
    response = requests.get(url, headers=headers)
    js = text_to_json(response.text)
    print(js)
    return {'gradeAvg': js['dsr']['gradeAvg'], 'rateTotal': js['dsr']['rateTotal']}


def add_data(data):
    """
    添加爬取后的数据到总数据数组中
    :param data
    """
    datas.append(data)


def save_data(data):
    """
    数据添加到数据库中
    :param data
    :return boolean
    """
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client['taobao']
    collection = db['goods']
    collection.insert_one(data)
    return True


if __name__ == '__main__':
    print(1)
    url = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.13.58404068ssb0Wo&id=559983439811&cm_id=140105335569ed55e27b&abbucket=7&skuId=3493501272522'
    x = spider_first(url)
    print(x)
    add_data(x)
    print(old_ids)
    print(new_ids)
    print("===========")
    for i in range(100):
        print(i+1)
        time.sleep(1)
        (key, value), = new_ids[0].items()
        y = spider_not_first(key, value)
        print(y)
        # save_data(y)
        add_data(y)
        print(old_ids)
        print(new_ids)
    print(datas)
