from flask import Blueprint, render_template, request
from web.service.social_network import recommend2Area as recommend2Area_service
from web.service.social_network import personal_network as personal_service
from web.service.social_network import public as public_service
from web.extensions import auth

recommend_graph_bp = Blueprint('recommend2Area', __name__)


@recommend_graph_bp.route("/")
@recommend_graph_bp.route("/index")
def recommend2Area():
    # TODO 获取当前用户所负责的高校 or 地区
    user_id = auth.getUserId()
    # orgs = [{"id": 19036, "name": "清华大学"}]
    orgs = public_service.getUserInfo(userid=user_id, areaAgent=True)
    return render_template("social_network/recommend2Area.html", orgs=orgs)


@recommend_graph_bp.route("/recommend")
def recommendResult():
    town_id = request.args.get("town", default="", type=str)
    com_id = request.args.get("com", default="", type=str)
    uni_id = request.args.get("uni", default="", type=str)
    limit = request.args.get("limit", default=15, type=int)

    return recommend2Area_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id, limit=limit)

