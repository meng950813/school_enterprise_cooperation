from flask import Blueprint, request
from web.service.social_network import link_path as path_service

link_path_bp = Blueprint('link_path', __name__)


@link_path_bp.route("/path")
def getLinkPath():
    # TODO 待获取数据，
    agent_id = 1  # 从登陆信息中获取
    agent_type = "uni"  # 从登陆信息中获取
    target_id = request.args.get("target", default=0, type=int)
    target_type = request.args.get("t_type", default="teacher", type=str)
    step = request.args.get("step", default=5, type=int)
    limit = request.args.get("limit", default=5, type=int)

    # target_id = 4797211

    return path_service.getLinkPath(agent_id=agent_id, agent_type=agent_type, target_id=target_id,
                                    target_type=target_type, max_step=step, limit=limit)
