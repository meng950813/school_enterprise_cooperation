from web.service.social_network import public as public_service
from web.dao.social_network import recommend_detail as detail_dao
from datetime import datetime
import math, time


# 团队对比
def compareTeacherAndEngineerTeam(eid=None, tid=None):
    """

    :param eid:
    :param tid:
    :return:
    """
    engineer_info = detail_dao.getEngineerTeamBasicInfo(e_id=eid)
    teacher_info = detail_dao.getTeacherTeamBasicInfo(t_id=tid)

    # patents ==> [] or [{code, name, date}]
    engineer_patents = detail_dao.getSimilarPatents(team_teacher=tid, team_engineer=eid, teacher=False)
    teacher_patents = detail_dao.getSimilarPatents(team_teacher=tid, team_engineer=eid, teacher=True)

    print(len(teacher_patents))
    tp = {p["code"] for p in teacher_patents}
    print(len(tp))

    # team_e_patentNum ==> [] or [{nums:xxx}]
    team_e_patentNum = detail_dao.getTeamPatentsNumber(team_id=eid, teacher=False)
    team_t_patentNum = detail_dao.getTeamPatentsNumber(team_id=tid, teacher=True)

    # field ==> [{"industry_e": "xxx", "industry_t": "xxxxx"}] or []
    field = detail_dao.getTeamField(eid=eid, tid=tid)
    field = {"industry_e": "", "industry_t": ""} if len(field) == 0 else field[0]

    engineer = formatDetailInfo(data=engineer_info, team_patent=team_e_patentNum, patents_list=engineer_patents,
                                field=field["industry_e"])
    teacher = formatDetailInfo(data=teacher_info, team_patent=team_t_patentNum, patents_list=teacher_patents,
                               field=field["industry_t"])

    return {"engineer": engineer, "teacher": teacher}


def formatDetailInfo(data, team_patent, patents_list, field=""):
    """
    将基本信息、团队专利总量、专利列表以及团队涉及行业 整合到一个字典中
    :param data: 团队基本信息，格式为 [{}] or []，工程师团队包括 工程师名， 团队人数，企业名； 专家团队包括 专家名、学校、学院、团队人数
    :param team_patent: 团队专利总数，[{"team_patent": xxx}]
    :param patents_list: 专利列表， [] or [{code, name, date}]
    :param field:
    :return:
    """
    now = int(time.time())
    result = {"org": "", "name": "", "members": "", "field": "", "institution": "", "team_patent": "",
              "patents_list": []}
    if len(data) > 0:
        result = data[0]

    for patent in patents_list:
        if patent["authorization_date"] is not None:
            patent["authorization_date"] = int((now - patent["authorization_date"]) / (60 * 60 * 24 * 365))
        else:
            patent["authorization_date"] = 0

    result["patents_list"] = patents_list
    result["team_patent"] = 0 if len(team_patent) == 0 else team_patent[0]["nums"]
    result["field"] = field
    return result


# 团队关系相关
def getTeamMembers(team_t, team_e):
    teacher_team = detail_dao.getTeamMembers(team_id=team_t, teacher=True)
    engineer_team = detail_dao.getTeamMembers(team_id=team_e, teacher=False)

    return {
        "teacher": formatTeamGraph(teacher_team, prefix="t", team=team_t, category=0),
        "engineer": formatTeamGraph(engineer_team, prefix="e", team=team_e, category=1),
    }


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

    # ==> [{ipc:xxx, patent:xxx}, ...]结果中包含重复数据，需要去重
    teacher_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=tid, teacher=True)
    engineer_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=eid, teacher=False)

    data = formatTechnicalFieldComparisonData(teacher=countIPCDistribute(IPC_patent=teacher_patent, merge=True),
                                              engineer=countIPCDistribute(IPC_patent=engineer_patent, merge=True))

    # if data is None:
    #     return public_service.returnResult(success=False, message="从图数据库获取数据格式不正确")
    return public_service.returnResult(success=True, data=data)


