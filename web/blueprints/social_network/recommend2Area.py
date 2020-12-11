from flask import Blueprint, render_template, request
from web.service.social_network import recommend2Area as recommend2Area_service
from web.service.social_network import public as public_service
from web.extensions import oidc
from web.utils import auth

recommend2Area_bp = Blueprint('recommend2Area', __name__)


@recommend2Area_bp.route("/")
@recommend2Area_bp.route("/index")
@oidc.require_login
def index():
    user_id = auth.getUserId()
    # orgs = [{"id": 2, "name": "开发区"}]
    towns = public_service.getUserInfo(userid=user_id, area_agent=True)
    return render_template("social_network/recommend2Area.html", towns=towns)


@recommend2Area_bp.route("/recommend")
@oidc.require_login
def recommendResult():
    town_id = request.args.get("town", default="", type=str)
    com_id = request.args.get("com", default="", type=str)
    uni_id = request.args.get("uni", default="", type=str)
    limit = request.args.get("limit", default=15, type=int)

    return recommend2Area_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id, limit=limit)

