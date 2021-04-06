from flask import Blueprint, redirect, url_for, abort, request, render_template, flash
from web.service.social_network import public as public_service
from web.service.social_network import personal_network as personal_service
from web.service.social_network import recommend2University as recommend2University_service
from web.service.social_network import recommend2Area as recommend2Area_service
from web.service.social_network import api as api_service
from web.extensions import oidc
from web.utils import auth
import json

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


@index_bp.route("/fuzzy-engineer")
def fuzzyMatchEngineer():
    name = request.args.get("name", default="")
    com = request.args.get("com", default=0, type=int)
    return public_service.fuzzyMatchEngineer(com=com, name=name)


@index_bp.route("/fuzzy-teacher")
def fuzzyMatchTeacher():
    name = request.args.get("name", default="")
    uni = request.args.get("uni", default=0, type=int)
    return public_service.fuzzyMatchTeacher(uni=uni, name=name)


@index_bp.route("/recommend")
# @oidc.require_login
def recommendResult():
    town_id = request.args.get("town", default="", type=str)
    com_id = request.args.get("com", default="", type=str)
    uni_id = request.args.get("uni", default="", type=str)
    teacher_id = request.args.get("teacher", default="", type=str)
    limit = request.args.get("limit", default=15, type=int)
    if not auth.require_role("KETD", "技转中心"):
        # 高校技转中心用户
        return recommend2University_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id,
                                                            teacher_id=teacher_id, limit=limit)
    else:
        # 地区中介用户
        return recommend2Area_service.recommendResult(town_id=town_id, com_id=com_id, uni_id=uni_id, limit=limit)


@index_bp.route("/recommend-table")
def recommendTable():
    return render_template("social_network/recommend.html")


@index_bp.route("/personal-network")
@oidc.require_login
def personalNetwork():
    if auth.isAreaAgent():
        return render_template("social_network/personal_network.html", area=True)
    else:
        user_id = auth.getUserId()
        universities = public_service.getUserInfo(userid=user_id, area_agent=False)
        return render_template("social_network/personal_network.html", area=False, universities=universities)


@index_bp.route("/getPersonalNetwork")
@oidc.require_login
def getPersonalNetwork():
    agent_id = auth.getUserId()
    agent_type = "uni" if auth.require_role("KETD", "技转中心") else "area"
    return personal_service.getPersonalNetwork(agent_id=agent_id, agent_type=agent_type)


@index_bp.route("/addContactInformation", methods=["POST"])
@oidc.require_login
def addContactInformation():
    agent_id = auth.getUserId()
    agent_type = "uni" if auth.require_role("KETD", "技转中心") else "area"
    target_id = request.form.get("target-id", default=0, type=int)
    target_type = request.form.get("target-type", default="", type=str)
    method = request.form.get("cooper-method", default="visit", type=str)
    datetime = request.form.get("datetime", default="", type=str)
    visited, cooperate, activity = 0, 0, 0
    if "active" == method:
        activity += 1
    elif "coop" == method:
        cooperate += 1
    elif "visit" == method:
        visited += 1
    else:
        flash(message="请选择正确的活动类型", category="error")
        return redirect(url_for("index.personalNetwork"))
    result = api_service.addContactInformation(agent_id=agent_id, agent_type=agent_type, target_id=target_id,
                                               target_type=target_type, visited=visited, cooperate=cooperate,
                                               activity=activity)
    if result["success"]:
        flash(message="添加成功", category="success")
    else:
        flash(message=result["message"], category="error")
    return redirect(url_for("index.personalNetwork"))


@index_bp.route("/cooperate", methods=["get"])
def cooperate():
    return render_template("social_network/cooperate.html")


@index_bp.route("/cooperate_record", methods=["get"])
def cooperate_record():
    records = [

    ]

    res = {"success": True, "data": records, "total": 1}

    return json.dumps(res)


@index_bp.route("/visit", methods=["get"])
def visit():
    return render_template("social_network/visit.html")


@index_bp.route("/visit_record", methods=["get"])
def visit_record():
    records = [
        {
            "teacher": "史清宇",
            "institution": "机械工程系",
            "university": "清华大学",
            "date": "2020年11月11日"
        },
        {
            "teacher": "汪泽",
            "institution": "机械学院",
            "university": "清华大学",
            "date": "2020年11月4日"
        },
        {
            "teacher": "胡楚雄",
            "institution": "机械工程系",
            "university": "清华大学",
            "date": "2020年10月23日"
        },
        {
            "teacher": "蔡志鹏",
            "institution": "机械工程系",
            "university": "清华大学",
            "date": "2020年8月19日"
        }
    ]

    res = {"success": True, "data": records, "total": 1}

    return json.dumps(res)