def countIPCDistribute(IPC_patent, merge=False):
    """
    将从数据库中获取到的，具有重复数据的 专利-ipc 对应关系数据重新统计，获取每个ipc对应的专利的数量
    :param IPC_patent: [{ipc:xxx, patent:xxx}, ...]结果中包含重复数据，需要去重
    :param merge: True or False, 是否将 IPC 归于大组
    :return: {"a01/01": 1, "a01/02": 1} ==> {"a01/00": 2}
    """
    count = dict()
    res = dict()
    for item in IPC_patent:
        ipc = item["ipc"]
        if ipc not in count:
            count[ipc] = set()
        count[ipc].add(item["patent"])

    for ipc, patent_set in count.items():
        ipc = ipc if not merge else public_service.transformIPC(ipc)
        if ipc not in res:
            res[ipc] = 0
        res[ipc] += len(patent_set)
    return res


def formatTechnicalFieldComparisonData(teacher, engineer):
    """
     将从数据库中获取的 同类专利数据，格式化为柱状图可渲染的格式
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


# 雷达图相关
def technicalFieldComparisonForRadar(eid=None, tid=None):
    """
        获取技术领域对比数据
        :return:
        {
            success: True or False,
            data:{
                "indicator": [
                    {"name": '销售（sales）', "max": 6500},
                    {"name": '管理（Administration）', "max": 16000},
                ],
               "t_value": [4300, 10000, 28000, 35000, 50000, 19000],
               "e_value": [5000, 14000, 28000, 31000, 42000, 21000],
            },
            message: xxx
        }
        """
    if eid is None or tid is None:
        return public_service.returnResult(success=False, message="参数有误，e_id=%s, t_id=%s" % (eid, tid))

    # ==> [{ipc:xxx, patent:xxx}, ...]结果中包含重复数据，需要去重
    teacher_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=tid, teacher=True)
    engineer_patent = detail_dao.getTeamTechnicalFieldDistribute(team_id=eid, teacher=False)

    data = formatFieldComparisonDataForRadar(teacher=formatIPC_PatentRelation(teacher_patent),
                                             engineer=formatIPC_PatentRelation(engineer_patent))
    # if data is None:
    #     return public_service.returnResult(success=False, message="从图数据库获取数据格式不正确")
    return public_service.returnResult(success=True, data=data)


def formatIPC_PatentRelation(ipc_patent):
    """
    将  [{ipc:xxx, patent:xxx}, ...] 类型数据格式化为 {ipc: {p1,p2,...}, ...} 格式
    :param ipc_patent: 从图数据库中获取的 专利与 ipc对应关系，list of dict类型 eg: [{ipc:xxx, patent:xxx}, ...]结果中包含重复数据，需要去重
    :return:  {ipc: {p1,p2,...}, ...}
    """
    res = {}
    for item in ipc_patent:
        ipc, patent = item["ipc"], item["patent"]
        if ipc not in res:
            res[ipc] = set()
        res[ipc].add(patent)
    return res


def formatFieldComparisonDataForRadar(teacher, engineer):
    """
    将专家/工程师的专利-ipc对应数量的数据格式化为 雷达图需要的格式
    :param teacher: 专家团队专利数据，dict类型 {ipc: {p1,p2,...}, ...}
    :param engineer: 工程师团队专利数据，dict类型 {ipc: {p1,p2,...}, ...}
    :return: 渲染雷达图所需数据, eg:
         {
            "indicator": [
                {"name": '销售（sales）', "max": 6500},
                {"name": '管理（Administration）', "max": 16000},
            ],
           "t_value": [4300, 10000, 28000, 35000, 50000, 19000],
           "e_value": [5000, 14000, 28000, 31000, 42000, 21000],
        }
    """
    ipc_set = set(teacher.keys())
    for key in engineer.keys():
        ipc_set.add(key)
    # [] or [{code: xxxx, title: xxx, ipc: xx}, ...]
    industry_ipc = detail_dao.getIndustryIPC(ipc_set)
    industry_title, ipc_industry = formatIPC_Industry(industry_ipc)

    # ==> {code： {p1, p2, ...}}
    industry_teacher_patent = countIndustryPatent(ipc_industry=ipc_industry, ipc_patent=teacher)
    industry_engineer_patent = countIndustryPatent(ipc_industry=ipc_industry, ipc_patent=engineer)
    # 取交集
    industry = getIndustryIntersection(industry_t_patent=industry_teacher_patent,
                                       industry_e_patent=industry_engineer_patent)

    indicator, t_value, e_value = list(), list(), list()

    # max_len = 0
    # for code in industry:
    #     t_num = len(industry_teacher_patent[code])
    #     e_num = len(industry_engineer_patent[code])
    #     max_len = max(max_len, max(math.ceil(t_num / 10) * 10, math.ceil(e_num / 10) * 10))
    for code in industry:
        t_num = len(industry_teacher_patent[code])
        e_num = len(industry_engineer_patent[code])
        indicator.append({
            "name": industry_title[code],
            "max": max(math.ceil(t_num / 10) * 10, math.ceil(e_num / 10) * 10)
            # "max": max_len
        })
        t_value.append(t_num)
        e_value.append(e_num)
    return {"indicator": indicator, "t_value": t_value, "e_value": e_value}


def formatIPC_Industry(industry_ipc):
    """
    将 [{code: xxxx, title: xxx, ipc: xx}, ...] 数据格式化为 {code: title} & {ipc: {code, ...}} 格式
    :param industry_ipc: [{code: xxxx, title: xxx, ipc: xx}, ...]
    :return: tuple of dict:  {code: title} , {code: {ipc, ...}}
    """
    industry_title, ipc_industry = {}, {}
    for item in industry_ipc:
        industry_title[item["code"]] = item["title"]
        if item["ipc"] not in ipc_industry:
            ipc_industry[item["ipc"]] = set()
        ipc_industry[item["ipc"]].add(item["code"])
    return industry_title, ipc_industry


def countIndustryPatent(ipc_industry, ipc_patent):
    """
    根据 ipc-patent 的数量关系 与 ipc-industry 对应关系， 统计 industry-patent的数量关系
    :param ipc_industry: ipc-industry 对应关系: {ipc: set{industry_code, ...}}
    :param ipc_patent:  ipc-patent的数量关系, dict 类型: {ipc: {p1,p2,...}, ...}
    :return: dict类型，{industry_code: {p1, p2, ...}, ....}
    """
    industry_patent = {}
    for ipc, patent in ipc_patent.items():
        if ipc not in ipc_industry:
            continue
        for industry in ipc_industry[ipc]:
            if industry not in industry_patent:
                industry_patent[industry] = set()
            # patent => {p1,p2,...}
            for p in patent:
                industry_patent[industry].add(p)

    return industry_patent
    # return {industry: len(patents) for industry, patents in industry_patent.items()}


def getIndustryIntersection(industry_t_patent, industry_e_patent, limit=6):
    """
    取两个团队的行业交集，并根据 limit 获取前几项
    :param industry_t_patent: 专家 行业与专利的关系 {industry_code: {p1, p2, ...}, ....}
    :param industry_e_patent: 工程师 行业与专利的关系 {industry_code: {p1, p2, ...}, ....}
    :param limit: 交集的数量， 默认为6
    :return: set 类型： {} or {code, ....}
    """
    # 取交集 ==> set()
    # industry = industry_t_patent.keys() & industry_e_patent.keys()
    # common_industry = dict()
    # for code in industry:
    #     common_industry[code] = min(industry_t_patent[code], industry_t_patent[code])
    # res = sorted(common_industry.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    # return {item[0] for item in res}

    total = dict()  # ==> {industry_code: 123, ....}
    for code, pt in industry_t_patent.items():
        num2 = 0 if code not in industry_e_patent else len(industry_e_patent[code])
        total[code] = len(pt) + num2
    res = sorted(total.items(), key=lambda kv: kv[1], reverse=True)[:limit]
    return {item[0] for item in res}


# 河流图相关
def chartsRiver(teamId=None, teacher=True):
    """
    获取某个团队的河流图数据
    :param teamId: 团队id ,
    :param teacher: 是否是专家团队，布尔型。
    :return: {
        success: True or False, message: xx,
        data: {
            legend: [ipc1, ipc2, ...]
            data: [["2020/1/1", "xx行业" or "IPC"， 123]， 。。。]
        }
    }
    """
    # ==> [{ipc:xxx, patent:xxx, date: 1429142400}, ...]结果中包含重复数据，需要去重
    ipc_patent_time = detail_dao.getTeamTechnicalFieldDistribute(team_id=teamId, teacher=teacher)

    ipc_patent = formatIPC_PatentRelation(ipc_patent_time)  # {ipc: {p1,p2,...}, ...}\
    # ==> {year: {patent,...}} & {patent: year, ...}
    year_patent, patent_year = formatYear_PatentRelation(ipc_patent_time)

    # ==> [{code: xxxx, title: xxx, ipc: xx}, ...]
    industry_ipc = detail_dao.getIndustryIPC(ipc_patent.keys())
    industry_title, ipc_industry = formatIPC_Industry(industry_ipc)

    # 统计每个行业下专利的数量 ==> {industry_code: {p1, p2, ...}, ...}
    industry_patent = countIndustryPatent(ipc_industry, ipc_patent)

    # 取涉及专利最多的 6 个行业 ==> {code1, code2, ...}
    tmp = sorted(industry_patent.items(), key=lambda kv: len(kv[1]), reverse=True)[:5]
    industry = {item[0] for item in tmp}

    legend = [industry_title[code] for code in industry]

    # ==> {2020: {industry1: 123, industry2: 345,...}, ...}
    time_industry = dict()
    max_year, min_year = max(year_patent.keys()), min(year_patent.keys())
    for year in range(min_year, max_year + 1):
        if year not in time_industry:
            time_industry[year] = dict()
        industry_year = time_industry[year]

        for code in industry:
            patents = industry_patent[code]
            for patent in patents:
                if year == patent_year[patent]:
                    if code not in industry_year:
                        industry_year[code] = 1
                    else:
                        industry_year[code] += 1

    res = list()
    for year, industry_dict in time_industry.items():
        for code in industry:
            num = 0 if code not in industry_dict else industry_dict[code]
            title = industry_title[code]
            res.append([str(year + 1), num, title])

    return public_service.returnResult(success=True, data={
        "legend": legend,
        "data": res
    })


def formatYear_PatentRelation(ipc_patent_time):
    """
    将[{ipc:xxx, patent:xxx, date: 1429142400}, ...]数据 格式化为 {year: {patent,...}} & {patent: year, ...}格式
    :param ipc_patent_time: 
    :return:  {year: {patent,...}} & {patent: year, ...}
    """
    year_patent, patent_year = dict(), dict()
    for item in ipc_patent_time:
        # ipc, patent, year = public_service.transformIPC(item["ipc"]),item["patent"],getYearFromTimestamp(item["date"])
        patent, year = item["patent"], getYearFromTimestamp(item["date"])
        if year not in year_patent:
            year_patent[year] = set()
        year_patent[year].add(patent)
        patent_year[patent] = year
    return year_patent, patent_year


def formatPatent_IPCRelation(ipc_patent_time):
    """
    将[{ipc:xxx, patent:xxx, date: 1429142400}, ...]数据 格式化为 {patnet: {ipc,...}} 格式
    :param ipc_patent_time: 
    :return: 
    """
    patent_ipc = dict()
    for item in ipc_patent_time:
        ipc, patent = item["ipc"], item["patent"]
        if patent not in patent_ipc:
            patent_ipc[patent] = set()
        patent_ipc[patent].add(ipc)
    return patent_ipc


def getYearFromTimestamp(timestamp):
    """
    返回时间戳所代表的时间年份
    :param timestamp: 整型时间戳
    :return: 2015
    """
    return datetime.fromtimestamp(int(timestamp)).year


# 词云相关
def wordCloud(teamId, teacher=True):
    """
    根据团队id & 团队类型获取团队涉及行业的词云
    :param teamId: 团队id ,
    :param teacher: 是否是专家团队，布尔型。
    :return: {
        success: True or False, message: xx,
        data: [
            {
                name: xxx,
                value: 123
            }, ...
        ]
    }
    """
    # ==> [{ipc:xxx, patent:xxx, date: 1429142400}, ...]结果中包含重复数据，需要去重
    ipc_patent_time = detail_dao.getTeamTechnicalFieldDistribute(team_id=teamId, teacher=teacher)

    ipc_patent = formatIPC_PatentRelation(ipc_patent_time)  # {ipc: {p1,p2,...}, ...}\
    # ==> [{code: xxxx, title: xxx, ipc: xx}, ...]
    industry_ipc = detail_dao.getIndustryIPC(ipc_patent.keys())
    industry_title, ipc_industry = formatIPC_Industry(industry_ipc)

    # 统计每个行业下专利的数量 ==> {industry_code: {p1, p2, ...}, ...}
    industry_patent = countIndustryPatent(ipc_industry, ipc_patent)
    # ==> [["农药制造", 110], ....]
    res = [{"name": industry_title[code], "value": len(patents)} for code, patents in industry_patent.items()]
    return public_service.returnResult(success=True, data=res)


if __name__ == '__main__':
    data = chartsRiver(teamId=5993157, teacher=True)
    print(data)
    data = chartsRiver(teamId=8886, teacher=False)
    print(data)
