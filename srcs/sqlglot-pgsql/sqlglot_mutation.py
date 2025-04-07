import random
import time

import sqlglot
from sqlglot.expressions import Expression
import pickle
import copy
from sqlglot_manager import ExpressionSetManager

# 2.11 todolist�??
# []插入和删�??
# 改进manager实现按照经验对节点分布进行插入删除，以及变异后更新manager
# 1w条的测试，主要测试fill

manager = ExpressionSetManager()


# 读取文件并解�?? SQL �??�??
def process_sql_file(file_path: str, manager: ExpressionSetManager):
    try:
        with open(file_path, 'r') as file:
            for line in file:
                sql = line.strip()  # 去掉两�??的空格和�?�??��??
                if sql.endswith(";"):
                    sql = sql[:-1]  # 去掉�??尾的分号
                if sql:
                    # 使用 sqlglot 解析 SQL �??�??
                    tree = sqlglot.parse_one(sql,read='postgres')
                    # 遍历�??法树�??的节�??
                    for node in tree.walk():
                        # 添加非根节点
                        if node != tree:
                            manager.add_node(node, node.parent)
        # print("Finished processing SQL file.")
    except Exception as e:
        pass
        # print(f"Error processing SQL file: {e}")


class SQLRandomReplacer:
    def __init__(self):
        """
        初�?�化替换�??
        :param random_node_generator: 一�??函数，接受当前节点并返回一�??新的随机节点
        """

    def check_func(self, tree):
        for node in tree.find_all(sqlglot.expressions.Select):
            # 忽略嵌�?�的查�??，仅检查顶层查询的 SELECT
            if node.parent is None:  # �??处理顶层查�??
                # 检�?? SELECT �??�??否有聚合函数
                for child in node.find_all(sqlglot.expressions.Sum):
                    if child.parent == node:
                        return True
        return False

    def insert_delete(self, node):

        return node

    def replace_nodes(self, parsed_sql):
        """
        遍历并替�?�???法树�??的每�??子节�??
        :param parsed_sql: 已解析的 SQL 表达�??
        """
        mutation_num = 0
        root = 0
        for node in parsed_sql.walk():
            # print(parsed_sql)
            # print("1")
            if mutation_num >= 10:
                break
            # 插入替换
            if node.key == 'select':
                new_node = self.insert_delete(node)
                # print("INSERT OR DELETE")
                if new_node is not None:
                    node.replace(new_node)
                    mutation_num = mutation_num + 1
                    # print(parsed_sql)
                    continue

            # 跳过根节点（�??选）
            if node.parent is None:
                # print(2)
                continue
            # 调用随机节点生成函数生成新的节点

            for a in range(10):
                # print(3)
                new_node = manager.get_random_node(node.parent)
                if node.key == new_node.key:
                    # 执�?�替换操�??
                    if new_node is not None:
                        node.replace(new_node)
                        mutation_num = mutation_num + 1
                        # print(parsed_sql)
                        break

        return parsed_sql

    # based on experience insert&delete followed by the seeds
    def mutation(self, parsed_sql):
        mutation_num = 20
        for node in parsed_sql.walk(bfs=True):


            if mutation_num < 0:
                break
            if random.random() > 0.8:

                std_node = manager.get_random_node_v2(node)

                if std_node is not None:

                    std_key = [key for key, value in std_node.args.items() if value is not None]
                    node_key = [key for key, value in node.args.items() if value is not None]
                    # insert from std_node
                    if random.random() > 0.8:
                        for key in std_key:

                            if key not in node_key:
                                # node.args[key] = std_node.args[key]
                                # print([node])
                                node.set(key, std_node.args[key])
                                # print([node])
                                # print(node.sql())
                                mutation_num = mutation_num -1
                    if random.random() < 0.2:
                        for key in node_key:

                            if key not in std_key:
                                node.set(key, None)
                                mutation_num = mutation_num - 1
                # print(std_node)
                # print(node)
            #replace
            if random.random() > 0.5 and node.parent is not None:

                new_node = manager.get_random_node_v2(node)

                if new_node is not None and node.key == new_node.key:
                    node.replace(new_node)
                    mutation_num = mutation_num - 1

            try:
                # print(parsed_sql.sql(dialect='postgres'))
                current_sql = str(parsed_sql.sql(dialect='postgres'))+';'
                # print(current_sql)
                check_sql = sqlglot.parse(current_sql,read='postgres')
            except Exception as e:
                return None
            else:
                pass
                # print("correct")

        return parsed_sql

