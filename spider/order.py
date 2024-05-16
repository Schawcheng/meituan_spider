import datetime
import json
from urllib.parse import urljoin, urlencode
import requests

import config.api_urls
import config.common

import spider.mall
import tools


def get_order_total(cookie, start_date, end_date):
    mall_info = spider.mall.get_mall_info(cookie)

    if mall_info is None:
        return None

    params = {
        'region_id': mall_info['regionId'],
        'region_version': mall_info['regionVersion']
    }

    query_params = urlencode(params)

    url = urljoin(config.api_urls.ORDER, '?' + query_params)
    headers = {
        'Cookie': cookie,
        'User-Agent': config.common.USER_AGENT
    }
    data = {
        'tag': 'complete',
        'startDate': start_date,
        'endDate': end_date,
        'pageNum': 1,
        'pageSize': 10,
        'pageGray': 1
    }

    res = requests.post(url=url, headers=headers, data=data)

    if res.status_code == 200:
        content = json.loads(res.text)
        if content['code'] == 0:
            total = content['data']['totalCount']
            print(f'{start_date}-{end_date}: {total}')
            return total
        else:
            print(f'{start_date}-{end_date}: {content}')
    else:
        print(f'{start_date}-{end_date}: {res.status_code}')
    return None


def get_orders_by_date(cookie, start_date, end_date):
    total = get_order_total(cookie, start_date, end_date)

    if total is None:
        return []

    mall_info = spider.mall.get_mall_info(cookie)

    if mall_info is None:
        return []

    params = {
        'region_id': mall_info['regionId'],
        'region_version': mall_info['regionVersion']
    }

    query_params = urlencode(params)

    url = urljoin(config.api_urls.ORDER, '?' + query_params)
    headers = {
        'Cookie': cookie,
        'User-Agent': config.common.USER_AGENT
    }

    data = {
        'tag': 'complete',
        'startDate': start_date,
        'endDate': end_date,
        'pageNum': 1,
        'pageSize': 10,
        'pageGray': 1
    }

    pages = total // 10 if total % 10 == 0 else total // 10 + 1
    orders = []
    for i in range(1, pages + 1):
        data.update({'pageNum': i})

        res = requests.post(url=url, headers=headers, data=data)
        if res.status_code == 200:
            content = json.loads(res.text)
            if content['code'] == 0:
                items = content['data']['wmOrderList']
                if items is None:
                    items = []
                orders.extend(items)

    return orders


def get_orders_in_365(cookie):
    start_date = datetime.datetime.now().date() - datetime.timedelta(days=365)
    count = 365 // 5 if 365 % 5 == 0 else 365 // 5 + 1

    orders = []
    for i in range(0, count):
        start_date_str = tools.date2str(start_date)
        end_date = start_date + datetime.timedelta(days=5)
        end_date_str = tools.date2str(end_date)

        items = get_orders_by_date(cookie, start_date_str, end_date_str)

        start_date = end_date + datetime.timedelta(days=1)

        orders.extend(items)
    return orders


def get_orders_in_7(cookie):
    end_date = datetime.datetime.now().date()
    start_date = end_date - datetime.timedelta(days=6)

    start_date_str = tools.date2str(start_date)
    end_date_str = tools.date2str(end_date)

    orders = get_orders_by_date(cookie, start_date_str, end_date_str)

    return orders
