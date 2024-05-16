import datetime


def space_strip(s: str):
    return s.replace(' ', '')


def cookies2dict(cookie):
    cookies_list = list(map(lambda item: item.split('='), cookie.split(';')))

    cookie_dict = {item[0]: item[1] for item in cookies_list}

    return cookie_dict


def date2str(date: datetime.date):
    return date.strftime('%Y-%m-%d')


def str2date(date_str: str):
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')
