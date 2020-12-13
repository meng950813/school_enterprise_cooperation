"""
获取两个节点之间的联络路径
"""
from web.settings import RELATION
from web.utils.neo4j_operator import neo4j as neo4j


def linkTargetByOrg(agent_id, agent_label, target_id, target_label):
    """
    通过组织机构获取联络路径
    :param agent_id: str
    :param agent_label:
    :param target_id: int
    :param target_label:
    :return: [{start, target, org}] or []
    """
    cql = "match (start:{agent_label}), (target:{target_label})-[:include|employ]-(org) " \
          "where start.id='{agent_id}' and target.id={target_id} " \
          "return start, target, org".format(agent_label=agent_label, agent_id=agent_id, target_id=target_id,
                                             target_label=target_label)
    return neo4j.run(cql)


def linkEngineerByPartner(agent_id, engineer_id):
    """
    通过 地区搭档获取联络路径
    :param agent_id: str
    :param engineer_id:
    :return: [{start, target, partner}] or []
    """
    cql = "MATCH (target:Engineer)-[:employ]-(:Company)-[:locate]-(town:Town) " \
          "where target.id={engineer_id} with target, town " \
          "match (start:Agent_University)-[r:partner]-(partner:Agent_Area)-[:work]-()-[:include]-(t:Town) " \
          "where start.id='{agent_id}' and t.id=town.id " \
          "return start, partner, target".format(engineer_id=engineer_id, agent_id=agent_id)
    return neo4j.run(cql)


def linkTeacherByPartner(agent_id, teacher_id):
    """
    通过 地区搭档获取联络路径
    :param agent_id: str
    :param teacher_id:
    :return: [{start, target, partner}] or []
    """
    cql = "MATCH (target:Teacher)-[:include]-(:Institution)-[:include]-(u:University) " \
          "where target.id={teacher_id} with target, u " \
          "match (start:Agent_Area)-[r:partner]-(partner:Agent_University)-[:work]-()-[:include]-(u2:University) " \
          "where start.id='{agent_id}' and u2.id=u.id " \
          "return start, partner, target".format(teacher_id=teacher_id, agent_id=agent_id)
    return neo4j.run(cql)


def getLinkPath(agent_id, agent_label, target_id, target_label, step=3, limit=5):
    """
    获取两节点之间的联络路径
    :param agent_id: str
    :param agent_label:
    :param target_id: int
    :param target_label:
    :param step: 整型，从 源节点到目标节点 的中间结点数量
    :param limit: 整型，路径数量
    :return: list of Path
    """
    cql = "MATCH p=(start:{agent_label})-[r:knows|partner|cooperate|include|employ*..{step}]-(target:{target_label}) " \
          "where start.id='{agent_id}' and target.id={target_id} " \
          "return p as path limit {limit}" \
        .format(agent_label=agent_label, agent_id=agent_id, target_id=target_id, target_label=target_label, step=step,
                limit=limit)
    return neo4j.run(cql)


def addContactInformation(start_node, target_node, visited=0, cooperate=0, activity=0):
    """
    添加联络信息： 使用 py2neo & neo4j_operator 封装的函数
    若 该关系尚不存在 => 创建关系， 否则 => 在原有基础上改变属性值
    :return: True or False
    """
    relationship = RELATION["KNOWS"]
    relation = neo4j.search_relationship(start_node=start_node, target_node=target_node, relationship=relationship)
    if relation is None:
        return neo4j.create_relationship(start_node=start_node, target_node=target_node, relationship=relationship,
                                         visited=visited, cooperate=cooperate, activity=activity)
    else:
        return neo4j.update_one_relationship(start_node=start_node, target_node=target_node, relation=relation,
                                             cover=False, visited=visited, cooperate=cooperate, activity=activity)
