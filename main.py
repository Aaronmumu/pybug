#!/usr/bin/python3
# -*- coding: utf-8 -*-

import urllib.parse as urlparse
import requests
from bs4 import BeautifulSoup
import csv
import calendar
import time
import lxml

def req(url):
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'}  # 简单定义个headers，防止识别爬虫
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        res.encoding = "utf-8"
        return res.text
    else:
        print('请求 %s 失败' % (url))
        return 0

search = [
    '排名',
    '英文标题',
    '店铺名',
    '信誉分',
    '好评率%',
    '价格低US',
    '价格高US',
    '是否包邮',
    '星级分',
    '评论',
    '订单',
    'p4p',
    '是否在线',
    '是否参加活动',
    '图片地址',
    '网址'
]

SITE = "http://www.amazon.co.jp"
Apartment = "aps"
# 设置查询的页码数
Pages = 2000
# 设置要查询的关键词
KEYWORD = [
    "switch",
]
# 需要查询的产品Asin值
Asin = [
    "B01NCX3W3O",
    "B07BQXJGW5"
]

def csvWrite(name='downoad', data=[]):
    with open(name + '.csv', 'a+', newline='') as f:
        csv_file = csv.writer(f, dialect='excel')
        csv_file.writerow(data)

def kwItem():
    for keyword in KEYWORD:
        print(keyword)
        for page in range(1, Pages + 1):
            data = {
                "keywords": keyword,
                "page": page,
                "rh": "i:" + Apartment + ",k:" + keyword
            }
            url = SITE + "/s/ref=nb_sb_noss?" + urlparse.urlencode(data)
            print(url)
            response = req(url)
            soup = BeautifulSoup(response, "lxml")
            # 提取页面中需要的数据，这里简单地提取了关键词涉及包含的产品数目，还有寻找目标产品是否在搜索范围内，是则返回对应asin关键词的排名
            TotalItem = soup.select("#s-result-count")[0].text
            if page == Pages:
                csvWrite(name='kwItem&AsinRank', data=[keyword, TotalItem])
                for asin in Asin:
                    if asin in response:
                        rank = soup.find_all(attrs={"data-asin": asin})[0].attrs["data-result-rank"]
                        csvWrite(name='kwItem&AsinRank', data=[keyword, TotalItem, asin, rank])


def kwItemd(keyword, page):
    # data = {
    #     "keywords": keyword,
    #     "page": page,
    #     "rh": "i:" + Apartment + ",k:" + keyword
    # }
    # url = SITE + "/s/ref=nb_sb_noss?" + urlparse.urlencode(data)
    ts = calendar.timegm(time.gmtime())
    ts = str(ts)

    url = "https://www.amazon.cn/s?i=apparel&rh=n%3A2016156051%2Cn%3A2016157051%2Cn%3A2152155051&page="+ page +"&qid=" + ts + "&ref=sr_pg_" + page
    response = req(url)
    # time.sleep(2)
    soup = BeautifulSoup(response, "lxml")

    #rank = soup.find_all()

    #csvWrite(name='kwItem&AsinRank', data=[url, keyword])
    #print('根据class_查询节点：', soup.find_all(id='container'))

    if page == '1':
        list = soup.select('#container #mainResults ul .a-spacing-mini a.s-access-detail-page')
        # # csvWrite(name='kwItem&AsinRank', data=[url])
        # for li in list:
        #     # print(li['href'], li['title'])
        #     csvWrite(name='kwItem&AsinRank', data=[li['href'], li['title']])
    else:
        csvWrite(name='link', data=[page, url])
        list = soup.select('#a-page #search a.a-text-normal span.a-text-normal')
        for li in list:
            link = 'https://www.amazon.cn' + li.parent['href']
            # print(link, li.string)
            response = req(link)
            print('url', link)
            soup = BeautifulSoup(response, "lxml")
            start = soup.select('#a-page #dp #ppd #acrPopover span a span.a-icon-alt')
            start = start[0].string if len(start) > 0 else '无'
            commt = soup.select('#centerCol span#acrCustomerReviewText')
            commt = commt[0].string if len(commt) > 0 else '无'
            money = soup.select('#price span.priceBlockBuyingPriceString')
            money = money[0].string if len(money) > 0 else '无'
            print('stay', start, commt, money)
            csvWrite(name='boy', data=[li.string, start, commt, money, link])
            # print(li['href'], li['title'])
            # csvWrite(name='kwItem&AsinRank', data=[li['href'], li['title']])

    #print('根据class_查询节点：', soup.select('#container #mainResults ul .a-spacing-mini a.s-access-detail-page'))

from multiprocessing import Pool

def main():
    #print('Start process.')
    p = Pool(4)
    for i in KEYWORD:
        for page in range(1, Pages + 1):
            # 开启多线程时，关键词 和 页码 作为参数进行传递,需要把解析函数中控制函数运行的循环语句给去掉
            page = str(page)
            p.apply_async(kwItemd, (i, page,))
            #print('Waiting for all subprocesses done...')
    p.close()
    p.join()

if __name__ == '__main__':
    main()
