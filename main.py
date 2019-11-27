import re
import json
import time
import requests
from bs4 import BeautifulSoup
import pymongo



old_ids = []  # 存放访问过的id值
new_ids = []  # 存放未访问过id的字典
datas = []  # 存放最终数据字典
shopid = ""
headers = {
    "Referer": "https://www.tmall.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "sec-fetch-mode": "no-cors",
    "sec-fetch-site": "cross-site",
    "accept": "*/*",
    "cookie": 't=4fffbcb931493463ccc3bd231a627f5e; thw=cn; enc=S8Dx40SKyG1j0da94qU71tAr4FAjQc408FLPvHQ1xEEAtTNkpTyEGw4rh89v3giX9g1D2ZkbkIL6ck5w7QS1KQ%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; UM_distinctid=16cd344097b6d2-0f9aab95adac12-7373e61-144000-16cd344097c271; ucn=center; cna=D4/MFbd5yGkCAW8pc7fjcu9R; lgc=%5Cu7B11%5Cu770B%5Cu5468%5Cu745C%5Cu6253%5Cu9EC4%5Cu76D6; tracknick=%5Cu7B11%5Cu770B%5Cu5468%5Cu745C%5Cu6253%5Cu9EC4%5Cu76D6; tg=0; mt=ci=-1_0; cookie2=15994181cce84ecc18dc3fe3c6f7d80b; v=0; _tb_token_=5b33be9676d67; unb=2452981807; uc1=cookie15=Vq8l%2BKCLz3%2F65A%3D%3D&cookie16=URm48syIJ1yk0MX2J7mAAEhTuw%3D%3D&cookie14=UoTbmVgT%2FjEcVA%3D%3D&pas=0&cookie21=URm48syIYB3rzvI4Dim4&lng=zh_CN&tag=10&existShop=false; uc3=lg2=UtASsssmOIJ0bQ%3D%3D&nk2=sy5iGiA8t0QHe7oyEEo%3D&id2=UUwVZj8AzY7ofQ%3D%3D&vt3=F8dByuQH9liFlzTsivc%3D; csg=4c07299d; cookie17=UUwVZj8AzY7ofQ%3D%3D; dnk=%5Cu7B11%5Cu770B%5Cu5468%5Cu745C%5Cu6253%5Cu9EC4%5Cu76D6; skt=49ab2757665405d4; existShop=MTU3NDg1MDkzOQ%3D%3D; uc4=id4=0%40U27KCo7v9xPMlvwkgEHKIC2I1ZVS&nk4=0%40sVGukzSZvbmQ4S1DuTMTax6TnUNDddxnPw%3D%3D; _cc_=VT5L2FSpdA%3D%3D; _l_g_=Ug%3D%3D; sg=%E7%9B%9672; _nk_=%5Cu7B11%5Cu770B%5Cu5468%5Cu745C%5Cu6253%5Cu9EC4%5Cu76D6; cookie1=B0f3kZbjh7h%2BmIbq3eOIs2rTgdSa6uDbMPu5c6SpDLk%3D; isg=BB0dKMaoHGKaYvhMMgaY2E__LPkXOlGM_qRpD9_iT3Sjlj3Ip4oYXHIHwMo1fGlE; l=dBEYQTOIqVIy80W-BOCZnurza77tQIRvnuPzaNbMi_5w-6Ts3sQOkp5HlF96cjWfOILB4dH2-sp9-etkw_x6UnIpXUJ6txDc.'
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
    soup_shopid = BeautifulSoup(page_txt, 'html.parser')
    shopid_text = soup_shopid.find('div', id='LineZing')
    title = soup.find('title')
    title_res = title.get_text()
    data = {'title': title_res[:-12]}
    global shopid
    shopid = shopid_text['shopid']
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
    url = 'https://aldcdn.tmall.com/recommend.htm?itemId=' + id + '&categoryId=50019790&sellerId=1714128138&shopId=' + shopid + '&brandId=3506680&refer=https%3A%2F%2Fdetail.tmall.com%2Fitem.htm%3Fspm%3Da230r.1.14.13.58404068ssb0Wo%26id%3D559983439811%26cm_id%3D140105335569ed55e27b%26abbucket%3D7%26skuId%3D3493501272522&brandSiteId=2&rn=&appId=03054&isVitual3C=false&isMiao=false&count=12&callback=jsonpAld03054'
    response = requests.get(url, headers=headers)
    print(response.text)
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
    # print(response.status_code)
    js = text_to_json(response.text)
    # print(js['defaultModel']['sellCountDO']['sellCount'])
    keys = list(js['defaultModel']['itemPriceResultDO']['priceInfo'].items())
    print(keys)
    key = keys[0][0]
    print(key)
    value = js['defaultModel']['itemPriceResultDO']['priceInfo'][key]
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
    # print(js)
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
    print("正在爬取第 1 条数据")
    url = 'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.1.29fb4bbbvDXMtp&id=602661042379&skuId=4387886106650&areaId=231200&user_id=2616970884&cat_id=2&is_b=1&rn=daff42eea9467dc32232f94508e70a34'
    x = spider_first(url)
    print(x)
    add_data(x)
    save_data(x)
    print(old_ids)
    print(new_ids)
    print(shopid)
    print("===========")
    for i in range(100):
        print("正在爬取第 " + str(i+2) + " 条数据")
        time.sleep(1)
        (key, value), = new_ids[0].items()
        y = spider_not_first(key, value)
        print(y)
        save_data(y)
        add_data(y)
        print(old_ids)
        print(new_ids)
    print(datas)
