from web.service.social_network import public as public_service
from web.dao.social_network import api as api_dao
from web.utils.neo4j_operator import neo4j as neo4j


def addContactInformation(agent_id=0, agent_type="area", target_id=0, target_type="engineer", visited=0, cooperate=0,
                          activity=0):
    """
    创建/更新 中介与 专家/工程师之间的关系
    :param agent_id: int 中介 id
    :param agent_type: str 中介类型 :area ==> Agent_Area or uni ==>  Agent_University
    :param target_id: int 目标节点 id
    :param target_type: str 目标节点类型类型: teacher ==> Teacher or engineer ==> Engineer
    :param visited: int 拜访次数
    :param cooperate: int 合作次数
    :param activity: int 参与活动次数
    :return : dict {success: True or False, message: xxx}
    """
    agent_label = public_service.transformUser(user=agent_type)
    if (not isinstance(agent_id, int)) or agent_id < 1 or agent_type is None:
        return public_service.returnResult(success=False, message="中介参数不正确")

    target_label = public_service.transformUser(user=target_type)
    if (not isinstance(target_id, int)) or target_id < 1 or target_label is None:
        return public_service.returnResult(success=False, message="目标节点参数不正确")

    start_node = neo4j.search_node(search_dict={"label": agent_label, "search": {"id": agent_id}})
    if start_node is None:
        return public_service.returnResult(success=False, message="源点信息有误")

    target_node = neo4j.search_node({"label": target_label, "search": {"id": target_id}})
    if target_node is None:
        return public_service.returnResult(success=False, message="目标节点信息有误")

    res = api_dao.addContactInformation(start_node=start_node, target_node=target_node, visited=visited,
                                        cooperate=cooperate, activity=activity)
    if res is False:
        return public_service.returnResult(success=False, message="创建/更新关系操作失败")
    return public_service.returnResult(success=True, message="操作成功")
