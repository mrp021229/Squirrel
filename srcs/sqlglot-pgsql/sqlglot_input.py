import os
import glob
import chardet
import sqlglot
def strip_semantics(sql,read='postgres'):
    # 解析 SQL 语句为语法树
    try:
        tree = sqlglot.parse_one(sql,read=read)
    except sqlglot.errors.ParseError as e:
        return None

    # print(tree)
    # 替换列名、表名、字符串、数字为占位符
    def replace_node(node):
        # print(node)
        if node is None:
            return
        if isinstance(node, sqlglot.exp.Identifier):  # 表名或列名
            node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Literal):  # 字符串或数字
        #     node.set("this", "x")
        elif isinstance(node, sqlglot.exp.Table):  # 表引用
            node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Star): # *不处理
        #     node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Column):
        #     node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Null):  # NULL 的处理 #null不处理
        #     node.set("this", "x")
        # 处理外键约束等
        elif isinstance(node, sqlglot.exp.ForeignKey):  # 外键约束
            for child in node.args.values():
                replace_node(child)

        elif isinstance(node, sqlglot.exp.Check):  # CHECK约束
            for child in node.args.values():
                replace_node(child)

        # 确保子节点是 Expression 或 list，而不是 string
        if hasattr(node, 'args'):
            for child in node.args.values():
                if isinstance(child, list):
                    for c in child:
                        replace_node(c)
                elif isinstance(child, sqlglot.Expression):
                    replace_node(child)

    def replace_x(tree):
        for node in tree.walk():
            if isinstance(node, sqlglot.exp.TableAlias):
                node.set('columns', None)
            if isinstance(node, sqlglot.exp.Identifier):  # 表名或列名
                node.set("this", "x")
            # elif isinstance(node, sqlglot.exp.Literal):  # 字符串或数字
            #     node.set("this", "x")
            elif isinstance(node, sqlglot.exp.Table):  # 表引用
                node.set("this", "x")

    replace_x(tree)
    # replace_node(tree)

    # 返回剥离后的 SQL
    return tree.sql()
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        confidence = result['confidence']
        return encoding if confidence > 0.5 else None

def parse_sql(sql):
    """
    尝试用 sqlglot 解析 SQL 语句，解析成功返回语句，失败返回 None。
    """
    try:

        parsed_sql = strip_semantics(sql,read='postgres')
        print("sdfsdf")
        print(sql)

        return parsed_sql  # 返回原始 SQL（如果需要进一步处理可以修改）
    except Exception:
        return None
def extract_sql_statements(test_dir, output_file):
    # 查找 test_dir 目录下的所有 .sql 文件
    sql_files = glob.glob(os.path.join(test_dir, '**', '*.sql'), recursive=True)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for sql_file in sql_files:
            encoding = detect_encoding(sql_file)
            if encoding is None:
                print(f"无法检测文件 {sql_file} 的编码格式，已跳过。")
                continue


            with open(sql_file, 'r', encoding='utf-8', errors='replace') as infile:
                sql_content = infile.read()
                # 将文件内容中的每个 SQL 语句合并为一行
                sql_statements = sql_content.split(';')



                for statement in sql_statements:
                    statement = statement.strip()
                    statement = parse_sql(statement)
                    if statement:
                        outfile.write(statement.replace('\n', ' ') + ';\n')


if __name__ == "__main__":
    test_directory = 'E:\your PhD\毕设\sqlglot\postgres\src\\test'  # 请将此路径替换为 PostgreSQL 源码中 test 目录的实际路径
    output_filename = 'pgsql_seed.txt'
    extract_sql_statements(test_directory, output_filename)
    print(f"SQL 语句已提取并保存到 {output_filename}")
