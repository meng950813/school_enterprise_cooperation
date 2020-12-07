from web.service.social_network import public as public_service
from web.dao.social_network import recommend_detail as detail_dao
import logging
import math


def recommendDetail(eid=None, tid=None, team=1):
    """

    """
    if eid is None or tid is None:
        # TODO
        return {}

    engineer_info = detail_dao.getTeamBasicInfo(_id=eid, teacher=False)
    teacher_info = detail_dao.getTeamBasicInfo(_id=tid, teacher=True)

    # patents ==> [] or [{code, name, date}]
    engineer_patents = detail_dao.getSimilarPatents(team_teacher=tid, team_engineer=eid, teacher=False)
    teacher_patents = detail_dao.getSimilarPatents(team_teacher=tid, team_engineer=eid, teacher=True)

    # field ==> [{"industry_e": "xxx", "industry_t": "xxxxx"}] or []
    field = detail_dao.getTeamField(eid=eid, tid=tid)
    field = {"industry_e": "", "industry_t": ""} if len(field) == 0 else field[0]

    return {
        "engineer": formatDetailInfo(engineer_info, engineer_patents, field=field["industry_e"]),
        "teacher": formatDetailInfo(teacher_info, teacher_patents, field=field["industry_t"]),
    }


def formatDetailInfo(data, patents, field=""):
    result = {"org": "", "name": "", "members": "", "field": "", "institution": "", "patents": []}
    if len(data) > 0:
        result = data[0]
    result["patents"] = patents
    result["field"] = field
    return result


def getTeamMembers(team_t, team_e):
    teacher_team = detail_dao.getTeamMembers(team_id=team_t, teacher=True)
    engineer_team = detail_dao.getTeamMembers(team_id=team_e, teacher=False)

    return {
        "teacher": formatTeamGraph(teacher_team, prefix="t", team=team_t, category=0),
        "engineer": formatTeamGraph(engineer_team, prefix="e", team=team_e, category=1),
    }


def technicalFieldComparison(eid=None, tid=None, team=1):
    """
    获取技术领域对比数据
    :return:
    {
        success: True or False,
        data:{
            "xAxis": ["ipc1", "ipc2", ..., "ipcn"],
            "eData": [n,n-1, ..., 1],
            "tData": [1,2,..., n]
        },
        message: xxx
    }
    """
    if eid is None or tid is None:
        return public_service.returnResult(success=False, message="参数有误，e_id=%s, t_id=%s" % (eid, tid))
    # data = detail_dao.getTechnicalFieldComparison(eid=eid, tid=tid, team=True if team == 1 else False)
    # data = transformTechnicalFieldComparisonData(data=data)
    teacher_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=tid, teacher=True)
    engineer_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=eid, teacher=False)

    data = formatTechnicalFieldComparisonData(teacher=transformIPC(teacher_patent), engineer=transformIPC(engineer_patent))
    # if data is None:
    #     return public_service.returnResult(success=False, message="从图数据库获取数据格式不正确")
    return public_service.returnResult(success=True, data=data)


def formatTeamGraph(team_data, prefix="t", team=0, category=0):
    """
    将从图数据库中获取的数据，格式化为 echarts 可解析的格式
    :team_data: [{id1, name1, count, id2, name2}, ...]
    """
    nodes, links = list(), list()
    nodes_set = set()
    for item in team_data:
        source = "%s_%s" % (prefix, item["id1"])
        target = "%s_%s" % (prefix, item["id2"])
        if source not in nodes_set:
            nodes_set.add(source)
            nodes.append(
                generateNode(id=item["id1"], key=source, name=item["name1"], value=item["patent1"], category=category,
                             team=team))
        if target not in nodes_set:
            nodes_set.add(target)
            nodes.append(
                generateNode(id=item["id2"], key=target, name=item["name2"], value=item["patent2"], category=category,
                             team=team))

        links.append({
            "source": source,
            "target": target,
            "value": int(item["count"])
        })
    return {"nodes": nodes, "links": links}


def generateNode(id, key, name, value, category, team):
    node = {
        "id": key,
        "name": name,
        "value": value,
        "symbolSize": computeSymbolSize(value),
        "category": category,
    }

    if int(id) == team:
        # node["label"] = {"normal": {"show": True}}
        node["itemStyle"] = {
            "borderType": 'solid',
            "borderWidth": 2,
            "borderColor": "#e6550d"
        }
    return node


