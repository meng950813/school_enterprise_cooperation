from web.settings import LABEL
from web.dao.social_network import public as public_dao


def getUserInfo(userid, area_agent=True):
    """
    根据 用户id 获取用户信息
    :param userid:
    :param area_agent: 是否为地区中介 Agent_Area or Agent_University
    :return: [{"id": 19036, "name": "清华大学"}, ...] or []
    """
    label = LABEL["areaAGENT"] if area_agent else LABEL["uniAGENT"]
    return public_dao.getUserInfo(userid=userid, label=label)


def getUsefulTowns(userid):
    """
    获取可选择区镇 ==> 有企业的区镇
    :return: [{"id": 2, "name": "开发区"}]
    """
    return public_dao.getUsefulTowns(userid=userid)


def fuzzyMatchOrg(label, name):
    """
    根据组织机构名，获取对应id
    :param label: str， c => Company, u => University, town => Town
    :param name: str, eg: 大学
    :return: {success=True or False, data=[] or [{id, name}, ...], message="xxx"}
    """
    label = transformOrg(label)
    if label is None:
        return returnResult(success=False, message="组织机构类型错误")
    if not name or 0 == len(name.strip()):
        return returnResult(success=False, message="组织机构名称不能为空")
    data = public_dao.fuzzyMatchOrg(label=label, name=name)
    return returnResult(success=True, data=data)


def fuzzyMatchTeacher(uni, name):
    """
    根据传入的专家名 & 高校， 获取其对应的专家
    :param uni: int
    :param name: str eg: "张"
    :return:  {success=True or False, data=[] or [{id, name}, ...], message="xxx"}
    """
    if not isinstance(uni, int) or uni <= 0:
        return returnResult(success=False, message="高校值不合法")
    if not isinstance(name, str) or 0 == len(name):
        return returnResult(success=False, message="专家信息错误")
    data = public_dao.fuzzyMatchTeacher(uni_id=uni, name=name)
    res = [
        {"id": item["id"], "name": "%s - %s" % (item["name"], item["institution"])}
        for item in data
    ]
    return returnResult(success=True, data=res)


def getUniversityList(limit=100):
    data = public_dao.getUniversityList(limit)
    if not data or len(data) == 0:
        # logging.error("获取高校列表失败")
        return []
    return data


def transformOrg(org):
    """
    根据传入的 组织机构类型，返回其在数据库 中对应的 label
    :param org: string 类型
    :return:
    """
    if "c" == org:
        return LABEL["COMPANY"]
    elif "town" == org:
        return LABEL["TOWN"]
    elif "u" == org:
        return LABEL["UNIVERSITY"]
    return None


def transformUser(user):
    """
    根据传入的 中介类型，返回其在图数据库 中对应的 label
    :param user: str 用户类型 :
                area ==> Agent_Area
                uni ==>  Agent_University
                teacher ==> Teacher
                engineer ==> Engineer
    :return: Agent_Area or Agent_University or Teacher or Engineer or None
    """
    if "area" == user:
        return LABEL["areaAGENT"]
    elif "uni" == user:
        return LABEL["uniAGENT"]
    elif "teacher" == user:
        return LABEL["TEACHER"]
    elif "engineer" == user:
        return LABEL["ENGINEER"]
    return None


def transformSort(sort, order):
    """
    根据传入的 排序内容 及 排序方式， 返回其对应图数据库中的 排序方式
    """
    order = "desc" if order == "desc" else "asc"
    if sort == "university":
        sort = "u_name"
    elif sort == "company":
        sort = "c_name"
    else:
        return ""
    return f" {sort} {order}, ".format(sort=sort, order=order)


def transformIPC(ipc):
    """
    将小组的ipc 归为大组
    :param ipc: B05D1/30
    :return: B05D1/00
    """
    return "%s/00" % ipc.split("/")[0]


def returnResult(success=True, data=None, message="", **kwargs):
    if not success:
        return {"success": success, "message": message, **kwargs}
    return {"success": success, "data": data, **kwargs}


def transformSimilarLabel(value, click=False):
    """
    格式化相似度
    :param value: float [0,1)
    :param click: True or False
    :return: 技术相似度： 98.90%
    """
    precent = round((1 - value) * 100, 2)
    if click:
        return "技术相似度： {p}% <br>点击查看详细对比".format(p=precent)
    else:
        return "技术相似度： {p}%".format(p=precent)
