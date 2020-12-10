from flask import Blueprint, render_template, request, abort
from web.service.social_network import public as public_service
from web.service.social_network import recommend_detail as detail_service

recommend_detail_bp = Blueprint('recommend_detail', __name__)


@recommend_detail_bp.route("/", methods=["GET"])
@recommend_detail_bp.route("/index", methods=["GET"])
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
def technicalFieldComparison():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    team = request.args.get("team", default=1, type=int)
    return detail_service.technicalFieldComparison(eid=eid, tid=tid, team=team)


@recommend_detail_bp.route("/teamMembers")
def getTeamMembers():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    return detail_service.getTeamMembers(team_t=tid, team_e=eid)
