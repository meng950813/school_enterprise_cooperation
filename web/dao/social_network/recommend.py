"""
获取推荐数据
"""
from web.settings import RELATION
from web.utils.neo4j_operator import neo4j as neo4j


def getOrgId(label, name):
    """
    根据组织机构名，获取对应id
    :param label:
    :param name:
    :return:[] or [{id:123, name: xxx}, .... ]
    """
    cql = """match (node:{label}) where node.name=~".*{name}.*" """ \
          """return node.id as id, node.name as name limit 5""".format(label=label, name=name)
    return neo4j.run(cql)


def getUniversityList(limit=100):
    cql = "match (u:University) where u.teachers > 0 return u.id as id, u.name as name  " \
          "order by u.teachers desc limit {limit}".format(limit=limit)
    return neo4j.run(cql)


def recommendTeacherForCompany(company_id, university_id, team=True, skip=0, limit=20):
    """
    向 企业推荐适合合作的 高校老师
    :param company_id: list : [12, 23, 34, ...] or []
    :param university_id: list : [23, ..] or []
    :param team: 是否以团队为单位
    :param skip:
    :param limit: 限制数量
    :return: [] or [{c_id, c_name, e_id, e_name, weight, t_id, t_name, u_id, u_name}, ...]
    """
    relation = RELATION["CSM"] if team else RELATION.get("PSM")
    cql = "match (c:Company)-[:employ]-(e:Engineer)-[r:{relation}]-(t:Teacher)-[:include]-(u:University) " \
          "where c.id in {company_id} and u.id in {university_id} and e.id=e.team and t.id=t.team " \
          "return c.id as c_id, c.name as c_name, e.id as e_id, e.name as e_name, r.weight as weight, " \
          "t.id as t_id, t.name as t_name, u.id as u_id, u.name as u_name " \
          "order by weight asc skip {skip} limit {limit}".format(relation=relation, company_id=company_id,
                                                                 university_id=university_id, skip=skip * limit,
                                                                 limit=limit)
    return neo4j.run(cql)


def recommendTeacherForArea(area_id, university_id, team=True, sort="", skip=0, limit=40):
    """
    向 地区 推荐适合与 高校 合作的企业
    :param area_id:
    :param university_id: list
    :param team:
    :param sort: 用于排序的其他字段，eg: company.name desc,
    :param skip:
    :param limit:
    :return: [{**town_id, town_name,** c_id, c_name, e_id, e_name, weight, t_id, t_name, u_id, u_name}, ...]
    """
    relation = RELATION["CSM"] if team else RELATION.get("PSM")
    cql = "Match (to:Town)-[:locate]-(c:Company)-[:employ]-(e:Engineer)-[r:{relation}]-(t:Teacher)" \
          "-[:include]-(u:University) where to.id={area_id} and u.id in {university_id} " \
          "return c.id as c_id, c.name as c_name, e.id as e_id, e.name as e_name, e.member as e_member, " \
          "r.weight as weight, t.name as t_name, t.id as t_id, t.institution as institution, t.member as t_member, " \
          "u.name as u_name, u.id as u_id " \
          "order by {sort} weight asc skip {skip} limit {limit}" \
        .format(relation=relation, area_id=area_id, university_id=university_id, sort=sort, skip=skip * limit,
                limit=limit)
    return neo4j.run(cql)


def totalRecommendTeacherForArea(area_id, university_id, team=True):
    """
    获取 地区 推荐适合与 高校 合作的企业 的总数
    """
    relation = RELATION["CSM"] if team else RELATION.get("PSM")
    cql = f"Match (to:Town)-[:locate]-(c:Company)-[:employ]-(e:Engineer)-[r:{relation}]-(t:Teacher)" \
          f"-[:include]-(u:University) where to.id={area_id} and u.id in {university_id} " \
          "return count(r) as total".format(relation=relation, area_id=area_id, university_id=university_id)

    return neo4j.run(cql)


def recommendCompanyForTeacher(teacher_id, area_id, skip=0, limit=20):
    """
    向 高校老师推荐 企业
    :param teacher_id:
    :param area_id:
    :param skip:
    :param limit:
    :return: [{t_id, t_name, weight, e_id, e_name, c_id, c_name, town_id, town_name}, ... ]
    """
    cql = "Match (t:Teacher)-[r]-(e:Engineer)-[:employ]-(c:Company)-[:locate]-(to:Town) " \
          f"where to.id={area_id} and t.id={teacher_id} " \
          "return t.id as t_id, t.name as t_name, r.weight as weight, e.id as e_id, e.name as e_name, " \
          "c.id as c_id, c.name as c_name, to.id as town_id, to.name as town_name " \
          "order by weight asc skip {skip} limit {limit}".format(teacher_id=teacher_id, area_id=area_id,
                                                                 skip=skip * limit, limit=limit)
    return neo4j.run(cql)
