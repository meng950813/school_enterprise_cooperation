"""
获取推荐团队的详细信息
"""
from web.settings import LABEL
from web.utils.neo4j_operator import neo4j as neo4j
from web.utils.mysql_operator import mysql as mysql


def getTeacherTeamBasicInfo(t_id):
    """
    获取专家团队的基本信息, 包括 专家名， 团队人数，所属高校和学院名
    :param t_id: 专家团队核心节点的 id
    :return: [{name, members, institution, org}]
    """
    cql = "match (org:{uni})-[:include]-(i:{inst})-[:include]-(t:{teacher}) where t.id={id} " \
          "return org.name as org, t.member as members, t.name as name, i.name as institution" \
        .format(uni=LABEL["UNIVERSITY"], inst=LABEL["INSTITUTION"], teacher=LABEL["TEACHER"], id=t_id)
    return neo4j.run(cql)


def getEngineerTeamBasicInfo(e_id):
    """
    获取工程师团队的基本信息， 包括 工程师名， 团队人数，企业名
    :param e_id: 工程师团队核心节点的 id
    :return: [{name, members, org}]
    """
    cql = "match (org:{com})-[:employ]-(e:{engineer}) where e.id={id} " \
          "return org.name as org, e.member as members, e.name as name, e.team_patent as team_patent" \
        .format(com=LABEL["COMPANY"], engineer=LABEL["ENGINEER"], id=e_id)
    return neo4j.run(cql)


def getSimilarPatents(team_teacher, team_engineer, teacher=True, skip=0, limit=15):
    """
    根据 专家团队和工程师团队的 team_id 获取团队间 相似的专利
    :return: [] or [{"teacher": Node type data, "engineer": Node type data}]
    """
    patent = "pt" if teacher else "pe"
    cql = "match (t:Teacher)-[:write]-(pt:Patent)-[:include]-(:IPC)-[:include]-(pe:Patent)-[:write]-(e:Engineer) " \
          "where t.team={team_teacher} and e.team={team_engineer} " \
          "return distinct({patent}.application_number) as code, {patent}.name as name, " \
          "{patent}.application_date as date order by date desc skip {skip} limit {limit}" \
        .format(team_teacher=team_teacher, team_engineer=team_engineer, patent=patent, skip=skip, limit=limit)
    return neo4j.run(cql)


def getTeamField(eid, tid):
    """
    统计 工程师团队 与 专家团队 中所有节点的industry属性，作为行业交集
    :return: [{}]
    """
    cql = "match (e:Engineer{team:%d}) with distinct(e.industry) as industry_e, count(e.industry) as count_e " \
          "match (t:Teacher{team:%d}) with distinct(t.industry) as industry_t, count(t.industry) as count_t, " \
          "industry_e, count_e " \
          "return industry_e, industry_t  order by count_e desc, count_t desc limit 1" % (eid, tid)
    return neo4j.run(cql)


def getTeamPatentsNumber(team_id, teacher=True):
    """
    统计团队中的全部成员的专利数量，将结果写入 团队核心节点中的 team_patent 属性中
    :param team_id:
    :param teacher:
    :return:[{"team_patent": 123}]
    """
    label = LABEL["TEACHER"] if teacher is True else LABEL["ENGINEER"]
    cql = "Match (l:{label})-[:write]-(p:Patent) where l.team={id} " \
          "return count(distinct(p)) as nums".format(label=label, id=team_id)
    return neo4j.run(cql)


def getTechnicalFieldComparison(eid=None, tid=None, team=True):
    """
    TODO to be deleted
    获取 企业工程师与专家的共同专利
    """
    param = "team" if team is True else "id"
    cql = "Match (e:Engineer)-[:write]-(ep:Patent)-[:include]-(ipc:IPC)-[:include]-(tp:Patent)-[:write]-(t:Teacher) " \
          f"where e.{param}={eid} and t.{param}={tid} " \
          "return ep.application_number as e_patent, " \
          "tp.application_number as t_patent, ipc.code as ipc".format(param=param, eid=eid, tid=tid)
    return neo4j.run(cql)


def getTeamTechnicalFieldDistribute(team_id, teacher=True):
    """
    获取企业工程师 / 高校专家的 团队专利技术分布 ==> 各个ipc下的专利数量分布
    :return: [{ipc:xxx, patent:xxx, date: 1429142400}, ...], 结果中包含重复数据，需要去重
    """
    label = LABEL["TEACHER"] if teacher is True else LABEL["ENGINEER"]
    cql = f"Match (n:{label})-[:write]-(p:Patent)-[:include]-(ipc:IPC) " \
          f"where n.team={team_id} " \
          f"return ipc.code as ipc, id(p) as patent, p.application_date as date"
    return neo4j.run(cql)


def getTeamMembers(team_id, teacher=True):
    """
    获取团队成员信息，用于展示团队关系图
    """
    label = LABEL["TEACHER"] if teacher is True else LABEL["ENGINEER"]
    cql = "match (t1:{label})-[r:cooperate]->(t2:{label}) " \
          "where t1.team={team_id} and t2.team={team_id} and r.frequency > 2 " \
          "and t1.id <> t2.id return t1.id as id1, t1.name as name1, t1.patent as patent1, r.frequency as count, " \
          "t2.id as id2, t2.name as name2, t2.patent as patent2".format(label=label, team_id=team_id)
    return neo4j.run(cql)


def getIndustryIPC(ipc):
    """
    获取 ipc 与 国民经济行业的对应关系
    :param ipc: set, {"A123/01", ..} or {}
    :return: [] or [{code: xxxx, title: xxx, ipc: xx}, ...]
    """
    if 0 == len(ipc):
        return []
    sql = "SELECT info.`code` as code, info.title as title, ipc_code as ipc " \
          "FROM industry_ipc as ipc " \
          "JOIN industry as info " \
          "ON info.`code` = ipc.industry_code and depth=2 " \
          "WHERE ipc.ipc_code IN {ipc}".format(ipc=tuple(ipc))
    # ==> [] or [{code: xxxx, title: xxx, ipc: xx}, ...]
    return mysql.fetch_data(sql)


if __name__ == '__main__':
    print(getIndustryIPC({"B05D1/28", "B05D1/18"}))