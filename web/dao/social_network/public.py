"""
获取推荐数据
"""
from web.settings import RELATION
from web.utils.neo4j_operator import neo4j as neo4j


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
