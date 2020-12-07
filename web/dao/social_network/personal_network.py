"""
获取推荐数据
"""
from web.settings import RELATION, LABEL
from web.utils.neo4j_operator import neo4j as neo4j


def getPersonalNetworkVisitedRelation(agent_id, agent_type):
    """
    获取个人中心网络中的拜访关系
    :param agent_id:
    :param agent_type: 中介类型： Agent_Area or Agent_University
    :return: [{s_id, s_name, t_id, t_name, org_id, org_name}]
    """
    if agent_type == LABEL["uniAGENT"]:
        return getVisitTeacherRelation(agent_id)
    else:
        return getVisitEngineerRelation(agent_id)


def getAgentNode(agent_id, agent_type=LABEL["uniAGENT"]):
    """
    根据 id 获取 地区/高校 技转中心中介节点基本信息
    """
    cql = "match (n:{agent}) where n.id = {id} return n.id as id, n.name as name".format(agent=agent_type, id=agent_id)
    # cql = "match (n:{agent}) where n.id = {id} return n.name as name".format(agent=agent_type, id=agent_id)
    return neo4j.run(cql)


def getVisitTeacherRelation(agent_id, limit=30):
    cql = "match (agent:{agent_label})-[r:knows]-(p:{target})-[:{rel}]-(org:{org}) where agent.id={id} " \
          "return agent.id as s_id, agent.name as s_name, p.id as t_id, p.name as t_name, " \
          "p.institution as institution, org.id as org_id, org.name as org_name, " \
          "r.activity as activity, r.cooperation as coop, r.visited as visited " \
          "order by r.update_time desc limit {limit}" \
        .format(agent_label=LABEL["uniAGENT"], target=LABEL["TEACHER"], rel=RELATION["INCLUDE"],
                org=LABEL["UNIVERSITY"], id=agent_id, limit=limit)
    return neo4j.run(cql)


def getVisitEngineerRelation(agent_id, limit=30):
    cql = "match (agent:{agent_label})-[r:knows]-(p:{target})-[:{rel}]-(org:{org}) where agent.id={id} " \
          "return agent.id as s_id, agent.name as s_name, p.id as t_id, p.name as t_name, " \
          "org.id as org_id, org.name as org_name" \
          "r.activity as activity, r.cooperation as coop, r.visited as visited " \
          "order by r.update_time desc limit {limit}" \
        .format(agent_label=LABEL["areaAGENT"], target=LABEL["ENGINEER"], rel=RELATION["EMPLOY"], org=LABEL["COMPANY"],
                id=agent_id, limit=limit)
    return neo4j.run(cql)


def getAgentPartnerRelation(agent_id, agent_type=LABEL["uniAGENT"]):
    """
    获取技转中心中介 个人中心网络中的 同事关系
    :param agent_id:
    :param agent_type: Agent_Area or Agent_University
    :return: [{t_id, t_name, org_id, org_name}]
    """
    # cql = "match (agent:{agent_label})-[p:partner]-(partner)-[:work]-(org) where agent.id={id} " \
    #       "return agent.name as s_name, agent.id as s_id, org.id as org_id, org.name as org_name, " \
    #       "partner.id as t_id,partner.name as t_name".format(agent_label=agent_type, id=agent_id)
    cql = "match (agent:{agent_label})-[p:partner]-(partner)-[:work]-(org) where agent.id={id} " \
          "return partner.id as t_id,partner.name as t_name, org.id as org_id, org.name as org_name" \
        .format(agent_label=agent_type, id=agent_id)
    return neo4j.run(cql)
