from web.service.social_network import public as public_service
from web.dao.social_network import link_path as path_dao
from web.service.social_network.recommend2Area import addLinks
from web.settings import LABEL

relation_dict = {
    "visited": "拜访 %s 次 <br>",
    "frequency": "合著专利 %s 项 <br>",
    "activity": "参与活动 %s 次 <br>",
    "cooperate": "合作 %s 次 <br>",
}

label_properties = {"id", "name", "institution", "tel"}


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
    if agent_label is None or not isinstance(agent_id, str) or len(agent_id) == 0:
        return public_service.returnResult(success=False, message="中介参数不正确")

    target_label = public_service.transformUser(user=target_type)
    if target_label is None or not isinstance(target_id, str) or len(target_id) == 0:
        return public_service.returnResult(success=False, message="目标节点参数不正确")

    if agent_label == LABEL["areaAGENT"] and target_label == LABEL["TEACHER"]:
        # 地区中介 联络 专家
        return linkTeacherByPartner(agent_id=agent_id, teacher_id=target_id)
    if agent_label == LABEL["uniAGENT"] and target_label == LABEL["ENGINEER"]:
        # 高校中介联络工程师
        return linkEngineerByPartner(agent_id=agent_id, engineer_id=target_id)

    social_path = linkTargetBySocial(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                                     target_label=target_label, max_step=max_step, limit=limit)
    if social_path is None:
        # 无法通过社交关系（如同事、朋友）等关系联系到目标 ==> 通过组织机构联系到目标
        return linkTargetByOrg(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                               target_label=target_label)
    return social_path


def linkEngineerByPartner(agent_id, engineer_id):
    """
    高校中介月用户 通过 地区搭档联络到用户
    :param agent_id: 技转中心用户id
    :param engineer_id: 目标工程师 id
    :return: {success=True or False, data={nodes, links}, message="xxx"}
    """
    # ==> [{start, target, partner}] or []
    path = path_dao.linkEngineerByPartner(agent_id=agent_id, engineer_id=engineer_id)
    if 0 == len(path):
        return public_service.returnResult(success=False, message="你在当前地区没有联络权限")
    return public_service.returnResult(success=True, data=generatePathWithPublicNode(start_node=path[0]["start"],
                                                                                     target_node=path[0]["target"],
                                                                                     agent_node=path[0]["partner"]))


def linkTeacherByPartner(agent_id, teacher_id):
    """
    地区中介 通过 高校搭档联络到用户
    :param agent_id:
    :param teacher_id:
    :return: {success=True or False, data={nodes, links}, message="xxx"}
    """
    # ==> [{start, target, partner}] or []
    path = path_dao.linkTeacherByPartner(agent_id=agent_id, teacher_id=teacher_id)
    if 0 == len(path):
        return public_service.returnResult(success=False, message="你在当前高校没有联络权限")
    return public_service.returnResult(success=True, data=generatePathWithPublicNode(start_node=path[0]["start"],
                                                                                     target_node=path[0]["target"],
                                                                                     agent_node=path[0]["partner"]))


def linkTargetByOrg(agent_id, agent_label, target_id, target_label):
    """
    通过 目标所属 学院 or 企业联络到目标的路径
    :param agent_id:
    :param agent_label:
    :param target_id:
    :param target_label:
    :return:
    """
    # ==> [{start, target, org}] or []
    path = path_dao.linkTargetByOrg(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                                    target_label=target_label)
    if 0 == len(path):
        return public_service.returnResult(success=False, message="参数错误， 无法找到节点")
    return public_service.returnResult(success=True, data=generatePathWithPublicNode(start_node=path[0]["start"],
                                                                                     target_node=path[0]["target"],
                                                                                     agent_node=path[0]["org"]))


def linkTargetBySocial(agent_id, agent_label, target_id, target_label, max_step=3, limit=5):
    """
    高校中介联络专家 or 地区中介联络工程师时， 通过社交关系获取联络路径
    :param agent_id: str
    :param agent_label: str
    :param target_id:
    :param target_label:
    :param max_step:
    :param limit:
    :return: None or {success: True or False, data: None or {...}, message: xxx}
    """
    path = path_dao.getLinkPath(agent_id=agent_id, agent_label=agent_label, target_id=target_id,
                                target_label=target_label, step=max_step, limit=limit)
    if 0 == len(path):
        return None
    else:
        return public_service.returnResult(success=True, data=formatPath2Echarts(path_list=path))


def generateSourceAndTarget(start_node, target_node):
    """
    将源节点和目标节点格式化为 Echarts 数据格式, 并设置节点属性
    :param start_node: Node
    :param target_node: Node
    :return:  nodes_dict 字典类型 ==> {node_id: node_info}
    """
    nodes_dict = dict()
    start_id = generateNode(node=start_node, nodes_dict=nodes_dict)
    target_id = generateNode(node=target_node, nodes_dict=nodes_dict)
    nodes_dict[start_id]["itemStyle"] = {"color": "#e6550d"}
    nodes_dict[target_id]["itemStyle"] = {"color": "#31a354"}
    return nodes_dict


def generatePathWithPublicNode(start_node, target_node, agent_node):
    """
    源节点 和 目标节点之间无直接联系时， 通过公共节点 （如 学院，企业等） 构建联络路径
    :param start_node: Node 类型， 源节点
    :param target_node: Node 类型， 目标节点
    :param agent_node: Node 类型， 中介节点
    :return: {nodes: [{},...], links: []}
    """
    nodes_dict = generateSourceAndTarget(start_node=start_node, target_node=target_node)
    agent_id = generateNode(node=agent_node, nodes_dict=nodes_dict)

    links = []
    for node_id in nodes_dict.keys():
        addLinks(links=links, source=node_id, target=agent_id)
    return {"nodes": [node for node in nodes_dict.values()], "links": links}


def formatPath2Echarts(path_list):
    """
    将从图数据库中获取的路径数据格式化为 Echarts 关系图 可解析的数据类型
    :param path_list: list of Path 类型 ==> [{"path": {nodes & relationships}}, ...]
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
        return {"nodes": [], "links": []}

    # dict 类型: key ==> node_id, value: node_info
    nodes_dict = generateSourceAndTarget(start_node=path_list[0]["path"].nodes[0],
                                         target_node=path_list[-1]["path"].nodes[-1])

    links = list()
    start_id, target_id = 0, 0
    for path in path_list:
        nodes, relationships = path["path"].nodes, path["path"].relationships
        for i in range(0, len(relationships)):
            start_label = str(nodes[i].labels).split(":")[1]
            target_label = str(nodes[i + 1].labels).split(":")[1]
            # 筛选掉 学院& 企业节点
            if start_label != "Institution" and start_label != "Company":
                start_id = generateNode(node=nodes[i], nodes_dict=nodes_dict)
            if target_label != "Institution" and target_label != "Company":
                target_id = generateNode(node=nodes[i + 1], nodes_dict=nodes_dict)

            if start_id != target_id:
                links.append(generateLink(source=start_id, target=target_id, relation=relationships[i]))

    return {
        "nodes": [value for value in nodes_dict.values()],
        "links": links
    }


def generateNode(node, nodes_dict={}):
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
