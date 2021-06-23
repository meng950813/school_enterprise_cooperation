import os

from config import MYSQL_PRODUCTION_URI

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    # wtform库用于CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', "secret key")

    # KeyCloak设置项
    OIDC_CLIENT_SECRETS = 'client_secrets.json'
    OIDC_ID_TOKEN_COOKIE_SECURE = False
    OIDC_REQUIRE_VERIFIED_EMAIL = False
    OIDC_USER_INFO_ENABLED = True
    OIDC_OPENID_REALM = 'kunshan'
    OIDC_SCOPES = ['openid']
    OIDC_INTROSPECTION_AUTH_METHOD = 'client_secret_post'


class DevelopmentConfig(BaseConfig):
    """开发环境配置"""
    SQLALCHEMY_DATABASE_URI = MYSQL_PRODUCTION_URI
    port = 8080


class TestingConfig(BaseConfig):
    """测试环境配置"""
    TESTING = True
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """生产环境配置"""
    pass


configuration = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig
}

RELATION = {
    "WRITE": "write",
    "INCLUDE": "include",
    "EMPLOY": "employ",
    "HANDLE": "handle",
    "MANAGE": "manage",
    "LOCATE": "locate",
    "COOPERATE": "cooperate",
    "KNOWS": "knows",  # 中介与专家/工程师的关系
    "PARTNER": "partner",  # 高校中介和地区中介的合作关系
    "INVOLVE": "involve",  # 专家/工程师（团队）所涉及的技术领域 （IPC）
    "PSM": "PSM",  # 专家个人与工程师个人的 相似性预测关系
    "CSM": "CSM",  # 专家团队与工程师团队的 相似性预测关系
    "CUSM": "CUSM",  # 企业-高效 的相似性，可用于解决 带哪些企业去哪些学校的问题
    "CISM": "CISM",  # 企业-学院 的相似性，可用于解决 带哪些企业去哪些学院的问题
    "CT": "CT",  # 企业-专家团队的相似性，
    "CT2": "CT2",  # 企业-专家团队的相似性，
    "CTT": "CTT",  # 企业-专家团队、考虑时间因素的相似性，
    "CTT3": "CTT3",  # 企业-专家团队、考虑时间因素的相似性，
    "CTTW2": "CTTW2",  # 企业-专家团队、考虑时间因素的相似性，
}

LABEL = {
    "CITY": "City",
    "TOWN": "Town",
    "UNIVERSITY": "University",
    "INSTITUTION": "Institution",
    "TEACHER": "Teacher",
    "COMPANY": "Company",
    "ENGINEER": "Engineer",
    "PATENT": "Patent",
    "IPC": "IPC",
    "TTC": "TechnologyTransferCenter",  # 高校技术转移中心
    "TTP": "TechnologyTransferPlatform",  # 地区技术转移平台
    "areaAGENT": "Agent_Area",  # 地区技术转移中心的中介用户
    "uniAGENT": "Agent_University",  # 高校技术转移中心的中介用户
}
