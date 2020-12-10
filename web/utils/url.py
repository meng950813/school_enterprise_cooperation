import re
from flask import request, redirect, url_for, current_app
from urllib.parse import urlparse, urljoin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature


TELEPHONE = re.compile(r"^1[3|4|5|6|7|8]\d{9}$")
PASSWORD = re.compile(r"(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{8,}")


def is_safe_url(target):
    """
    确保内部的URL才是安全的
    :param target:
    :return:
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='main.index', **kwargs):
    """
    重定向
    :param default:
    :param kwargs:
    :return:
    """
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(expire_in=None, **kwargs):
    """
    生成令牌
    :param expire_in: 过期时间，默认为1小时
    :param kwargs:
    :return: 返回令牌
    """
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)
    data = {}
    data.update(**kwargs)
    return s.dumps(data)


def get_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
        return data
    except (SignatureExpired, BadSignature) as e:
        return None


