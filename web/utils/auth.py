from flask import redirect, url_for, g
from base64 import b64decode
# from web.extensions import oidc
import json


def getUserId():
    """
    获取用户 在图数据库中的 id, 一般为其手机号
    :return: str
    """
    return g.oidc_id_token['preferred_username']


def isUniversityAgent():
    """
    判断当前用户是否为高校技转中心中介
    :return:  True or False
    """
    return require_role("KETD", "技转中心")


def isAreaAgent():
    """
    判断当前用户是否为 地区中介用户
    :return: True or False
    """
    return require_role("KETD", "孵化器")


def require_role(client, role):
    """
    判断当前用户是否拥有特定角色
    :param client:
    :param role:
    :return: True or False
    """
    # try:
    #     pre, tkn, post = oidc.get_access_token().split('.')
    # except Exception as e:
    #     print(e)
    #     oidc.logout()
    #     # TODO 此处应重定向到登陆页面
    #     return redirect(url_for('index.index'))
    # missing_padding = 4 - len(tkn) % 4
    # tkn += '=' * missing_padding
    # access_token = json.loads(b64decode(tkn, altchars='-_'))
    # return role in access_token['resource_access'][client]['roles']
