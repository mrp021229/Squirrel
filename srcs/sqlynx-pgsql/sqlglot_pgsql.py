# -*- coding: utf-8 -*-

import sqlglot
import sqlglot_manager
import sqlglot_mutation
import sqlglot_fill
import sys
import os

def mutation(sql):
    # log_path = "/home/output/fuzz_log.txt"
    # os.makedirs(os.path.dirname(log_path), exist_ok=True)
    mutated_sql = sqlglot_mutation.get_mutated_sql(sql)
    # with open(log_path, "a", encoding="utf-8") as log_file:
    #     log_file.write("[Mutated SQL Before Fill]")
    #     try:
    #         log_file.write(mutated_sql + "\n")
    #     except Exception as e:
    #         log_file.write(f"[Error writing mutated SQL: {e}]\n")
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