from flask import Blueprint, render_template, request
from web.service.social_network import recommend as recommend_service, personal_network as personal_service

recommend_graph_bp = Blueprint('recommend_graph', __name__)


@recommend_graph_bp.route("/")
@recommend_graph_bp.route("/index")
@recommend_graph_bp.route("/array-graph")
def recommendArrayGraph():
    return render_template("social_network/array_graph.html")


@recommend_graph_bp.route("/recommend")
def recommendResult():
    com_id = request.args.get("com", default="", type=str)
    uni_id = request.args.get("uni", default="", type=str)
    limit = request.args.get("limit", default=15, type=int)
    return recommend_service.recommendTeacherForCompany(company_id=com_id, university_id=uni_id, limit=limit)


@recommend_graph_bp.route("/org-info")
def getOrgInfo():
    name = request.args.get("name", default="")
    org_type = request.args.get("type", default="")
    return recommend_service.getOrgId(label=org_type, name=name)


@recommend_graph_bp.route("/personal-network")
def personalNetwork():
    return render_template("social_network/personal_network.html")


@recommend_graph_bp.route("/getPersonalNetwork")
def getPersonalNetwork():
    # TODO 动态获取中介 id 及 类型
    agent_id = 1
    agent_type = "uni"
    return personal_service.getPersonalNetwork(agent_id=agent_id, agent_type=agent_type)
