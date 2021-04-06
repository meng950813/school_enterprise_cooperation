from web.service.social_network import public as public_service
from web.dao.social_network import recommend2Area as recommend2Area_dao


def recommendResult(town_id=None, com_id="", uni_id="", limit=20):
    """
    根据传入参数的不同组合，调用不同的处理部分， 返回统一格式的推荐结果
    :param town_id: 区镇id, str类型，
    :param com_id: 企业id, str类型，多个企业id之间以 , 分割， eg:”123,234,345“
    :param uni_id: 高校id, str类型，多个id之间以 , 分割， eg:”321,453,465“
    :param limit:
    :return: {
        success: True or False
        data: {
            # 此处使用二维数组存储 nodes, len(nodes) 表示共有多少列节点， len(nodes[i]) 表示 第 i 列有多少节点
            nodes:[[{node prop}], [...], ...]
            links: [{source: xx, target:xxx, others: xxx}, ...]
            category: [{name: xxx}]
        }
    }
    """
    if not isinstance(town_id, str) or 0 == len(town_id):
        return public_service.returnResult(success=False, message="区镇值不正确")

    towns = [int(t_id) for t_id in town_id.split(",")]

    if not isinstance(com_id, str) or 0 == len(com_id):  # 未传入 企业参数 或 参数格式不正确
        if not isinstance(uni_id, str) or 0 == len(uni_id):  # 未传入高校参数 或 参数格式不正确
            # ==> 只输入区镇信息， 为特定区域内的企业 推荐 适合合作的高校
            return recommendUniversityAndCompany(town_id=towns, limit=limit)
        else:  # 传入高校参数
            # ==> 指定地区和高校，推荐适合与当地企业合作的高校
            uni_id_list = [int(u_id) for u_id in uni_id.split(",")]
            return recommendInstitutionAndCompany(town_id=towns, uni_id=uni_id_list, limit=limit)
    else:  # 输入企业
        comps = [int(c_id) for c_id in com_id.split(",")]
        if not isinstance(uni_id, str) or 0 == len(uni_id):  # 未传入高校参数 或 参数格式不正确
            # ==> 推荐与特定企业相匹配的高校专家团队
            # return recommendInstitutionForCompany(com_id=comps, limit=limit)
            return recommendEngineerAndTeacherTeam2(com_id=comps, limit=limit)
        else:
            # ==> 推荐企业工程师和高校专家
            uni_id_list = [int(u_id) for u_id in uni_id.split(",")]
            return recommendEngineerAndTeacherTeam(com_id=comps, uni_id=uni_id_list, limit=limit)


def recommendUniversityAndCompany(town_id=None, reverse=True, limit=20):
    """
    为特定区域内的企业 推荐 适合合作的高校
    :param town_id: 整型
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :param limit:
    :return:
    """
    records = recommend2Area_dao.recommendUniversityAndCompany(town_id=town_id, limit=limit)
    return public_service.returnResult(success=True,
                                       data=formatRecommendUniversityAndCompany(records=records, reverse=reverse))


def formatRecommendUniversityAndCompany(records, reverse=True):
    """
    将 高校和企业的推荐结果 格式化
    :param records: [{town_id, town_name, c_id, c_name, u_id, u_name, weight}, ...]
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :return: {nodes, links, category}
    """
    nodes_town, nodes_com, nodes_uni = list(), list(), list()
    links = list()
    node_set = set()
    category_list, category_map = list(), dict()

    if 0 == len(records):
        return {"nodes": [], "links": links, "category": category_list}

    for record in records:
        town_id, com_id = "town_%s" % record["town_id"], "c_%s" % record["c_id"]
        uni_id = "u_%s" % record["u_id"]
        # 以区镇名 作为category
        category_index = addCategory(category_list, category_map, node_id=record["town_id"], name=record["town_name"])
        addNode(node_set, nodes_town, node_id=town_id, category=category_index, label=record["town_name"])  # 添加区镇节点
        addNode(node_set, nodes_com, node_id=com_id, category=category_index, label=record["c_name"])  # 添加企业节点
        addLinks(links=links, source=town_id, target=com_id, category=category_index)  # 添加区镇与企业的关系

        # 以学校名 作为 category
        category_index = addCategory(category_list, category_map, node_id=record["u_id"], name=record["u_name"])
        addNode(node_set, nodes_uni, node_id=uni_id, category=category_index, label=record["u_name"])  # 添加高校节点

        addLinks(links=links, source=com_id, target=uni_id,
                 label=public_service.transformSimilarLabel(record["weight"]))
        # addLinks(links=links, source=com_id, target=uni_id, click=True, label=transformSimilarLabel(record["weight"]))
    if reverse:
        nodes = [nodes_town, nodes_com, [], nodes_uni]
    else:
        nodes = [nodes_uni, [], nodes_com, nodes_town]
    return {"nodes": nodes, "links": links, "category": category_list}


