# -*- coding: utf-8 -*-
import random
import sqlglot
from sqlglot.expressions import Expression
import pickle



class ExpressionSetManager:
    def __init__(self):
        self.parent_to_nodes = {}

    def add_node(self, node: 'Expression', parent_node: 'Expression'):
        
        parent_type = type(parent_node).__name__
        node_type = type(node).__name__

        if parent_type not in self.parent_to_nodes:
            self.parent_to_nodes[parent_type] = {}

        if node_type not in self.parent_to_nodes[parent_type]:
            self.parent_to_nodes[parent_type][node_type] = set()

        self.parent_to_nodes[parent_type][node_type].add(node)

    def get_random_node(self, parent_node: 'Expression') -> 'Expression':
        
        parent_type = type(parent_node).__name__
        node_type = type(parent_node).__name__  # 由于未修改方法签名，默认按 parent_node 类型返回同类型节点

        if (parent_type in self.parent_to_nodes and
            node_type in self.parent_to_nodes[parent_type] and
            self.parent_to_nodes[parent_type][node_type]):

            return random.choice(list(self.parent_to_nodes[parent_type][node_type]))
        else:
            raise ValueError(f"No nodes available for parent type: {parent_type} and node type: {node_type}")

    def get_random_node_v2(self, node: 'Expression') -> 'Expression':
        
        parent_type = type(node.parent).__name__
        node_type = type(node).__name__



        if (parent_type in self.parent_to_nodes and
            node_type in self.parent_to_nodes[parent_type] and
            self.parent_to_nodes[parent_type][node_type]):

            return random.choice(list(self.parent_to_nodes[parent_type][node_type]))
        else:
            return None

    def save_to_file(self, file_path: str):
       
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.parent_to_nodes, f)
            print(f"Successfully saved to {file_path}")
        except Exception as e:
            print(f"Failed to save to {file_path}: {e}")

    def load_from_file(self, file_path: str):
        
        try:
            with open(file_path, 'rb') as f:
                self.parent_to_nodes = pickle.load(f)
            print(f"Successfully loaded from {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}. Starting with an empty manager.")
            self.parent_to_nodes = {}
        except Exception as e:
            print(f"Failed to load from {file_path}: {e}")
            self.parent_to_nodes = {}

    def __str__(self):
        
        lines = []
        for parent_type, node_dict in self.parent_to_nodes.items():
            for node_type, nodes in node_dict.items():
                lines.append(f"{parent_type} -> {node_type}: {len(nodes)} nodes")
        return "\n".join(lines)



# 读取文件并解析 SQL 语句
def process_sql_file(file_path: str, manager: ExpressionSetManager):
    try:
        with open(file_path, 'r',encoding='utf-8', errors='ignore') as file:
            for line in file:
                sql = line.strip()  # 去掉两端的空格和换行符
                if sql.endswith(";"):
                    sql = sql[:-1]  # 去掉末尾的分号
                if sql:
                    try:
                        # 使用 sqlglot 解析 SQL 语句
                        tree = sqlglot.parse_one(sql,read='mysql')
                        # 遍历语法树中的节点
                        for node in tree.walk():
                            # 添加非根节点
                            # if node != tree:
                            manager.add_node(node, node.parent)
                    except Exception as e:
                        print(f"unabled SQL: {e}")
        print("Finished processing SQL file.")
    except Exception as e:
        print(f"Error processing SQL file: {e}")


def test_manager():
    sql = """
        select a,sum(b) from a;
        """
    file_path = "mysql_seed.pkl"
    new_manager = ExpressionSetManager()
    new_manager.load_from_file(file_path)
    print(new_manager)

    # 使用 sqlglot 解析 SQL 语句
    parsed = sqlglot.parse(sql,read='mysql')
    for node in parsed[0].walk():
        if isinstance(node, sqlglot.exp.Sum):
            new_node = new_manager.get_random_node_v2(node)
    parsed[0].args['expressions'].append(new_node)
    print(parsed[0])


    exit(0)


if __name__ == "__main__":
    # test_manager()
    # file_path = "mysql_seed.pkl"
    # new_manager = ExpressionSetManager()
    # new_manager.load_from_file(file_path)
    # print(new_manager)
    # exit()

    # 使用示例
    seed_path = "mysql_seed.txt"
    manager = ExpressionSetManager()

    # 处理 SQL 文件，将节点存入管理器
    process_sql_file(seed_path, manager)

    
    print(manager)
    # 保存到本地文件
    file_path = "mysql_seed.pkl"
    manager.save_to_file(file_path)
    exit(0)
