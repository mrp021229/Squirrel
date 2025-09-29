# -*- coding: utf-8 -*-

import copy
import getDBMS
import sqlglot
import random

import time
from sqlglot.expressions import table_name

from sqlglot_manager import ExpressionSetManager
import read_num
# sqlglot.exp
# 
table_dict = {
    'table1': {'columns': ['id', 'name', 'age', 'email', 'a'], 'constraints': []},
    'table2': {'columns': ['a', 'b', 'c'], 'constraints': []},
    'table3': {'columns': ['d', 'e'], 'constraints': []}
}
# def getDBMS():
#     table_dict = {
#         'table1': {'columns': ['id', 'name', 'age', 'email'], 'constraints': []},
#         'table2': {'columns': ['a', 'b', 'c','z'], 'constraints': []},
#         'table3': {'columns': ['d', 'e', 'f', 'p'], 'constraints': []}
#     }
#     return

new_manager = None

def set_expression_manager(mgr):
    global new_manager
    new_manager = mgr

def getSameNode(node):

    new_node = new_manager.get_random_node_v2(node)
    return new_node

def getSumFuc():
    sql = """
            select a,sum(b) from a;
            """
    file_path = "/home/Squirrel/srcs/sqlynx-sqlite/sqlite_seed.pkl"


    # ?
    parsed = sqlglot.parse(sql)
    for node in parsed[0].walk():
        if isinstance(node, sqlglot.exp.Sum):
            new_node = new_manager.get_random_node_v2(node)
            break
    return new_node


def is_aggregate_function(expression):
    # ?
    aggregate_functions = ["COUNT", "SUM", "AVG", "MIN", "MAX", "GROUP_CONCAT", "STD", "VARIANCE", "BIT_AND", "BIT_OR"]

    # 
    if isinstance(expression, sqlglot.expressions.Function) and expression.name.upper() in aggregate_functions:
        return True
    return False


def get_sub_space(parsed, sql_dict):
    columns = []
    alias = None
    if isinstance(parsed, sqlglot.exp.Select):
        exp = parsed.args.get('expressions')
        for col in exp:
            if isinstance(col, sqlglot.exp.Column):
                columns.append(col.this)
            if isinstance(col, sqlglot.exp.Alias):
                columns.append(col.alias)
            if isinstance(col, sqlglot.exp.Star):
                for details in sql_dict:
                    # print(sql_dict[details]['columns'])
                    columns.extend(sql_dict[details]['columns'])
        return columns, alias
    else:
        if isinstance(parsed, sqlglot.exp.Table) or isinstance(parsed, sqlglot.exp.Subquery):
            random_key = random.choice(list(sql_dict.keys()))
            return sql_dict[random_key]['columns'], random.choice(sql_dict[random_key]['alias'])
        else:
            pass
            # print("warning!")
    # print(columns)
    return columns


def is_in_subquery(node, root):
    while node is not root:
        if isinstance(node, sqlglot.exp.Subquery):
            return True
        node = node.parent
    return False





# 
def get_random_table_column(tables):
    # 
    table_name = random.choice(list(tables.keys()))

    # 
    aliases = tables[table_name]['alias']
    if aliases:
        chosen_table = random.choice(aliases)
    else:
        chosen_table = table_name

    # 
    columns = tables[table_name]['columns']
    chosen_column = random.choice(columns)

    return chosen_table, chosen_column


def numbered_x(parsed):
    total_num = 0
    for node in parsed.walk():
        if isinstance(node, sqlglot.exp.Identifier):  # 
            node.set("this", "x" + str(total_num))
            total_num = total_num + 1
        # elif isinstance(node, sqlglot.exp.Literal):  # 
        #     node.set("this", "x" + str(total_num))
        #     total_num = total_num + 1
        elif isinstance(node, sqlglot.exp.Table):  # 
            node.set("this", "x" + str(total_num))
            total_num = total_num + 1

    return parsed


