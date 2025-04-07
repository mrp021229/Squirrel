import random
import sqlglot
from sqlglot.expressions import Expression
import pickle


class ExpressionSetManager:
    def __init__(self):
        # �?ㄤ簬瀛樺偍鑺傜偣鐨勫�瑰櫒锛岄敭涓虹埗鑺傜偣�?诲瀷锛屽€间负鑺傜偣闆嗗悎
        self.parent_to_nodes = {}

    def add_node(self, node: Expression, parent_node: Expression):
        parent_type = type(parent_node).__name__  # 鑾峰彇鐖惰妭鐐圭�?鍨�??悕绉�?
        if parent_type not in self.parent_to_nodes:
            self.parent_to_nodes[parent_type] = set()
        self.parent_to_nodes[parent_type].add(node)

    def get_random_node(self, parent_node: Expression) -> Expression:
        
        parent_type = type(parent_node).__name__  # 鑾峰彇鐖惰妭鐐圭�?鍨�??悕绉�?
        if parent_type in self.parent_to_nodes and self.parent_to_nodes[parent_type]:
            return random.choice(list(self.parent_to_nodes[parent_type]))
        else:
            raise ValueError(f"No nodes available for parent type: {parent_type}")

    def get_random_node_v2(self, node: Expression) -> Expression:
        """
        """

        parent_type = type(node.parent).__name__  # 鑾峰彇鐖惰妭鐐圭�?鍨�??悕绉�?
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
        """
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(self.parent_to_nodes, f)
            # print(f"Successfully saved to {file_path}")
        except Exception as e:
            # print(f"Failed to save to {file_path}: {e}")

    def load_from_file(self, file_path: str):
        """
        """
        try:
            with open(file_path, 'rb') as f:
                self.parent_to_nodes = pickle.load(f)
            # print(f"Successfully loaded from {file_path}")
        except FileNotFoundError:
            # print(f"File not found: {file_path}. Starting with an empty manager.")
            self.parent_to_nodes = {}
        except Exception as e:
            # print(f"Failed to load from {file_path}: {e}")
            self.parent_to_nodes = {}

    def __str__(self):
        """
        """
        return "\n".join(
            f"{parent_type}: {len(nodes)} nodes"
            for parent_type, nodes in self.parent_to_nodes.items()
        )


# 璇�?�彇鏂囦欢骞惰В鏋�? SQL 璇�鍙�
def process_sql_file(file_path: str, manager: ExpressionSetManager):
    try:
        with open(file_path, 'r',encoding='utf-8') as file:
            for line in file:
                sql = line.strip()  # 鍘绘帀涓ょ��鐨勭┖鏍煎拰鎹㈣�岀��
                if sql.endswith(";"):
                    sql = sql[:-1]  # 鍘绘帀鏈�灏剧殑鍒嗗彿
                if sql:
                    # 浣跨�? sqlglot 瑙ｆ�? SQL 璇�鍙�
                    tree = sqlglot.parse_one(sql,read='postgres')
                    # �?嶅巻璇�娉曟爲涓�鐨�?�?鐐�
                    for node in tree.walk():
                        # 娣�?��?�闈炴牴鑺傜�?
                        # if node != tree:
                        manager.add_node(node, node.parent)
        # print("Finished processing SQL file.")
    except Exception as e:
        # print(f"Error processing SQL file: {e}")


def test_manager():
    sql = """
        select a,sum(b) from a;
        """
    file_path = "/home/Squirrel/srcs/sqlglot-pgsql/mysql_seed.pkl"
    new_manager = ExpressionSetManager()
    new_manager.load_from_file(file_path)
    # print(new_manager)

    # 浣跨�? sqlglot 瑙ｆ�? SQL 璇�鍙�
    parsed = sqlglot.parse(sql,read='postgres')
    for node in parsed[0].walk():
        if isinstance(node, sqlglot.exp.Sum):
            new_node = new_manager.get_random_node_v2(node)
    parsed[0].args['expressions'].append(new_node)
    # print(parsed[0])


    exit(0)


if __name__ == "__main__":
    # test_manager()
    # file_path = "mysql_seed.pkl"
    # new_manager = ExpressionSetManager()
    # new_manager.load_from_file(file_path)
    # print(new_manager)
    # exit()

    # 浣跨敤绀轰緥
    seed_path = "pgsql_seed.txt"
    manager = ExpressionSetManager()

    # 澶勭�? SQL 鏂囦欢锛屽皢鑺傜偣瀛樺叆绠＄悊鍣�
    process_sql_file(seed_path, manager)

    # 鏌ョ湅绠＄悊鍣ㄤ腑淇濆瓨鐨勮�?鐐�
    # print("绠＄悊鍣ㄧ姸�?�?:")
    # print(manager)
    # 淇濆瓨鍒版湰鍦版枃浠�?
    file_path = "pgsql_seed.pkl"
    manager.save_to_file(file_path)
    exit(0)
