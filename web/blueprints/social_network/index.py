from flask import Blueprint, redirect, url_for, abort, request, render_template
from web.service.social_network import public as public_service
from web.service.social_network import personal_network as personal_service
from web.service.social_network import recommend2University as recommend2University_service
from web.service.social_network import recommend2Area as recommend2Area_service
from web.extensions import oidc
from web.utils import auth

index_bp = Blueprint('index', __name__)


@index_bp.route("/")
@index_bp.route("/index")
@oidc.require_login
def index():
    if auth.isUniversityAgent():
        # 高校技转中心用户
        return redirect(url_for("recommend2University.index"))
    elif auth.isAreaAgent():
        # 地区中介用户
        return redirect(url_for("recommend2Area.index"))
    else:
        abort(404)


@index_bp.route("/logout")
@oidc.require_login
def logout():
    oidc.logout()
    return redirect(url_for('index.index'))


@index_bp.route("/fuzzy-org")
def fuzzyMatchOrg():
    name = request.args.get("name", default="")
    org_type = request.args.get("type", default="")
    return public_service.fuzzyMatchOrg(label=org_type, name=name)


@index_bp.route("/fuzzy-teacher")
def fuzzyMatchTeacher():
    name = request.args.get("name", default="")
    uni = request.args.get("uni", default=0, type=int)
    return public_service.fuzzyMatchTeacher(uni=uni, name=name)


@index_bp.route("/personal-network")
@oidc.require_login
def personalNetwork():
    return render_template("social_network/personal_network.html")


@index_bp.route("/getPersonalNetwork")
@oidc.require_login
def getPersonalNetwork():
    agent_id = auth.getUserId()
    agent_type = "uni" if auth.require_role("KETD", "技转中心") else "area"
    return personal_service.getPersonalNetwork(agent_id=agent_id, agent_type=agent_type)


@index_bp.route("/recommend")
# @oidc.require_login
def recommendResult():
    town_id = request.args.get("town", default="", type=str)
    com_id = request.args.get("com", default="", type=str)
    uni_id = request.args.get("uni", default="", type=str)
    teacher_id = request.args.get("teacher", default="", type=str)
    limit = request.args.get("limit", default=15, type=int)
    if auth.require_role("KETD", "技转中心"):
        # 高校技转中心用户
        return recommend2University_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id,
                                                            teacher_id=teacher_id, limit=limit)
    else:
        # 地区中介用户
        return recommend2Area_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id, limit=limit)
