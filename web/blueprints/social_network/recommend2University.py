from flask import Blueprint, render_template, request
from web.service.social_network import recommend2Area as recommend2Area_service
from web.service.social_network import recommend2University as recommend2University_service
from web.service.social_network import public as public_service
from web.extensions import oidc
from web.utils import auth

recommend2University_bp = Blueprint('recommend2University', __name__)


@recommend2University_bp.route("/")
@recommend2University_bp.route("/index")
@oidc.require_login
@oidc.require_keycloak_role('KETD', "技转中心")
def index():
    user_id = auth.getUserId()
    # orgs = [{"id": 19036, "name": "清华大学"}]
    universities = public_service.getUserInfo(userid=user_id, area_agent=False)
    towns = public_service.getUsefulTowns(userid=user_id)
    return render_template("/social_network/recommend2University.html", universities=universities, towns=towns)



