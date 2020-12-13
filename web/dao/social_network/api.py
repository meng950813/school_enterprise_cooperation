"""
修改用户信息的api
包括： 修改联系情况
"""
from web.settings import RELATION
from web.utils.neo4j_operator import neo4j as neo4j


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
