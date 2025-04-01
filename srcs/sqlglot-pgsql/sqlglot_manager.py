import random
import sqlglot
from sqlglot.expressions import Expression
import pickle


class ExpressionSetManager:
    def __init__(self):
        # 用于存储节点的�?�器，键为父节点类型，值为节点集合
        self.parent_to_nodes = {}

    def add_node(self, node: Expression, parent_node: Expression):
        """
        向集合中添加节点�?
        如果对应父节点类型的集合不存�?，则创建一�?新集合�?
        """
        parent_type = type(parent_node).__name__  # 获取父节点类型名�?
        if parent_type not in self.parent_to_nodes:
            self.parent_to_nodes[parent_type] = set()
        self.parent_to_nodes[parent_type].add(node)

    def get_random_node(self, parent_node: Expression) -> Expression:
        """
        随机返回与指定父节点类型相同的一�?节点�?
        """
        parent_type = type(parent_node).__name__  # 获取父节点类型名�?
        if parent_type in self.parent_to_nodes and self.parent_to_nodes[parent_type]:
            return random.choice(list(self.parent_to_nodes[parent_type]))
        else:
            raise ValueError(f"No nodes available for parent type: {parent_type}")

    def get_random_node_v2(self, node: Expression) -> Expression:
        """
        随机返回与指定父节点类型相同的一�?节点�?
        """

        parent_type = type(node.parent).__name__  # 获取父节点类型名�?
        same_type_node = []
        if parent_type in self.parent_to_nodes and self.parent_to_nodes[parent_type]:
            for exp in self.parent_to_nodes[parent_type]:
                if exp.key == node.key:
                    same_type_node.append(exp)
            if len(same_type_node) == 0:
                return None
            return random.choice(list(same_type_node))
        else:
            return None
            raise ValueError(f"No nodes available for parent type: {parent_type}")

    def save_to_file(self, file_path: str):
        """
        将当前的 ExpressionSetManager 内�?�保存到�?地文件�?
        """
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.parent_to_nodes, f)
            print(f"Successfully saved to {file_path}")
        except Exception as e:
            print(f"Failed to save to {file_path}: {e}")

    def load_from_file(self, file_path: str):
        """
        从本地文件加载内容并初�?�化 ExpressionSetManager�?
        """
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
        """
        返回当前存储状态的字�?�串表示�?
        """
        return "\n".join(
            f"{parent_type}: {len(nodes)} nodes"
            for parent_type, nodes in self.parent_to_nodes.items()
        )


# 读取文件并解�? SQL �?�?
def process_sql_file(file_path: str, manager: ExpressionSetManager):
    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            for line in file:
                sql = line.strip()  # 去掉两�??的空格和换�?��??
                if sql.endswith(";"):
                    sql = sql[:-1]  # 去掉�?尾的分号
                if sql:
                    # 使用 sqlglot 解析 SQL �?�?
                    tree = sqlglot.parse_one(sql,read='postgres')
                    # 遍历�?法树�?的节�?
                    for node in tree.walk():
                        # 添加非根节点
                        # if node != tree:
                        manager.add_node(node, node.parent)
        print("Finished processing SQL file.")
    except Exception as e:
        print(f"Error processing SQL file: {e}")


def test_manager():
    sql = """
        select a,sum(b) from a;
        """
    file_path = "/houm/Squirrel/srcs/sqlglot-pgsql/mysql_seed.pkl"
    new_manager = ExpressionSetManager()
    new_manager.load_from_file(file_path)
    print(new_manager)

    # 使用 sqlglot 解析 SQL �?�?
    parsed = sqlglot.parse(sql,read='postgres')
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
    seed_path = "pgsql_seed.txt"
    manager = ExpressionSetManager()

    # 处理 SQL 文件，将节点存入管理�?
    process_sql_file(seed_path, manager)

    # 查看管理器中保存的节�?
    print("管理器状�?:")
    print(manager)
    # 保存到本地文�?
    file_path = "pgsql_seed.pkl"
    manager.save_to_file(file_path)
    exit(0)
