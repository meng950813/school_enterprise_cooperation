from flask import Blueprint, render_template, request
from web.service.social_network import recommend as recommend_service
from web.service.social_network import public as public_service
from web.service.social_network import recommend_detail as detail_service

recommend_bp = Blueprint('recommend', __name__)


@recommend_bp.route("/")
@recommend_bp.route("/index")
def index():
    universities = public_service.getUniversityList(limit=150)
    return render_template("social_network/index.html", universities=universities)


@recommend_bp.route("/recommendTeacherForArea", methods=["GET"])
def recommendTeacherForArea():
    u_id = request.args.get("uni", default="", type=str)
    skip = request.args.get("pageNum", default=0, type=int)
    limit = request.args.get("pageSize", default=10, type=int)
    sort = request.args.get("sort", type=str, default="")
    order = request.args.get("order", type=str, default="desc")
    return recommend_service.recommendTeacherForArea(area_id=2, uni_id=u_id, sort=sort, order=order,
                                                     skip=skip, limit=limit)


@recommend_bp.route("/recommendDetail", methods=["GET"])
def recommendDetail():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    team = request.args.get("team", default=1, type=int)
    basic_info = detail_service.recommendDetail(eid=eid, tid=tid, team=team)
    return render_template("social_network/compareTeacherAndEngineerTeam.html", eid=eid, tid=tid, team=team, basic_info=basic_info)


@recommend_bp.route("/technicalFieldComparison")
def technicalFieldComparison():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    team = request.args.get("team", default=1, type=int)
    return detail_service.technicalFieldComparison(eid=eid, tid=tid, team=team)


@recommend_bp.route("/teamMembers")
def getTeamMembers():
    eid = request.args.get("eid", default=None, type=int)
    tid = request.args.get("tid", default=None, type=int)
    return detail_service.getTeamMembers(team_t=tid, team_e=eid)