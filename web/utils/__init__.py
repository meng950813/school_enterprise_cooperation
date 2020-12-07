import time
from datetime import datetime


def timestamp2text(timestamp):
    """时间戳转换成字符串, 类似mysql的from_unixtime操作"""
    obj = time.localtime(timestamp)
    text = time.strftime('%Y-%m-%d %H:%M:%S', obj)
    return text


def timestamp2day(timestamp):
    """
    时间戳转化成字符串 年月日
    :param timestamp:
    :return:
    """
    obj = time.localtime(timestamp)
    text = time.strftime('%Y-%m-%d', obj)
    return text


def timestamp2month(timestamp):
    """
    时间戳转化成字符串 月
    :param timestamp:
    :return:
    """
    obj = time.localtime(timestamp)
    text = time.strftime('%m', obj)
    return text


def timestamp2year(timestamp):
    """
    时间戳转化成字符串 年
    :param timestamp:
    :return:
    """
    obj = time.localtime(timestamp)
    text = time.strftime('%Y', obj)
    return text


def text2timestamp(text):
    obj = time.strptime(text, '%Y-%m-%d %H:%M:%S')
    timestamp = time.mktime(obj)
    return timestamp


def date2timestamp(text):
    obj = time.strptime(text, '%Y-%m-%d')
    timestamp = time.mktime(obj)
    return timestamp


def yearStart2timestamp(next_year=0):
    """
    获取据今年next_year年的 第一天的时间戳
    eg: 今年2020年，
        next_year=0，则返回 2020-01-01 的时间戳
        next_year=1，则返回 2021-01-01 的时间戳
        next_year=-1，则返回 2019-01-01 的时间戳
    """
    cur_year = datetime.now().year + next_year
    return int(date2timestamp("%s-01-01" % cur_year))


def min_max(count, min_count, max_count):
    """确定最小值和最大值"""
    min_count = count if min_count > count else min_count
    max_count = count if max_count < count else max_count
    return min_count, max_count
