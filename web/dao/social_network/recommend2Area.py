"""
面向地区中介的 推荐功能，主要包括
    input   =>  output
1.  town    =>  company & university
2.  town + university   =>  company & institution
3.  company =>  company & institution
4.  company + university    =>  engineer_team & teacher_team
5.  company + institution   =>  engineer_team & teacher_team
"""
from web.settings import RELATION
from web.utils.neo4j_operator import neo4j as neo4j


def recommendUniversityAndCompany(town_id, limit=20):
    """
    根据选定区域id，向指定区域推荐 企业 和 高校
    :param town_id: int
    :param limit:
    :return: [{town_id, town_name, c_id, c_name, u_id, u_name, weight}, ...]
        # {col0_id, col0_name, col1_id, col1_name, col2_id, col2_name, weight}
    """
    cql = "match (town:Town)-[:locate]-(c:Company)-[r:{relation}]-(u:University) " \
          "where town.id={town_id} " \
          "return town.id as town_id,town.name as town_name, c.id as c_id, c.name as c_name, " \
          "u.id as u_id, u.name as u_name, r.weight as weight " \
          "order by weight asc limit {limit}".format(relation=RELATION["CUSM"], town_id=town_id, limit=limit)
    return neo4j.run(cql)


def recommendInstitutionAndCompany(town_id, uni_id, limit=20):
    """
    根据选定区域的id、 以及选定高校的id, 推荐地区企业 和 高校学院
    :param town_id: int
    :param uni_id: list [23, ..] or []
    :param limit:
    :return: [{town_id, town_name, c_id, c_name, i_id, i_name, u_id, u_name, weight)}]
    """
    cql = "match (town:Town)-[:locate]-(c:Company)-[r:{relation}]-(i:Institution)-[:include]-(u:University) " \
          "where town.id = {town_id} and u.id in {uni_id} " \
          "return town.id as town_id,town.name as town_name, c.id as c_id, c.name as c_name, " \
          "i.id as i_id, i.name as i_name, u.id as u_id, u.name as u_name, r.weight as weight " \
          "order by weight asc limit {limit}".format(relation=RELATION["CISM"], town_id=town_id, uni_id=uni_id, limit=limit)
    return neo4j.run(cql)


def recommendInstitutionForCompany(company_id, limit=20):
    """
    根据企业id， 为特定企业推荐 高校学院
    :param company_id: list [123, ..]
    :param limit:
    :return: [{town_id, town_name, c_id, c_name, i_id, i_name, u_id, u_name, weight)}]
    """
    cql = "match (town:Town)-[:locate]-(c:Company)-[r:{relation}]-(i:Institution)-[:include]-(u:University) " \
          "where c.id in {company_id} " \
          "return town.id as town_id,town.name as town_name, c.id as c_id, c.name as c_name, " \
          "i.id as i_id, i.name as i_name, u.id, u.name, r.weight as weight " \
          "order by weight asc limit {limit}".format(relation=RELATION["CISM"], company_id=company_id, limit=limit)
    return neo4j.run(cql)


def recommendEngineerAndTeacher(company_id, uni_id, limit=20):
    """
    选定企业和高校，推荐 工程师团队和专家团队
    :param company_id: list [123, 234, ...]
    :param uni_id: list [1213, 2234, ...
    :param limit:
    :return: [{c_id, c_name, e_id, e_name, t_id, t_name, i_id, i_name, u_id, u_name, weight)}]
    """
    cql = "match (c:Company)-[:employ]-(e:Engineer)-[r:{relation}]-(t:Teacher)-[:include]-" \
          "(i:Institution)-[:include]-(u:University) " \
          "where c.id in {company_id} and u.id in {uni_id}" \
          "return c.id as c_id, c.name as c_name, e.id as e_id, e.name as e_name, t.id as t_id, t.name as t_name, " \
          "i.id as i_id, i.name as i_name, u.id as u_id, u.name as u_name, r.weight as weight " \
          "order by weight asc limit {limit}".format(relation=RELATION["CSM"], company_id=company_id, uni_id=uni_id, limit=limit)
    return neo4j.run(cql)
