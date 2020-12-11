"""
面向高校中介的 推荐功能，主要包括
    input   =>  output
2.  university + town       =>  company & institution           ==> recommend2Area.recommendInstitutionAndCompany
3.  university + company    =>  engineer_team & teacher_team    ==> recommend2Area.recommendEngineerAndTeacher
4.  teacher + town          =>  company & teacher               ==> TODO
5.  teacher + company       =>  engineer_team & teacher         ==> TODO
"""
from web.service.social_network import public as public_service
from web.service.social_network import recommend2Area as recommend2Area_service
from web.dao.social_network import recommend2University as recommend2University_dao


def recommendResult(uni_id="", teacher_id=None, town_id=None, com_id="", limit=20):
    """
    根据传入参数的不同组合，调用不同的处理部分， 返回统一格式的推荐结果
    :param uni_id: 高校id, str eg: "123,2343"
    :param teacher_id: 专家id, str, eg: "3224,3435"
    :param town_id: 区镇id, str, eg: "324,435"
    :param com_id: 企业id, str类型，多个企业id之间以 , 分割， eg:”123,234,345“
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
    if not isinstance(uni_id, str) or 0 == len(uni_id):
        return public_service.returnResult(success=False, message="高校值不正确")
    if not isinstance(town_id, str) or 0 == len(town_id):
        return public_service.returnResult(success=False, message="区镇值不正确")

    towns = [int(t_id) for t_id in town_id.split(",")]
    unis = [int(u_id) for u_id in uni_id.split(",")]

    if isinstance(com_id, str) and 0 < len(com_id) and isinstance(teacher_id, str) and 0 < len(teacher_id):
        # 指定企业 & 专家
        # ==> 推荐 专家个人和 工程师团队
        comps = [int(c_id) for c_id in com_id.split(",")]
        teachers = [int(t_id) for t_id in teacher_id.split(",")]
        return recommendEngineerAndTeacher(com_id=comps, uni_id=unis, teacher_id=teachers, limit=limit)

    elif isinstance(com_id, str) and 0 < len(com_id):
        # 指定高校 & 企业
        # ==> 推荐企业工程师和高校专家
        comps = [int(c_id) for c_id in com_id.split(",")]
        return recommend2Area_service.recommendEngineerAndTeacherTeam(com_id=comps, uni_id=unis, reverse=False,
                                                                      limit=limit)

    elif isinstance(teacher_id, str) and 0 < len(teacher_id):
        # 指定 专家 & 地区
        # ===> 推荐 适合与专家合作的企业
        # TODO
        return public_service.returnResult(success=False, message="未获取到数据")
    else:
        # 指定高校 & 地区
        # ==> 推荐适合与当地企业合作的高校
        return recommend2Area_service.recommendInstitutionAndCompany(town_id=towns, uni_id=unis, reverse=False,
                                                                     limit=limit)


def recommendEngineerAndTeacher(com_id, uni_id, teacher_id, limit=20):
    """
    指定企业 & 专家，推荐 专家和 工程师团队
    :param com_id: list [12,34,3]
    :param uni_id: list [23,543]
    :param teacher_id: [234,453, 435]
    :param limit:
    :return:
    """
    records = recommend2University_dao.recommendEngineerAndTeacher(com_id=com_id, uni_id=uni_id, teacher_id=teacher_id,
                                                                   limit=limit)
    return public_service.returnResult(success=True,
                                       data=recommend2Area_service.formatRecommendEngineerAndTeacher(records=records,
                                                                                                     reverse=False))


def recommendCompanyAndTeacher(town_id, teacher_id, limit):
    """
    TODO
    指定 专家 & 地区 ===> 推荐 适合与专家合作的企业
    :param town_id:
    :param teacher_id:
    :param limit:
    :return:
    """