sub_space = {}#

def fill_sql_template(parsed):
    table_dict = getDBMS.getDBMS()

    # 
    def get_random_column(table_name):
        return random.choice(table_dict[table_name]['columns'])

    # 
    def get_random_table():
        return random.choice(list(table_dict.keys()))

    v_num = read_num.read_integer_from_file()
    # print(parsed)
    # 
    for table in parsed.find_all(sqlglot.exp.Table):
        table.set('db', None)
    sql_dict = {}
    current_space = {}

    def fill_table(node):
        table_name = get_random_table()
        alias = node.args.get("alias")
        # test = sqlglot.parse(parsed.sql())
        # print(test)
        if alias is None:
            node.set("alias", sqlglot.exp.TableAlias(this=sqlglot.exp.Identifier(this=str(node.this), quoted=False)))
        node.set("this", table_name)
        alias = node.args.get("alias")
        # test = sqlglot.parse(parsed.sql())
        if isinstance(alias, sqlglot.exp.TableAlias):
            alias = str(alias)
        return table_name, alias

    def fill_sql_dict(table_name, alias, columns):
        if table_name not in sql_dict:
            sql_dict[table_name] = {
                "alias": [alias],
                "columns": columns
            }
        else:
            sql_dict[table_name]['alias'].append(alias)
        return {"table_name": table_name,
                "alias": alias,
                "columns": columns}


    if isinstance(parsed, sqlglot.exp.Create):
        kind = parsed.args.get('kind')
        columns = []
        if kind == 'TABLE':
            if isinstance(parsed.this,sqlglot.exp.Table) is False:
                parsed = parsed.this
            node = parsed.this
            table_name = 'v'+str(v_num)
            v_num =v_num+1
            while isinstance(node, sqlglot.exp.Table) is False:
                node = node.this
            # print([parsed])
            node.set('this',table_name)
            expression = parsed.args.get('expression')
            if expression:
                fill_sql_template(expression)
            expressions = parsed.args.get('expressions')
            # print(expressions)
            if expressions is not None:
                # print("SDf")
                columnDefs = parsed.find_all(sqlglot.exp.ColumnDef)
                for columnDef in columnDefs:
                    if is_in_subquery(columnDef, parsed) is not True:
                        column_name = 'v'+str(v_num)
                        v_num = v_num+1
                        columnDef.this.set('this',column_name)
                        columns.append(column_name)
                primary_key = parsed.find_all(sqlglot.exp.Column)
                key_space = copy.deepcopy(columns)
                for key in primary_key:
                    if is_in_subquery(key, parsed) is not True:
                        if len(key_space) >0 :
                            tmp = random.choice(key_space)
                            key.this.set('this',tmp)
                            key_space.remove(tmp)
                        else:
                            key.set('this',None)
        if kind == 'INDEX':
            name = 'v'+str(v_num)
            v_num = v_num+1
            index = parsed.this
            index.set('this', name)
            table_name = get_random_table()
            table = index.args.get('table')
            table.set('this',table_name)
            columns = parsed.find_all(sqlglot.exp.Column)
            for column in columns:
                column_name = get_random_column(table_name)
                column.set('this', column_name)
        if kind =='VIEW':
            name = 'v' + str(v_num)
            v_num = v_num + 1
            table = parsed.args.get('this')
            table.set('this', name)
            expression = parsed.args.get('expression')
            if expression:
                fill_sql_template(expression)
        read_num.write_integer_to_file(v_num)
        return parsed
    if isinstance(parsed, sqlglot.exp.Insert):
        # print([parsed])
        schema = parsed.this
        # print([schema])
        expressions = schema.args.get('expressions')
        columns_num = len(expressions)
        expression = parsed.args.get('expression')
        table_name = get_random_table()
        table = schema.args.get('this')
        table.set('this',table_name)
        # print(table_name)
        identifier_names = random.sample(table_dict[table_name]['columns'], columns_num)
        for identifier in expressions:
            identifier_name = random.choice(identifier_names)
            identifier.set('this',identifier_name)
            identifier_names.remove(identifier_name)
        # print([expression])
        if isinstance(expression, sqlglot.exp.Select): # 
            select = expression
            # print([select])
            fill_sql_template(select)
            select_expressions = select.args.get('expressions')
            if select.args.get('group') is not None:
                columns_num  =columns_num -1
            # if len(select_expressions) >columns_num :
        if isinstance(expression, sqlglot.exp.Values):
            tuples = expression.args.get('expressions')
            for tuple in tuples:
                literals = tuple.args.get('expressions')
                while len(literals) > columns_num:
                    literals.remove(random.choice(literals))
                while len(literals) < columns_num:
                    node = random.choice(literals)
                    literals.append(getSameNode(node))
        return parsed
    if isinstance(parsed, sqlglot.exp.Drop):
        kind = parsed.args.get('kind')
        if kind =='TABLE':
            table = parsed.args.get('this')

            table_name = get_random_table()
            table.set('this', table_name)
            return parsed
    if isinstance(parsed, sqlglot.exp.Update):
        table = parsed.args.get('this')
        if isinstance(table, sqlglot.exp.Table):
            fill_sql_template(table)
        alias = table.args.get('alias')

        table_name = table.args.get('this')

        key = parsed.args
        for node in key:
            if key[node] is not None and node != 'this':
                if isinstance(key[node], list):
                    # print(key[node])
                    for a in key[node]:
                        for b in a.find_all(sqlglot.exp.Column):
                            if is_in_subquery(b, a) is not True:
                                new_column = get_random_column(table_name)
                                b.set('this',new_column)
                                if b.args.get('table') is not None:
                                    if alias is not None:
                                        b.set('table',alias)
                                    else:
                                        b.set('table',table_name)

                else:
                    # print([key[node]])
                    for b in key[node].find_all(sqlglot.exp.Column):
                        # print("@#@#")
                        if is_in_subquery(b, key[node]) is not True:
                            new_column = get_random_column(table_name)
                            b.set('this', new_column)
                            if b.args.get('table') is not None:
                                if alias is not None:
                                    b.set('table', alias)
                                else:
                                    b.set('table', table_name)
        return parsed

    if isinstance(parsed, sqlglot.exp.Select):
        from_clause = parsed.args.get('from')
        node = from_clause.this
        # print("SDFDS")
        if isinstance(node, sqlglot.exp.Table):
            # print("!!!")
            table_name, alias = fill_table(node)
            columns = table_dict[table_name]['columns']
            current_space = fill_sql_dict(table_name, alias, columns)
        if isinstance(node, sqlglot.exp.Subquery):
            table_name = str(node.this)
            columns = sub_space[table_name]['columns']
            alias = table.args.get('alias')
            if alias is None:
                alias = sub_space[table_name]['alias']
            current_space = fill_sql_dict(table_name, alias, columns)

    if isinstance(parsed, sqlglot.exp.Table):
        table_name, alias = fill_table(parsed)
        columns = table_dict[table_name]['columns']
        current_space = fill_sql_dict(table_name, alias, columns)
    if isinstance(parsed, sqlglot.exp.Subquery):
        table_name = str(parsed.this)
        columns = sub_space[table_name]['columns']
        alias = table.args.get('alias')
        if alias is None:
            alias = sub_space[table_name]['alias']
        current_space = fill_sql_dict(table_name, alias, columns)
    # print(current_space)

    def fill_using_and_on(join, used_table_name, used_table_columns, table_name, table_columns):
        using = join.args.get('using')
        on = join.args.get('on')
        if on:
            num = 0
            for node in on.find_all(sqlglot.exp.Column):
                if num % 2 == 0:
                    name = used_table_name
                    columns = random.choice(used_table_columns)
                else:
                    name = table_name
                    columns = random.choice(table_columns)
                if is_in_subquery(node, join) is not True:
                    node.set('this', sqlglot.exp.Identifier(this=columns, quoted=False))
                    node.set('table', sqlglot.exp.Identifier(this=name, quoted=False))
        if using:
            common_elements = list(set(used_table_columns) & set(table_columns))
            # print(common_elements)
            if len(common_elements) < len(using):
                join_key = [key for key, value in join.args.items() if value is not None]
                for key in join_key:
                    if key != 'this':
                        join.set(key, None)
                join.set('method', 'natural')
            else:
                random_elements = random.sample(common_elements, len(using))
                for a in range(len(random_elements)):
                    using[a].set('this', random_elements[a])

    join_clause = parsed.args.get("joins")
    if join_clause:
        for join in join_clause:
            used_table_name = current_space['alias']
            used_table_columns = current_space['columns']
            node = join.this
            if isinstance(node, sqlglot.exp.Table):
                table_name, alias = fill_table(node)
                columns = table_dict[table_name]['columns']
                current_space = fill_sql_dict(table_name, alias, columns)
            if isinstance(node, sqlglot.exp.Subquery):
                table_name = str(node.this)
                columns = sub_space[table_name]['columns']
                alias = table.args.get('alias')
                if alias is None:
                    alias = sub_space[table_name]['alias']
                current_space = fill_sql_dict(table_name, alias, columns)
            fill_using_and_on(join, used_table_name, used_table_columns, table_name, columns)

    def fill_column(node):
        new_table, new_column = get_random_table_column(sql_dict)
        node.set("this", new_column)
        node.set("table", new_table)

    key = parsed.args
    # print(key)
    new_node = getSumFuc()#
    if 'group' in key and key['group'] is not None:
        parsed.args['expressions'].append(new_node)
    new_node = []
    for node in key:
        if key[node] is not None and node != 'from' and node != 'joins' and node != 'this':
            # if node == 'group':
            #     new_node = getSumFuc()
            #     parsed.args['expressions'].append(new_node)

            if isinstance(key[node], list):
                # print(key[node])
                for a in key[node]:
                    for b in a.find_all(sqlglot.exp.Column):
                        if is_in_subquery(b, a) is not True:
                            fill_column(b)
            else:
                # print([key[node]])
                for b in key[node].find_all(sqlglot.exp.Column):
                    # print("@#@#")
                    if is_in_subquery(b, key[node]) is not True:
                        fill_column(b)
            if node == 'expressions':
                columns = key[node]
                for column in columns:
                    if isinstance(column, sqlglot.exp.Column):
                        new_node.append(column)

            if node == 'group' and len(new_node)>0 :
                group = parsed.args['group']
                group.args['expressions'].clear()
                for column in new_node:

                    group.args['expressions'].append(column)

    columns, alias = get_sub_space(parsed, sql_dict)
    sub_space[str(parsed.sql())] = {
        "columns": columns,
        "alias": alias
    }
    read_num.write_integer_to_file(v_num)
    return parsed


