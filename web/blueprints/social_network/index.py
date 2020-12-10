from flask import Blueprint, redirect, url_for, abort, request, render_template
from web.service.social_network import public as public_service
from web.service.social_network import personal_network as personal_service
from web.extensions import oidc
from web.utils import auth
import requests

index_bp = Blueprint('index', __name__)


@index_bp.route("/")
@index_bp.route("/index")
@oidc.require_login
def index():
    if auth.require_role("KETD", "技转中心"):
        # 高校技转中心用户
        return redirect(url_for("recommend2Area.index"))
    elif auth.require_role("KETD", "孵化器"):
        # 地区中介用户
        pass
    else:
        abort(404)


@index_bp.route("/logout")
def logout():
    # back_host = "39.98.94.44"
    back_host = "127.0.0.1:5000"
    url = "http://39.98.94.44:8085/auth/realms/kunshan/protocol/openid-connect/logout?" \
          "redirect_uri=http://{back_host}/logout".format(back_host=back_host)
    response = requests.get(url=url)

    oidc.logout()
    return redirect(url_for('index.index'))


@index_bp.route("/org-info")
def getOrgInfo():
    name = request.args.get("name", default="")
    org_type = request.args.get("type", default="")
    return public_service.getOrgId(label=org_type, name=name)


@index_bp.route("/personal-network")
@oidc.require_login
def personalNetwork():
    return render_template("social_network/personal_network.html")


@index_bp.route("/getPersonalNetwork")
@oidc.require_login
def getPersonalNetwork():
    # TODO 动态获取中介 id 及 类型
    agent_id = auth.getUserId()
    agent_type = "uni" if auth.require_role("KETD", "技转中心") else "area"
    return personal_service.getPersonalNetwork(agent_id=agent_id, agent_type=agent_type)
