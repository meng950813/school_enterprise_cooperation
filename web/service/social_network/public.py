from web.settings import LABEL


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