# scopes
scoped_node = set()

subqueries = []


def analyze_subqueries(parsed, depth):
    """
    
    """
    # if result is None:
    #     result = []
    for node in parsed.walk(bfs=True):
        # 
        if isinstance(node, sqlglot.exp.Subquery) and node not in scoped_node:
            scoped_node.add(node)
            analyze_subqueries(node.this, depth + 1)
            # table_space = getTableSpace(node)
            subqueries.append({
                "parent": parsed,  # 
                "query": node,  # 
                "table_space": None,
                "depth": depth
            })

    return


def sort_subqueries(subqueries):
    """
    
    """
    return sorted(subqueries, key=lambda x: x["depth"], reverse=True)


def fill_sql(sql):
    # with open("memtest.txt", "a") as f:
    #     f.write(f"sqlglot_mutation fill module expression_manager id: {id(new_manager)}\n")
    sub_space.clear()
    subqueries.clear()
    scoped_node.clear()
    parsed = sqlglot.parse(sql)
    # print(parsed)
    parsed[0] = numbered_x(parsed[0])
    analyze_subqueries(parsed[0], 1)
    # 
    sorted_subqueries = sort_subqueries(subqueries)
    # for subquery in sorted_subqueries:
    #     print(f"Query: {subquery['query']}, table_space: {subquery['table_space']}, "
    #           f"depth: {subquery['depth']}")
    # print(sorted_subqueries[0]['query'])
    for subquery in sorted_subqueries:
        fill_sql_template(subquery['query'])
    fill_sql_template(parsed[0])
    sub_space.clear()
    subqueries.clear()
    scoped_node.clear()
    return parsed[0].sql(dialect='sqlite')


