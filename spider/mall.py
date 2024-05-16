import json
import requests

import config.api_urls
import config.common


def get_mall_region_info(url, headers):
    res = requests.get(url=url, headers=headers)
    if res.status_code == 200:
        content = json.loads(res.text)
        if content['code'] == 0:
            # fields: ignoreSetRouterProxy regionVersion, womPoiId, regionId
            region_info = content['data']
            return region_info
    return None


def get_mall_info(cookie):
    url = config.api_urls.MALL_INFO
    headers = {
        'Cookie': cookie,
        'User-Agent': config.common.USER_AGENT
    }
    res = requests.get(url=url, headers=headers)

    if res.status_code == 200:
        content = json.loads(res.text)
        if content['code'] == 0:
            mall_info = content['data']
            return mall_info

    return None


def get_mall_hui_fu_lv(url, headers, data):
    res = requests.post(url=url, headers=headers, data=data)

    if res.status_code == 200:
        content = json.loads(res.text)
        if content['code'] == 0:
            hui_fu_lv = content['data']['title']
            return hui_fu_lv

    return None


if __name__ == '__main__':
    print(get_mall_info(config.common.TEST_COOKIE))