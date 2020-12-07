import os
from config import MYSQL_PRODUCTION_URI, SQLALCHEMY_BINDS

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    # wtform库用于CSRF
    SECRET_KEY = os.getenv('SECRET_KEY', "secret key")


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

# 中介（孵化器）类型
AGENT_PATTERN = ["官办官营", "官办民营", "民办民营"]

# 中介（孵化器）等级
AGENT_LEVEL = ["", "国家级", "省级", "市级", "县级"]

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
    "CSM": "CSM"  # 专家团队与工程师团队的 相似性预测关系
}

LABEL = {
    "CITY": "City",
    "TOWN": "Town",
    "UNIVERSITY": "University",
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