# # 
# template = "SELECT x0, SUM(x4) as b FROM x1 join A LEFT JOIN x2 on x1.a=x2.b WHERE x6.x5 IS NULL group by x9"
# parsed = sqlglot.parse(template)
#
# print(parsed)
# # 
# filled_sql = fill_sql_template(parsed[0])
# print(filled_sql)

def get_sql():
    with open('/home/Squirrel/srcs/sqlynx-sqlite/mutation-sqlite.txt', 'r', encoding='utf-8') as file:
        # 
        content = file.read()

        # 
        sql_statements = content.split(';')

        # 
        sql_statements = [stmt.strip() for stmt in sql_statements if stmt.strip()]

    # 
    return sql_statements


def write(sql):
    # 
    output_file = "/home/Squirrel/srcs/sqlynx-sqlite/filledSQL.txt"
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(sql + ";\n")


if __name__ == "__main__":

    # fill program
    start_time = time.time()
    for sql in get_sql():
        try:
            filledQSL = fill_sql(sql)
            write(filledQSL.sql())
        except Exception as e:
            print("failed")
            print(sql)
        else:
            print("success")
    end_time = time.time()
    print(":", end_time - start_time, "?")
    exit(0)
    #
    # CREATE VIEW x AS SELECT 1 + 2 /* hello */ + 3 FROM (SELECT CAST(x.x AS CHAR CHARACTER SET utf8mb3) FROM x, x AS x LIMIT 1) AS x WHERE x = x
    # CREATE VIEW v6 AS SELECT CAST(1 / 3 AS FLOAT) AS x, CAST(1 / 3 AS DOUBLE) AS x, CAST(CAST(999.00009 AS DECIMAL(7, 4)) AS DOUBLE) AS x
    # CREATE VIEW x.x AS SELECT x + 0 FROM (x AS x JOIN (x AS x JOIN x ON x.x = x.x) ON (x.x = x.x AND x.x IN (SELECT x FROM x))) WHERE x = ANY (SELECT x FROM x)
    # CREATE VIEW x AS SELECT x.x + 3 FROM (SELECT * FROM x ORDER BY x, x) AS x
    #
    #
    #
    #
    #
    #

    sql = """
     UPDATE products p
JOIN (SELECT product_id, SUM(order_amount) AS total_sales
      FROM orders
      GROUP BY product_id) o
  ON p.product_id = o.product_id
SET p.sales = o.total_sales
WHERE p.product_type = 'Electronics';

    
    """
    parsed = sqlglot.parse(sql)
    # print([parsed[0]])
    parsed[0] = numbered_x(parsed[0])
    analyze_subqueries(parsed[0], 1)
    # 
    sorted_subqueries = sort_subqueries(subqueries)
    for subquery in sorted_subqueries:
        print(f"Query: {subquery['query']}, table_space: {subquery['table_space']}, "
              f"depth: {subquery['depth']}")
    # print(sorted_subqueries[0]['query'])
    for subquery in sorted_subqueries:
        fill_sql_template(subquery['query'].this)
    print("result")
    fill_sql_template(parsed[0])
    print(parsed[0])
# 