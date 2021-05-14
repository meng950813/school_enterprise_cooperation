from flask import Blueprint, render_template, request, abort
from web.service.social_network import public as public_service
from web.service.social_network import recommend_detail as detail_service
# from web.extensions import oidc

recommend_detail_bp = Blueprint('recommend_detail', __name__)


@recommend_detail_bp.route("/", methods=["GET"])
@recommend_detail_bp.route("/index", methods=["GET"])
# @oidc.require_login
def index():
    source = request.args.get("s", default="", type=str)
    target = request.args.get("t", default="", type=str)
    if source == target or not (isinstance(source, str) and isinstance(target, str)):
        abort(400)

    source, target = source.split("_"), target.split('_')
    if 2 != len(source) or 2 != len(target) or source[0] == target[0]:
        abort(400)

    try:
        source[1], target[1] = int(source[1]), int(target[1])
    except Exception as e:
        abort(400)

    if (source[0] == "e" and target[0] == "t") or (source[0] == "t" and target[0] == "e"):
        return compareTeacherAndEngineerTeam(source=source, target=target)
    return "TODO"


def compareTeacherAndEngineerTeam(source, target):
    """
    展示 专家团队 - 工程师团队的对比 页面
    :param source: list, ["e", 123] or ["t", 321]
    :param target: list, ["e", 123] or ["t", 321]
    :return:
    """
    eid, tid = (source[1], target[1]) if source[0] == "e" else (target[1], source[1])
    basic_info = detail_service.compareTeacherAndEngineerTeam(eid=eid, tid=tid)
    return render_template("social_network/compareTeacherAndEngineerTeam.html", eid=eid, tid=tid, basic_info=basic_info)


@recommend_detail_bp.route("/technicalFieldComparison")
# @oidc.require_login
def technicalFieldComparison():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    team = request.args.get("team", default=1, type=int)
    return detail_service.technicalFieldComparison(eid=eid, tid=tid, team=team)


@recommend_detail_bp.route("/field")
# @oidc.require_login
def technicalFieldComparisonForRadar():
    """
    获取技术领域分布雷达图所需数据
    :return:
    """
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    return detail_service.technicalFieldComparisonForRadar(eid=eid, tid=tid)


@recommend_detail_bp.route("/teamMembers")
# @oidc.require_login
def getTeamMembers():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    return detail_service.getTeamMembers(team_t=tid, team_e=eid)


@recommend_detail_bp.route("/river")
# @oidc.require_login
def technicalFieldComparisonForRiver():
    """
    获取河流图所需数据
    :return:
    """
    teamId = request.args.get("teamId", default=None, type=int)
    team_type = request.args.get("type", default=1, type=int)
    return detail_service.chartsRiver(teamId=teamId, teacher=True if 1 == team_type else False)


@recommend_detail_bp.route("/wordCloud")
# @oidc.require_login
def technicalFieldComparisonForWordCloud():
    """
    获取词云所需数据
    :return:
    """
    teamId = request.args.get("teamId", default=None, type=int)
    team_type = request.args.get("type", default=1, type=int)
    return detail_service.wordCloud(teamId=teamId, teacher=True if 1 == team_type else False)
