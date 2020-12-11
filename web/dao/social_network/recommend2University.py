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


def recommendEngineerAndTeacher(com_id, uni_id, teacher_id, limit=20):
    """
    指定企业 & 专家，推荐 专家和 工程师团队
    :param com_id: list [12,34,3]
    :param uni_id: list [23,543]
    :param teacher_id: [234,453, 435]
    :param limit:
    :return: [{c_id, c_name, e_id, e_name, t_id, t_name, i_id, i_name, u_id, u_name, weight)}]
    """
    cql = "match (c:Company)-[:employ]-(e:Engineer)-[r:{relation}]-(t:Teacher)-[:include]-" \
          "(i:Institution)-[:include]-(u:University) " \
          "where c.id in {company_id} and u.id in {uni_id} and t.id in {teacher_id}" \
          "return c.id as c_id, c.name as c_name, e.id as e_id, e.name as e_name, t.id as t_id, t.name as t_name, " \
          "i.id as i_id, i.name as i_name, u.id as u_id, u.name as u_name, r.weight as weight " \
          "order by weight asc limit {limit}".format(relation=RELATION["PSM"], company_id=com_id, uni_id=uni_id,
                                                     teacher_id=teacher_id, limit=limit)
    return neo4j.run(cql)
