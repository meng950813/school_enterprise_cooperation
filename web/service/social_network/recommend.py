from web.service.social_network import public as public_service
from web.dao.social_network import recommend as recommend_dao
import logging


def recommendUniversityAndCompany(town_id=None, uni_id=None, limit=20, filter_company=""):
    """
    针对给定的地区和高校，推荐适合与高校合作的企业
    :param town_id: int 区镇id, 若 town_id==0 表示全部区镇
    :param uni_id: String, eg: "123,456,345"
    :param limit:
    :param filter_company: String, 需要排除在外的企业id, 字符串类型，以英文逗号分割, eg: "123,4432,5,2354"
    :return:
    """

    if town_id is None or town_id < 0:
        return public_service.returnResult(success=False, message="区镇选择不正确")
    if not uni_id or 0 == len(uni_id):
        return public_service.returnResult(success=False, message="高校不能为空")

    try:
        filter_list = []
        if filter_company and len(filter_company) > 0:
            filter_list = [int(com_id) for com_id in filter_company.split(",")]

        university_id = [int(u_id) for u_id in uni_id.split(",")]
    except BaseException as e:
        logging.error(e)
        return public_service.returnResult(success=False, message="传入参数格式不正确")


def recommendTeacherForArea(area_id=None, uni_id=None, team=True, skip=0, limit=20, sort="", order="desc"):
    """
    向地区推荐适合于 某一高校合作的企业及对应团队
    :param area_id:
    :param uni_id: String, eg: "123,456,345"
    :param team: 是够团队
    :param skip: 偏移量
    :param limit: 一次获取的数据量
    :param sort: 用于排序的字段, 目前只根据 企业名 及 高校名 排序
    :param order: 排序方式 asc or desc
    :return:
    """
    if not area_id:
        return public_service.returnResult(success=False, message="找不到地区")
    if not uni_id or len(uni_id) == 0:
        return public_service.returnResult(success=False, message="找不到高校")
    try:
        uni_id_list = [int(uid) for uid in uni_id.split(",")]
    except BaseException as e:
        logging.error(e)
        return public_service.returnResult(success=False, message="参数格式不正确")

    sort = public_service.transformSort(sort, order)
    data = recommend_dao.recommendTeacherForArea(area_id=area_id, university_id=uni_id_list, team=team, sort=sort,
                                                 skip=skip, limit=limit)
    total = recommend_dao.totalRecommendTeacherForArea(area_id=area_id, university_id=uni_id_list, team=team)
    total = 0 if len(total) == 0 else total[0]["total"]
    return public_service.returnResult(success=True, data=data, total=total, offset=skip, limit=limit, team=team)


def recommendTeacherForCompany(company_id, university_id, team=True, limit=20):
    """
     向企业推荐适合于 某一高校合作的企业及对应团队
    :param company_id: str类型，以 “,” 作为 分隔符， eg: "123，234，456"
    :param university_id: String, eg: "123,456,345"
    :param team: 是否团队
    :param limit: 一次获取的数据量
    :return:
    """
    if not company_id or len(company_id) == 0:
        return public_service.returnResult(success=False, message="企业不能为空")
    if not university_id or len(university_id) == 0:
        return public_service.returnResult(success=False, message="高校不能为空")
    try:
        company_id = [int(com_id) for com_id in company_id.split(",")]
        university_id = [int(uni_id) for uni_id in university_id.split(",")]
    except BaseException as e:
        logging.error(e)
        return public_service.returnResult(success=False, message="传入参数格式不正确")

    data = recommend_dao.recommendTeacherForCompany(company_id=company_id, university_id=university_id, limit=limit,
                                                    team=team)

    return formatResultOfRecommendTeacherForCompany(data=data, team=team)


