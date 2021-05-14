from flask import Blueprint, render_template, request
from web.service.social_network import recommend2Area as recommend2Area_service
from web.service.social_network import public as public_service
# from web.extensions import oidc
from web.utils import auth

recommend2Area_bp = Blueprint('recommend2Area', __name__)


@recommend2Area_bp.route("/")
@recommend2Area_bp.route("/index")
# @oidc.require_login
# @oidc.require_keycloak_role('KETD', "孵化器")
def index():
    user_id = auth.getUserId()
    # orgs = [{"id": 2, "name": "开发区"}]
    towns = public_service.getUserInfo(userid=user_id, area_agent=True)
    return render_template("social_network/recommend2Area.html", towns=towns)
