import datetime
import json
import time

from urllib.parse import urlencode, urljoin
import requests

import tools
import config.common
import config.api_urls


def get_comments_total(cookie, begin_time, end_time, comment_type):
    cookie_trim = tools.space_strip(cookie)
    cookie_dict = tools.cookies2dict(cookie_trim)

    params = {
        'ignoreSetRouterProxy': 'true',
        'acctId': cookie_dict['acctId'],
        'wmPoiId': cookie_dict['wmPoiId'],
        'token': cookie_dict['token'],
        'appType': 3,

        # 0=>全部 1=>好评 2=>中评 3=>差评
        'commScore': comment_type,
        'commType': -1,
        'hasContent': -1,
        'periodType': 1,
        'beginTime': begin_time,
        'endTime': end_time,
        'pageNum': 1,
        'onlyAuditNotPass': 0,
        'pageSize': 10,
        'source': 1,
    }

    headers = {
        'Cookie': cookie,
        'User-Agent': config.common.USER_AGENT
    }
    query_params = urlencode(params)
    url = urljoin(config.api_urls.COMMENT, '?' + query_params)

    res = requests.get(url=url, headers=headers)

    if res.status_code == 200:
        content = json.loads(res.text)
        if content['code'] == 0:
            total = content['data']['total']
            print(f"{begin_time}-{end_time}: {total}")
            return total
        else:
            print(f"{begin_time}-{end_time}: {content}")
    return None


def get_comments_in_180(cookie, comment_type):
    begin_time = str(int(datetime.datetime.timestamp(datetime.datetime.now() - datetime.timedelta(days=180))))
    end_time = str(int(time.time()))

    total = get_comments_total(cookie, begin_time, end_time, comment_type)

    if total is None:
        return []

    pages = total // 10 if total % 10 == 0 else total // 10 + 1

    cookie_trim = tools.space_strip(cookie)
    cookie_dict = tools.cookies2dict(cookie_trim)

    params = {
        'ignoreSetRouterProxy': 'true',
        'acctId': cookie_dict['acctId'],
        'wmPoiId': cookie_dict['wmPoiId'],
        'token': cookie_dict['token'],
        'appType': 3,

        # 0=>全部 1=>好评 2=>中评 3=>差评
        'commScore': comment_type,
        'commType': -1,
        'hasContent': -1,
        'periodType': 1,
        'beginTime': begin_time,
        'endTime': end_time,
        'pageNum': 1,
        'onlyAuditNotPass': 0,
        'pageSize': 10,
        'source': 1,
    }

    headers = {
        'Cookie': cookie,
        'User-Agent': config.common.USER_AGENT
    }

    comments = []
    for i in range(1, pages + 1):
        params.update({'pageNum': i})
        query_params = urlencode(params)
        url = urljoin(config.api_urls.COMMENT, '?' + query_params)

        res = requests.get(url=url, headers=headers)

        if res.status_code == 200:
            content = json.loads(res.text)
            if content['code'] == 0:
                items = content['data']['list']
                comments.extend(items)
    return comments


if __name__ == '__main__':
    print(get_comments_in_180(config.common.TEST_COOKIE, 3))