def formatResultOfRecommendTeacherForCompany(data, team):
    """
    将从图数据库中获取的数据格式化为前端可处理的数据格式
    """
    if 0 == len(data):
        return public_service.returnResult(success=False, message="未查询到数据")

    nodes_com, nodes_engineer, nodes_teacher, nodes_uni = list(), list(), list(), list()
    links = []
    set_node = set()
    category_list, category_map = list(), dict()
    for record in data:
        com_id = "c_%s" % record["c_id"]
        e_id = "e_%s" % record["e_id"]
        t_id = "t_%s" % record["t_id"]
        u_id = "u_%s" % record["u_id"]

        # 添加企业节点
        index_category = addCategory(category_list=category_list, category_map=category_map, node_id=record["c_id"],
                                     name=record["c_name"])
        addNode(node_set=set_node, node_container=nodes_com, node_id=com_id, category=index_category,
                label=record["c_name"])
        # 添加工程师节点
        addNode(node_set=set_node, node_container=nodes_engineer, node_id=e_id, category=index_category,
                label=record["e_name"])
        # 添加工程师与企业的关系
        addLinks(links=links, source=com_id, target=e_id, category=index_category)

        # 添加高校节点
        index_category = addCategory(category_list=category_list, category_map=category_map, node_id=record["u_id"],
                                     name=record["u_name"])
        addNode(node_set=set_node, node_container=nodes_uni, node_id=u_id, category=index_category,
                label=record["u_name"])
        # 添加专家节点
        addNode(node_set=set_node, node_container=nodes_teacher, node_id=t_id, category=index_category,
                label=record["t_name"])

        # 添加专家和高校的关系
        addLinks(links=links, source=u_id, target=t_id, category=index_category)

        # 添加工程师与专家的技术领域相似关系
        isTeam = "团队" if team else ""
        similar = '%.2f' % ((1 - record["weight"]) * 100) + "%"
        weight = "{engineer}{team} - {teacher}{team} " \
                 "<br> 技术相似度：{similar} ".format(engineer=record["e_name"], team=isTeam, teacher=record["t_name"],
                                                similar=similar, category=index_category)
        addLinks(links=links, source=e_id, target=t_id, weight=weight)

    result = {"com": nodes_com, "engineer": nodes_engineer, "teacher": nodes_teacher, "uni": nodes_uni}
    return public_service.returnResult(success=True, data={"nodes": result, "links": links, "category": category_list})


def addNode(node_set, node_container, node_id, **properties):
    """
    将 节点数据 格式化为 Echarts node 类型数据
    :param node_set: set 类型， 保存已格式化为 node 节点的 node_id,
    :param node_container: list of dict, 引用类型， [{id, name, symbolSize, ....}, ....]
    :param node_id: 节点id ==> 源于 图数据库中的 节点id, 此数据唯一
    :param properties: 节点除 id, name 之外的其他属性
    :return:
    """
    if node_id in node_set:
        return None
    node_set.add(node_id)
    # params = {"name": node_id, "symbolSize": 30}
    params = {"name": node_id}
    for key, v in properties.items():
        params[key] = v
    return node_container.append(params)


def addLinks(links, source, target, **properties):
    """
    添加节点关系
    :param links: list of dict, 引用类型，
    :param source: 节点 id
    :param target: 节点id
    :param properties: 关系的属性
    :return:
    """
    link = {
        "source": source,
        "target": target
    }
    for key, v in properties.items():
        link[key] = v
    return links.append(link)


def addCategory(category_list, category_map, node_id, name):
    """
    根据 node_id 和 category_name 获取每个节点的 category值， 若当前category_name不存在， 添加到 category_list 数组中
    :param category_list: list of dict, 保存 category_list ==> [{name:xxx}, ...]
    :param category_map: dict, 保存 每个 node 在 category_list 中对应的 category 的下标
    :param node_id: int 节点id
    :param name: category_name
    :return: 返回当前category 在数组中的下标
    """
    if node_id not in category_map:
        category_list.append({"name": name})
        category_map[node_id] = len(category_list) - 1
    return category_map[node_id]
