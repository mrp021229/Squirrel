# -*- coding: utf-8 -*-

import sqlglot
import sqlglot_manager
import sqlglot_mutation
import sqlglot_fill
import sys

def mutation(sql):
    mutated_sql = sqlglot_mutation.get_mutated_sql(sql)
    # print("mutation")
    # print(mutated_sql)
    filled_sql = sqlglot_fill.fill_sql(mutated_sql)
    # print("fill")
    # print(filled_sql)
    return filled_sql

if __name__ == "__main__":
    sql = """
    SELECT c2, c6 FROM t1, t2 WHERE t1.c1 = t2.c5;
    SELECT x FROM x WHERE x > 0.5
    """
    print(type(sql))
    print(sql)
    byte= sql.encode('utf-8')
    print(type(byte))
    print(repr(byte))
    byte = bytearray(byte)
    print(repr(byte))

    # print(mutation("create table v0(v1 INT, v2 INT);"))