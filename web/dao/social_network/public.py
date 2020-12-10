"""
获取推荐数据
"""
from web.settings import RELATION, LABEL
from web.utils.neo4j_operator import neo4j as neo4j


def getUserInfo(userid, label=LABEL["areaAGENT"]):
    """
    根据 用户id 获取用户信息
    :param userid: int or str
    :param label: Agent_Area or Agent_University
    :return: [{"id": 19036, "name": "清华大学"}, ...] or []
    """
    cql = "match (agent:{label})-[:work]-()-[:include]-(org) " \
          "where agent.id='{userid}' " \
          "return org.id as id, org.name as name".format(label=label, userid=userid)
    return neo4j.run(cql)


def getUsefulTowns(userid):
    """
    获取可选择区镇
    :return: [{"id": 2, "name": "开发区"}]
    """
    cql = "match (uniAgent:{uniAgent})-[:partner]-(areaAgent:{areaAgent})-[:work]-()-[:include]-(t:Town) " \
          "where uniAgent.id='{userid}' " \
          "with distinct(t) as town " \
          "return town.id as id, town.name as name"\
        .format(areaAgent=LABEL["areaAGENT"], uniAgent=LABEL["uniAGENT"], userid=userid)
    return neo4j.run(cql)


def getOrgId(label, name):
    """
    根据组织机构名，获取对应id
    :param label:
    :param name:
    :return:[] or [{id:123, name: xxx}, .... ]
    """
    cql = """match (node:{label}) where node.name=~".*{name}.*" """ \
          """return node.id as id, node.name as name limit 5""".format(label=label, name=name)
    return neo4j.run(cql)


def getUniversityList(limit=100):
    cql = "match (u:University) where u.teachers > 0 return u.id as id, u.name as name  " \
          "order by u.teachers desc limit {limit}".format(limit=limit)
    return neo4j.run(cql)