def recommendEngineerAndTeacherTeam(com_id, uni_id, reverse=True, limit=20):
    """
    制定 高校 & 企业 推荐 专家团队 & 工程师团队
    :param com_id: list, [] or [123,435...]
    :param uni_id: list [] or [345, 5435,...]
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :param limit: 一次获取的数据量
    :return:
    """
    records = recommend2Area_dao.recommendEngineerAndTeacherTeam(company_id=com_id, uni_id=uni_id, limit=limit)
    return public_service.returnResult(success=True,
                                       data=formatRecommendEngineerAndTeacher(records=records, reverse=reverse))


def recommendEngineerAndTeacherTeam2(com_id, reverse=True, limit=20):
    """
    制定 高校 & 企业 推荐 专家团队 & 工程师团队
    :param com_id: list, [] or [123,435...]
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :param limit: 一次获取的数据量
    :return:
    """
    records = recommend2Area_dao.recommendEngineerAndTeacherTeam2(com_id=com_id, limit=limit)
    return public_service.returnResult(success=True,
                                       data=formatRecommendEngineerAndTeacher(records=records, reverse=reverse))


def formatRecommendEngineerAndTeacher(records, reverse=True):
    """
    将 工程师团队和专家团队的推荐结果  格式化为前端可处理的数据格式
    :param records: [{c_id, c_name, e_id, e_name, t_id, t_name, i_id, i_name, u_id, u_name, weight)}]
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :return: {nodes, links, category}
    """
    nodes_com, nodes_engineer, nodes_teacher, nodes_institution, nodes_uni = list(), list(), list(), list(), list()
    links = []
    node_set = set()
    category_list, category_map = list(), dict()

    if 0 == len(records):
        return {"nodes": [], "links": links, "category": category_list}

    for record in records:
        com_id, e_id = "c_%s" % record["c_id"], "e_%s" % record["e_id"]
        t_id, i_id, u_id = "t_%s" % record["t_id"], "i_%s" % record["i_id"], "u_%s" % record["u_id"]
        category_index = addCategory(category_list, category_map, node_id=record["c_id"], name=record["c_name"])
        addNode(node_set, nodes_com, node_id=com_id, category=category_index, label=record["c_name"])  # 添加企业节点
        addNode(node_set, nodes_engineer, node_id=e_id, category=category_index, label=record["e_name"])  # 添加工程师节点
        addLinks(links=links, source=com_id, target=e_id, category=category_index)  # 添加工程师与企业的关系

        category_index = addCategory(category_list, category_map, node_id=record["u_id"], name=record["u_name"])
        addNode(node_set, nodes_uni, node_id=u_id, category=category_index, label=record["u_name"])  # 添加学校节点
        addNode(node_set, nodes_institution, node_id=i_id, category=category_index, label=record["i_name"],
                uni=record["u_name"])  # 添加学院节点
        addNode(node_set, nodes_teacher, node_id=t_id, category=category_index, label=record["t_name"])  # 添加专家节点

        addLinks(links=links, source=u_id, target=i_id, category=category_index)  # 添加学校和学院的关系
        addLinks(links=links, source=i_id, target=t_id, category=category_index)  # 添加学院和专家的关系
        # 添加相似关系
        addLinks(links=links, source=e_id, target=t_id, click=True,
                 label=public_service.transformSimilarLabel(record["weight"], click=True))

    if reverse:
        nodes = [nodes_com, nodes_engineer, [], nodes_teacher, nodes_institution, nodes_uni]
    else:
        nodes = [nodes_uni, nodes_institution, nodes_teacher, [], nodes_engineer, nodes_com]

    return {"nodes": nodes, "links": links, "category": category_list}


