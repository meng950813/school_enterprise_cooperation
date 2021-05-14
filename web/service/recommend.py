class Recommend(object):
    pass
    # def reRank(self, eid, limit):
    #     vec_e = self.getNodeVector(eid)  # 获取节点向量
    #     recall_list = vec2Faiss(vec_e, limit * 10)  # 获取召回结果
    #     com_id, capital = self.getCapital(eid)  # 获取工程师所在企业id及其注册资本
    #     RD = capital * 0.03  # 计算研发投入占比
    #     cooperate_record = self.getCooperateRecord(com_id)  # 获取合作记录
    #     recommend = dict()
    #     for item in recall_list:
    #         tid, sim = item["id"], item["sim"]
    #         if tid in cooperate_record:  # 双方有过合作
    #             sim += cooperate_record[tid] / capital
    #         recommend[tid] = sim
    #     res = sorted(recommend.items(), key=lambda kv: (kv[1], kv[0]))  # 按权值重排序
    #     res = res[:limit]  # 截取排名靠前的结果
    #     # 返回格式化推荐结果
    #     return [{"tid": item[0], "sim": item[1]} for item in res]
