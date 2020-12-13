from flask import Blueprint, request
from web.service.social_network import link_path as path_service
from web.utils import auth

link_path_bp = Blueprint('link_path', __name__)


@link_path_bp.route("/path")
def getLinkPath():
    agent_id = auth.getUserId()
    # agent_id = "jizhuan1"
    agent_type = ""  # 从登陆信息中获取
    if auth.isUniversityAgent():
        agent_type = "uni"
    elif auth.isAreaAgent():
        agent_type = "area"

    target_id = request.args.get("target", default="", type=str)
    target_type = request.args.get("t_type", default="teacher", type=str)
    step = request.args.get("step", default=3, type=int)
    limit = request.args.get("limit", default=5, type=int)

    # target_id = 4797211

    return path_service.getLinkPath(agent_id=agent_id, agent_type=agent_type, target_id=target_id,
                                    target_type=target_type, max_step=step, limit=limit)
