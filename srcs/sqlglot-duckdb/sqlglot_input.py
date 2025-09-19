# -*- coding: utf-8 -*-

import os
import glob
import chardet
import sqlglot
def strip_semantics(sql,read='duckdb'):
    # 
    try:
        tree = sqlglot.parse_one(sql,read=read)
    except sqlglot.errors.ParseError as e:
        return None

    # print(tree)
    # 
    def replace_node(node):
        # print(node)
        if node is None:
            return
        if isinstance(node, sqlglot.exp.Identifier):  # 
            node.set("this", "x")
        # elif isinstance(node, sqlglot.exp.Literal):  # 
        #     node.set("this", "x")
        elif isinstance(node, sqlglot.exp.Table):  # 
            node.set("this", "x")
        elif isinstance(node, sqlglot.exp.ForeignKey):  # 
            for child in node.args.values():
                replace_node(child)

        elif isinstance(node, sqlglot.exp.Check):  # 
            for child in node.args.values():
                replace_node(child)

        # 
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
            if isinstance(node, sqlglot.exp.Identifier):  # 
                node.set("this", "x")
            # elif isinstance(node, sqlglot.exp.Literal):  # 
            #     node.set("this", "x")
            elif isinstance(node, sqlglot.exp.Table):  # 
                node.set("this", "x")

    replace_x(tree)
    # replace_node(tree)

    # 
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
    
    """
    try:

        parsed_sql = strip_semantics(sql,read='duckdb')
        print("sdfsdf")
        print(sql)

        return parsed_sql  # 
    except Exception:
        return None
def extract_sql_statements(test_dir, output_file):
    # 
    sql_files = glob.glob(os.path.join(test_dir, '**', '*'), recursive=True)
    with open(output_file, 'a', encoding='utf-8') as outfile:
        for sql_file in sql_files:
            encoding = detect_encoding(sql_file)
            if encoding is None:
                print(f" {sql_file} ")
                continue


            with open(sql_file, 'r', encoding='utf-8', errors='replace') as infile:
                sql_content = infile.read()
                # 
                sql_statements = sql_content.split(';')



                for statement in sql_statements:
                    statement = statement.strip()
                    statement = parse_sql(statement)
                    if statement:
                        outfile.write(statement.replace('\n', ' ') + ';\n')


if __name__ == "__main__":
    