def get_mutated_sql(sql):
    # print("mmm")
    # print(sql)
    file_path = "/home/Squirrel/srcs/sqlglot-pgsql/pgsql_seed.pkl"
    manager.load_from_file(file_path)
    parsed = sqlglot.parse(sql,dialect='postgres')
    replacer = SQLRandomReplacer()

    new_sql = copy.deepcopy(random.choice(parsed))
    transformed_sql = replacer.mutation(new_sql)

    try:
        if transformed_sql is not None:
            check_sql = sqlglot.parse_one(transformed_sql.sql(dialect='postgres'),read='postgres')
    except Exception as e:
        # print("failed")
        return None
    else:
        # print("success")
        return transformed_sql.sql(dialect='postgres')
        
    

if __name__ == "__main__":
    start_time = time.time()
    file_path = "/home/Squirrel/srcs/sqlglot-pgsql/pgsql_seed.pkl"

    manager.load_from_file(file_path)
#from squirrel-pgsql
    sql = """
    
    insert into v0(v1,v3) values(10,10);
    create table v0(v1 INT, v2 INT);
    select v1, v2 from v0;
    create table v0(v1 int);
    create index v1 on v0(v1);
    insert into v0 values(1);
    update v0 set v1 = 1 where v1 = 3; 
    select v1 from v0;
    create table v0(v1 INT, v2 INT);
    create index v3 on v0(v1);
    reindex table v0;
    create table v0(v1 int ,v2 int);
    create view v2 as select v1, v2 from v0;
    insert into v2 values(1, 1);
    select v1 from v2;
    create table v0(v1 INT, v2 INT, v3 FLOAT, v4 INT);
    create view v5 AS select * from v0;
    insert into v5(v3, v4) values(10, 'duck');
    create table v0(v1 FLOAT);
    create view v2 AS select * from v0;
    select * from v2;
    create temp table v0(v1 int);
    insert into v0 values (1);
    alter table v0 drop column v1;
    create table v0(v1 int);
    insert into v0 values( 1 );
    create table v0(v1 INT, v2 STRING);
    insert into table v0(v1) values(10);
    select v1 from v0;
    create table v0(v1 INT);
    insert into v0(v1) values (10);
    update v0 set v1=3;
    create table v0(v1 STRING);
    alter table v0 RENAME TO v2;
    insert into v2(v1) values(10);
    create table v0(v1 VARCHAR(10));
    select * from v0;
    create table v0(v1 int, v2 int, v3 char);
    select v1 from v0 union select v2 from v0;
    reindex table v0;
    create table v0(v1 int, v2 int, v3 char);
    select v1 from v0 union select v2 from v0;
    CREATE TABLE v0 ( v1 INT , v2 INT ) ;
    CREATE FUNCTION v3 ( ) RETURN TRIGGER AS $$ BEGIN UPDATE v0 set v1=10 where v1=5 ;END $$ LANGUAGE PLPGSQL ;
    CREATE TRIGGER v5 BEFORE INSERT OF v1 ON v0 FOR EACH ROW EXECUTE PROCEDURE v3 ( ) ;
    insert into v0(v1, v2) values (1,1);
    """
    sql2="""
    
    update v0 set v1 = 1 where v1=20;
    """
    parsed = sqlglot.parse(sql,dialect='postgres')
    # print(parsed[0].args)
    replacer = SQLRandomReplacer()
    num = 0
    # 假�?�文件名
    output_file = "mutation-pgsql.txt"
    with open(output_file, "a", encoding="utf-8") as f:
        for i in range(10000):
            # print(i)
            new_sql = copy.deepcopy(random.choice(parsed))
            # print("choice")
            # print(new_sql)
            transformed_sql = replacer.mutation(new_sql)

            try:
                # print("!")
                if transformed_sql is not None:
                    check_sql = sqlglot.parse_one(transformed_sql.sql(dialect='postgres'),read='postgres')
                # print("@")
            except Exception as e:
                pass
                # print("failed")
                # print(repr(transformed_sql))
            else:
                # print("success")
                # print(transformed_sql)
                if transformed_sql is not None:
                    f.write(transformed_sql.sql(dialect='postgres') + ";\n")
                # print(repr(transformed_sql))
                    num = num + 1

    # print("success num:")
    # print(num)
    end_time = time.time()
    # print("运�?�时�??:", end_time - start_time, "�??")
# 1w test
# success num:
# 9997
# 运�?�时�??: 167.36811637878418 �??