def recommendInstitutionAndCompany(town_id, uni_id, reverse=True, limit=20):
    """
    根据选定区域的id、 以及选定高校的id, 推荐地区企业 和 高校学院
    :param town_id:list [2,3,4...]
    :param uni_id:
    :param reverse: True or False, 地区排列 与 高校排列 的顺序
    :param limit:
    :return:
    """
    records = recommend2Area_dao.recommendInstitutionAndCompany(town_id=town_id, uni_id=uni_id, limit=limit)
    return public_service.returnResult(success=True,
                                       data=formatRecommendInstitutionAndCompany(records, reverse=reverse))


def formatRecommendInstitutionAndCompany(records, reverse=True):
    """
    将 企业和特定学校的的推荐结果 格式化为前端可处理的数据格式
    :param records: [{town_id, town_name, c_id, c_name, i_id, i_name, u_id, u_name, weight)}]
    :param reverse: True:地区排列 + 高校排列 , False: 高校排列 + 地区排列
    :return: {nodes, links, category}
    """
    nodes_town, nodes_com, nodes_institution, nodes_uni = list(), list(), list(), list()
    links = list()
    node_set = set()
    category_list, category_map = list(), dict()

    if 0 == len(records):
        return {"nodes": [], "links": links, "category": category_list}

    for record in records:
        town_id, com_id = "town_%s" % record["town_id"], "c_%s" % record["c_id"]
        i_id, uni_id = "i_%s" % record["i_id"], "u_%s" % record["u_id"]
        # 以区镇名 作为category
        category_index = addCategory(category_list, category_map, node_id=record["town_id"], name=record["town_name"])
        addNode(node_set, nodes_town, node_id=town_id, category=category_index, label=record["town_name"])  # 添加区镇节点
        addNode(node_set, nodes_com, node_id=com_id, category=category_index, label=record["c_name"])  # 添加企业节点
        addLinks(links=links, source=town_id, target=com_id, category=category_index)  # 添加区镇与企业的关系

        # 以学校名 作为 category
        category_index = addCategory(category_list, category_map, node_id=record["u_id"], name=record["u_name"])
        addNode(node_set, nodes_uni, node_id=uni_id, category=category_index, label=record["u_name"])  # 添加高校节点
        addNode(node_set, nodes_institution, node_id=i_id, category=category_index, label=record["i_name"],
                uni=record["u_name"])  # 添加学院节点
        addLinks(links=links, source=uni_id, target=i_id, category=category_index)  # 添加学校和学院的关系

        addLinks(links=links, source=com_id, target=i_id,
                 label=public_service.transformSimilarLabel(record["weight"]))  # 添加相似关系

    if reverse:
        nodes = [nodes_town, nodes_com, [], nodes_institution, nodes_uni]
    else:
        nodes = [nodes_uni, nodes_institution, [], nodes_com, nodes_town]
    return {"nodes": nodes, "links": links, "category": category_list}


def recommendInstitutionForCompany(com_id, limit=20):
    """
    根据企业id， 为特定企业推荐 高校学院
    :param com_id: list [2,3,4...]
    :param limit:
    :return:
    """
    records = recommend2Area_dao.recommendInstitutionForCompany(company_id=com_id, limit=limit)
    return public_service.returnResult(success=True, data=formatRecommendInstitutionAndCompany(records))


def addNode(node_set, node_container, node_id, **properties):
    """
    将 节点数据 格式化为 Echarts node 类型数据
    :param node_set: set 类型， 保存已格式化为 node 节点的 node_id,
    :param node_container: list of dict, 引用类型， [{id, name, symbolSize, ....}, ....]
    :param node_id: 节点id ==> 源于 图数据库中的 节点id, 此数据唯一, eg: u_123
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
