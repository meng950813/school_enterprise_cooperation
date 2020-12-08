from web.service.social_network import public as public_service
from web.dao.social_network import link_path as path_dao
from web.utils.neo4j_operator import neo4j as neo4j

relation_dict = {
    "visited": "拜访 %s 次 <br>",
    "frequency": "合著专利 %s 项 <br>",
    "activity": "参与活动 %s 次 <br>",
    "cooperate": "合作 %s 次 <br>",
}

label_properties = {"id", "name", "institution"}


def getLinkPath(agent_id=0, agent_type="area", target_id=0, target_type="engineer", max_step=3, limit=5):
    """
    获取两个节点之间的联络路径, 并格式化为 Echarts 关系图 可解析的数据格式
    :param agent_id: int 中介 id
    :param agent_type: str 中介类型 :area ==> Agent_Area or uni ==>  Agent_University
    :param target_id: int 目标节点 id
    :param target_type: str 目标节点类型类型: teacher ==> Teacher or engineer ==> Engineer
    :param max_step: int 路径最大长度
    :param limit: int 路径数量
    :return : {success: True or False, data: None or {...}, message: xxx}
    """
    agent_label = public_service.transformUser(user=agent_type)
    if (not isinstance(agent_id, int)) or agent_id < 1 or agent_type is None:
        return public_service.returnResult(success=False, message="中介参数不正确")

    target_label = public_service.transformUser(user=target_type)
    if (not isinstance(target_id, int)) or target_id < 1 or target_label is None:
        return public_service.returnResult(success=False, message="目标节点参数不正确")

    nodes = path_dao.getSourceAndTarget(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                                        target_label=target_label)
    if 0 == len(nodes):
        return public_service.returnResult(success=False, message="节点不存在")
    nodes_dict = generateSourceAndTarget(start_node=nodes[0]["start"], target_node=nodes[0]["target"])

    path = path_dao.getLinkPath(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                                target_label=target_label, step=max_step, limit=limit)

    return public_service.returnResult(success=True, data=formatPath2Echarts(path_list=path, nodes_dict=nodes_dict))


def generateSourceAndTarget(start_node, target_node):
    """
    将源节点和目标节点格式化为 Echarts 数据格式
    :param start_node: Node
    :param target_node: Node
    :return:  nodes_dict 字典类型
    """
    nodes_dict = dict()
    start = generateNode(node=start_node, nodes_dict=nodes_dict)
    target = generateNode(node=target_node, nodes_dict=nodes_dict)
    nodes_dict[start]["itemStyle"] = {"color": "#e6550d"}
    nodes_dict[target]["itemStyle"] = {"color": "#31a354"}
    return nodes_dict


def formatPath2Echarts(path_list, nodes_dict):
    """
    将从图数据库中获取的路径数据格式化为 Echarts 关系图 可解析的数据类型
    :param path_list: list of Path 类型
    :param nodes_dict: dict 类型: key ==> node_id, value: node_info
    :return :  dict {
            "nodes": [
                {id, name, ....}, ...
            ],
            "links": [
                {"source": id1, "target": id2, value: xxx}, ...
            ]
        }
    """
    if 0 == len(path_list):
        return {"nodes": [value for value in nodes_dict.values()], "links": []}

    links = list()
    for path in path_list:
        nodes, relationships = path["path"].nodes, path["path"].relationships
        for i in range(0, len(relationships)):
            start_id = generateNode(node=nodes[i], nodes_dict=nodes_dict)
            target_id = generateNode(node=nodes[i + 1], nodes_dict=nodes_dict)
            links.append(generateLink(relation=relationships[i], source=start_id, target=target_id))

    return {
        "nodes": [value for value in nodes_dict.values()],
        "links": links
    }


def generateNode(node, nodes_dict):
    """
    将节点数据从 Node 类型转变为 dict 类型， 并添加到 node_dict 字典中
    :param node:  Node 类型
    :param nodes_dict:  dict 类型,
    :return: node_id, 整型
    """
    node_id = str(node.identity)
    if node_id not in nodes_dict:
        node_info = dict()
        # label_properties == > {"id", "name", "institution"}
        for key in label_properties:
            if node[key] is not None:
                node_info[key] = node[key]

        if "id" in node_info:
            node_info["node_id"] = node_info["id"]
        node_info["id"] = node_id
        node_info["node_label"] = str(node.labels).lower().split(":")[1]

        nodes_dict[node_id] = node_info
    return node_id


def generateLink(relation, source, target):
    """
    根据 relationship 类型生成Echarts适配的关系格式， 主要生成 悬浮窗的内容
    :param relation: Relationship 类型 ==>
    :param source: 节点id
    :param target: 目标节点id
    :return: dict {
            source: 123,
            target: 234,
            label: "悬浮框描述文本"
        }
    """
    label = ""
    # TODO 未获取到关系中的属性
    for key, value in dict(relation).items():
        if key in relation_dict and value > 0:
            label += relation_dict[key] % value
    return {
        "source": source,
        "target": target,
        "label": label
    }


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

    res = path_dao.addContactInformation(start_node=start_node, target_node=target_node, visited=visited,
                                         cooperate=cooperate, activity=activity)
    if res is False:
        return public_service.returnResult(success=False, message="创建/更新关系操作失败")
    return public_service.returnResult(success=True, message="操作成功")