def computeSymbolSize(patent_count):
    return 12 + math.log(int(patent_count), 2) * 4


def transformIPC(patent_distribute):
    """
    将ipc 小组的数量统一转化为 大组的数量
    TODO 问题在于：一个专利若有同一个大组的n个ipc分组关系，转换后会，当前大组下回被当作有n个专利
    eg：一个专利的ipc分类： a0/01,a01/02,... ==> {"a01/01": 1, "a01/02": 1} ==> {"a01/00": 2}

    :patent_distribute: list of dict ==> [{"ipc": "xxx", "count": 1}, ....]
    :return: {"xxx/00": 4, "yyy/00": 5, ...}
    """
    res = dict()
    for item in patent_distribute:
        ipc = public_service.transformIPC(item["ipc"])
        if ipc not in res:
            res[ipc] = 0
        res[ipc] += item["count"]

    return res


def formatTechnicalFieldComparisonData(teacher, engineer):
    """
     将从数据库中获取的 同类专利数据，格式化为前端可处理的格式
    :param teacher: 专家团队专利数据， dict类型 eg: {"A012350/00": 2, "A012351/00": 3, ...}
    :param engineer: 工程师团队专利数据， dict类型 eg: {"A012350/00": 2, "A012351/00": 3, ...}
    :return: dict 类型， 展示对比图需要的横纵坐标数据： 横坐标：ipc序列， 纵坐标： 工程师 & 专家 与 ipc 对应的 专利数量
        eg： {
            "xAxis": ["ipc1", "ipc2", ..., "ipcn"],
            "eData": [n,n-1, ..., 1],
            "tData": [1,2,..., n]
        }
    """
    res = {"xAxis": [], "eData": [], "tData": []}
    if not teacher or not engineer:
        return res

    e_patent, t_patent = dict(), dict()
    for ipc, count in engineer.items():
        if ipc not in teacher:
            continue
        e_patent[ipc], t_patent[ipc] = count, teacher[ipc]

    # 按照工程师专利数量逆序排序 ==> [(ipc, count),(),....]
    temp = sorted(e_patent.items(), key=lambda kv: kv[1], reverse=True)
    res["xAxis"] = [ipc[0] for ipc in temp]
    res["eData"] = [e_patent[ipc] for ipc in res["xAxis"]]
    res["tData"] = [t_patent[ipc] for ipc in res["xAxis"]]

    return res


def transformTechnicalFieldComparisonData(data):
    """
    将从数据库中获取的 同类专利数据，格式化为前端可处理的格式
    :param data: list of dict类型 eg: [{"e_patent": 123, "t_patent": 234, "ipc": "ABDC50/01"}, ...]
    :return: dict 类型， 展示对比图需要的横纵坐标数据： 横坐标：ipc序列， 纵坐标： 工程师 & 专家 与 ipc 对应的 专利数量
        eg： {
            "xAxis": ["ipc1", "ipc2", ..., "ipcn"],
            "eData": [n,n-1, ..., 1],
            "tData": [1,2,..., n]
        }
    """
    if not data:
        return {"xAxis": [], "eData": [], "tData": []}

    ipc_dict = dict()
    for item in data:
        # ipc = item["ipc"]
        ipc = public_service.transformIPC(item["ipc"])
        if ipc not in ipc_dict:
            ipc_dict[ipc] = {"e": set(), "t": set()}
        ipc_dict[ipc]["e"].add(item["e_patent"])
        ipc_dict[ipc]["t"].add(item["t_patent"])

    # 统计企业在每个ipc下的专利数量， 用于排序
    patent_count = {ipc: len(value["e"]) for ipc, value in ipc_dict.items()}

    # 根据企业专利数量对 ipc 进行排序 ==> [(ipc, count), ...]
    patent_count = sorted(patent_count.items(), key=lambda x: x[1], reverse=True)

    # 取前 10 项
    # patent_count = patent_count[:10]

    xAxis = [item[0] for item in patent_count]
    eData = [item[1] for item in patent_count]
    tData = [len(ipc_dict[item[0]]["t"]) for item in patent_count]

    return {
        "xAxis": xAxis,
        "eData": eData,
        "tData": tData
    }
