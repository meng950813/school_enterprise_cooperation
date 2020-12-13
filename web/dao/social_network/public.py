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
          "return town.id as id, town.name as name" \
        .format(areaAgent=LABEL["areaAGENT"], uniAgent=LABEL["uniAGENT"], userid=userid)
    return neo4j.run(cql)


def fuzzyMatchOrg(label, name):
    """
    根据组织机构名，获取对应id
    :param label:
    :param name:
    :return:[] or [{id:123, name: xxx}, .... ]
    """
    cql = """match (node:{label}) where node.name=~".*{name}.*" """ \
          """return node.id as id, node.name as name limit 5""".format(label=label, name=name)
    return neo4j.run(cql)


def fuzzyMatchTeacher(uni_id, name):
    """
    根据教师名， 模糊匹配
    :param uni_id: int
    :param name:
    :return:
    """
    cql = """match (u:{uni})-[:include]-(i:{inst})-[:include]-(t:{teacher})""" \
          """where u.id={uni_id} and t.name=~".*{name}.*" """ \
          """return t.id as id, t.name as name, i.name as institution limit 5""" \
        .format(uni=LABEL["UNIVERSITY"], inst=LABEL["INSTITUTION"], teacher=LABEL["TEACHER"], uni_id=uni_id, name=name)
    return neo4j.run(cql)


def fuzzyMatchEngineer(com_id, name):
    """
    根据工程师名 & 企业id, 模糊匹配
    :param com_id: int
    :param name:
    :return:
    """
    cql = """match (c:{com})-[:employ]-(e:{engineer})""" \
          """where c.id={com_id} and e.name=~".*{name}.*" """ \
          """return e.id as id, e.name as name limit 5""" \
        .format(com=LABEL["COMPANY"], engineer=LABEL["ENGINEER"], com_id=com_id, name=name)
    return neo4j.run(cql)


def getUniversityList(limit=100):
    cql = "match (u:University) where u.teachers > 0 return u.id as id, u.name as name  " \
          "order by u.teachers desc limit {limit}".format(limit=limit)
    return neo4j.run(cql)
