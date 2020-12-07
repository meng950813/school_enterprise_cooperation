from web.service.social_network import public as public_service
from web.dao.social_network import personal_network as personal_dao
import logging


def getPersonalNetwork(agent_id, agent_type=0):
    """
    获取中介的个人中心网络
    :param agent_id:
    :param agent_type: 中介类型： area ==> Agent_Area or uni ==>  Agent_University
    :return: [{s_id, s_name, t_id, t_name, org_id, org_name}]
    """
    agent_type = public_service.transformUser(user=agent_type)
    if (not isinstance(agent_id, int)) or agent_id <= 0 or agent_type is None:
        return public_service.returnResult(success=False, message="参数不正确")

    agent = personal_dao.getAgentNode(agent_id=agent_id, agent_type=agent_type)
    if not agent or 0 == len(agent):
        return public_service.returnResult(success=False, message="id有误, 查无此人")

    work_network = personal_dao.getAgentPartnerRelation(agent_id=agent_id, agent_type=agent_type)
    visit_network = personal_dao.getPersonalNetworkVisitedRelation(agent_id=agent_id, agent_type=agent_type)

    data = formatPersonalNetworkData(agent=agent[0], work_relation=work_network, visit_relation=visit_network)
    return public_service.returnResult(success=True, data=data)


def formatPersonalNetworkData(agent, work_relation, visit_relation):
    """
    将 拜访关系和 同事 关系格式化为 前端可渲染的数据格式
    :param agent: dict: {id, name}
    :param work_relation: list of dict: [{t_id, t_name, org_id, org_name, institution, activity, coop, visited}, ...]
    :param visit_relation: list of dict: [{t_id, t_name, org_id, org_name, institution, activity, coop, visited}, ...]
    :return {
                name: "中介节点",
                value: "xx",
                list: [
                    {
                        name: "org节点",
                        value: "xxx",
                        list: [
                            {
                                name: "个人",
                                value: "xxxx",
                                // list:[],
                            }, ...
                        ]
                    }, ...
                ]
            }
    """
    agent["id"] = "a" + str(agent["id"])
    agent["list"] = divideOrg(work_relation, index=0)
    agent["list"].extend(divideOrg(visit_relation, index=1000000))
    return agent


def divideOrg(relation, index=0):
    """
    根据工作关系或同事关系，统计出所属组织分布
    :return : [
        {
            name: "",
            value: "",
            list: [
                {name, value, label, ...}
            ]
        }
    ]
    """
    org_list, org_index = list(), dict()
    for item in relation:
        index += 1
        leave_node = {
            "id": str(index),
            "node_id": item["t_id"],
            "name": item["t_name"],
            "V": 0 if not item.get("visited") else item["visited"],
            "A": 0 if not item.get("activity") else item["activity"],
            "C": 0 if not item.get("coop") else item["coop"]

        }
        if not item.get("institution"):
            item["institution"] = ""
            key = item["org_name"]
        else:
            key = item["org_name"] + "-" + item["institution"]
        if key not in org_index:
            index += 1
            org_info = {
                "id": str(index),
                "node_id": item["org_id"],
                "name": key,
                "list": list()
            }
            org_list.append(org_info)
            org_index[key] = len(org_list) - 1

        org_list[org_index[key]]["list"].append(leave_node)
    return org_list
