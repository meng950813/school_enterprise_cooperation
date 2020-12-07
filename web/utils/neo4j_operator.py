"""
节点及关系操作，包括
创建节点/关系，
修改节点/关系属性，
删除节点/关系
"""
from py2neo import Graph, Node, Relationship, RelationshipMatcher
from config import NEO_CHEN


class Neo4jOperate(object):
    def __init__(self, host, user, password):
        self.graph = Graph(host, auth=(user, password))

        self.relationship_matcher = RelationshipMatcher(self.graph)

    def create_one_relationship(self, start_node={}, target_node={}, relationship=None, **prop):
        """
        创建两个节点间关系: 若已存在
        :param start_node: Node or  dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param target_node: Node or dict ==> {"label": "Patent", "search":{"ipc_code": "CN102931914A"}}
        :param relationship: str 关系名
        :param prop: 关系属性
        :return: True or False
        """
        s_node = self.search_node(start_node)
        t_node = self.search_node(target_node)
        if s_node is None or t_node is None:
            return False

        relation = self.search_relationship(s_node, t_node, relationship)
        if relation:
            return self.update_one_relationship(s_node, t_node, relationship, **prop)
        return self.create_relation(start_node=s_node, relationship=relationship, target_node=t_node, **prop)

    def update_one_relationship(self, start_node={}, target_node={}, relation=None, cover=True, **prop):
        """
        修改两个节点间关系
        :param start_node: Node or  dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param target_node: Node or dict ==> {"label": "Patent", "search":{"ipc_code": "CN102931914A"}}
        :param relation: 关系名 or Relationship
        :param cover: 新传入的属性值是否覆盖原值， 默认True
        :param prop: 关系属性
        :return: True or False
        """
        if not isinstance(relation, Relationship):
            relation = self.search_relationship(start_node, target_node, relation)

        if relation is None:
            return False

        for key, value in dict(prop).items():
            if key not in relation or cover is True:
                relation[key] = value
            else:
                relation[key] += value
        try:
            self.graph.push(relation)
            return True
        except Exception as e:
            print(e)
            return False

    def delete_one_relationship(self, start_node={}, target_node={}, relationship=None, properety=None):
        """
        删除一条节点间关系， 返回关系上的所有属性
        :param start_node: dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param target_node: dict ==> {"label": "Patent", "search":{"ipc_code": "CN102931914A"}}
        :param relationship: 关系名
        :param properety: set 属性集合，若不为空，返回被删除关系的对应属性值: {"weight", "paper",...}
        :return: 关系属性：{} or False
        """
        relation = self.search_relationship(start_node, target_node, relationship)
        if relation is None:
            return True

        try:
            # 关系存在 ==> 删除关系，返回关系属性
            if properety is not None and len(properety) > 0:
                back = {}
                for key in set(properety):
                    if key in relation:
                        back[key] = relation[key]
                return back
            self.graph.separate(relation)
            return True
        except Exception as e:
            return False

    def migrate_relationship(self, source_node={}, self_node={}, target_node={}, r_type=None, **property):
        """
        断开某节点与当前节点的关系，并将该关系转移到另一节点中， 保存关系上的所有属性
        A-B ==> B-C
        :param source_node: Node or  dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param self_node: Node or  dict
        :param target_node: Node or  dict
        :param r_type: 关系名
        :param property: set, 需要转移的属性集合
        :return: True or False
        """
        relation = self.delete_one_relationship(source_node, self_node, r_type, **property)
        return self.create_one_relationship(target_node, self_node, **relation)

    def search_relationship(self, start_node={}, target_node={}, relationship=None):
        """
        查找节点间关系
        :param start_node: dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param target_node:  dict ==> {"label": "Patent", "search":{"ipc_code": "CN102931914A"}}
        :param relationship: 关系名
        :return: Relationship or None
        """
        # 查找结点
        start_node = self.search_node(start_node)
        if start_node is None:
            return None
        target_node = self.search_node(target_node)
        if target_node is None:
            return None

        return self.relationship_matcher.match(nodes=[start_node, target_node], r_type=relationship).first()

    def search_node(self, search_dict):
        """
        根据给定参数字典返回节点
        :param search_dict: Node or dict ==> {"label": "Teacher", "search":{"id": 123}}
        :return: Node or None
        """
        if type(search_dict) is Node:
            return search_dict

        elif type(search_dict) is dict:
            if "label" in search_dict and "search" in search_dict:
                node_search = self.graph.nodes.match(search_dict["label"]).where(**search_dict["search"]).first()
                return node_search
            else:
                return None

    def update_node(self, search_dict, **prop):
        """
        根据给定参数字典更新节点属性
        :param search_dict: Node or dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param prop: 节点属性
        :return: True or False
        """
        node = self.get_node(search_dict=search_dict, create_if_not_exist=False)
        if node is None:
            return False
        for key, value in prop.items():
            node[key] = value
        try:
            self.graph.push(node)
            return True
        except Exception as e:
            return False

    def get_node(self, search_dict, create_if_not_exist=True, **prop):
        """
        从数据库中搜索节点，若数据库中不存在，创建节点再返回
        :param search_dict: Node or dict ==> {"label": "Teacher", "search":{"id": 123}}
        :param create_if_not_exist: boolean型， 若查询不到节点则 创建, 默认 True
        :param prop: 节点属性
        :return: Node or None ==> 表示创建节点失败
        """
        node = self.search_node(search_dict)
        if node is None and create_if_not_exist:
            return self.create_node(search_dict=search_dict, **prop)
        # else:
        #     # print("节点已存在")
        #     Logger.info("node exist")
        return node

    def create_node(self, search_dict, **prop):
        node = Node(search_dict["label"], **prop)
        try:
            self.graph.create(node)
            return self.search_node(search_dict)
        except Exception as e:
            # print("创建节点失败，%s" % e)
            return None

    def create_relation(self, start_node, relationship, target_node, **prop):
        relation = Relationship(start_node, relationship, target_node)
        for key, value in dict(prop).items():
            relation[key] = value

        try:
            self.graph.create(relation)
            return True
        except Exception as e:
            # print("创建关系失败：%s" % e)
            return False
        return False

    def run(self, cql):
        return self.graph.run(cql).data()

    def run_without_data(self, cql):
        return self.graph.run(cql)


neo4j = Neo4jOperate(**NEO_CHEN)
