# -*- coding: utf-8 -*-
import os
import subprocess
import random
import sqlglot_pgsql
import sqlglot

import sqlglot
import sqlglot_mutation
import sqlglot_fill
from sqlglot_manager import ExpressionSetManager
expression_manager = None

def init(seed):
    global expression_manager
    expression_manager = ExpressionSetManager()
    expression_manager.load_from_file("/home/Squirrel/srcs/sqlglot-pgsql/pgsql_seed.pkl")  # 替换为实际路径
    sqlglot_mutation.set_expression_manager(expression_manager)  # 注入给子模块
    sqlglot_fill.set_expression_manager(expression_manager)
    # try:
    #     with open("/home/database.txt", "w") as f:
    #         f.write("1")
    #     print("[mutator] init: wrote 1 to /home/database.txt")
    # except Exception as e:
    #     print(f"[mutator] init: failed to write to file - {e}")
    # return 0


def deinit():
    pass


# def deinit():  # optional for Python
#     passs
def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False


def fuzz_count(buf):
    return 2


def fuzz(buf, add_buf, max_size):

    # log_path = "/home/output/fuzz_log.txt"
    # os.makedirs(os.path.dirname(log_path), exist_ok=True)

    # #
    # with open(log_path, "a", encoding="utf-8") as log_file:
    #     log_file.write("[Original buf]:")
    #     try:
    #         log_file.write(buf.decode('utf-8') + "\n")
    #     except UnicodeDecodeError:
    #         log_file.write("[Decode Error:UTF-8]\n")


    buf = buf.decode('utf-8')
    sql_statements = buf.split(';')

    mutated_sql_statements = []

    for sql in sql_statements:
        if sql.strip():

            mutated_out = None

            try:
                mutated_out = sqlglot_pgsql.mutation(sql.strip())

            except Exception as e:
                mutated_out = None
            else:
                pass

            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)
                # print("SDFSDFsdf")
                # # 将原始SQL和变异后的SQL写入文件
                # with open("/home/mutated_sql.txt", "a") as file:
                #     file.write("sql: " + sql + "\n")
                #     file.write("new_sql: " + mutated_out + "\n")


    # print("SD")

    mutated_sql = '; '.join(mutated_sql_statements)
    mutated_sql = mutated_sql.replace('\ufffd', '[INV]')
    mutated_sql = mutated_sql.encode('utf-8', errors='ignore')
    buf = mutated_sql
    buf = bytearray(buf)

    # #
    # with open(log_path, "a", encoding="utf-8") as log_file:
    #     log_file.write("[Mutated buf]:")
    #     try:
    #         log_file.write(buf.decode('utf-8') + "\n")
    #     except UnicodeDecodeError:
    #         log_file.write("[Decode Error:UTF-8]\n")
    if len(buf) == 0:
        return bytearray(b'0')
    return buf

if __name__ == "__main__":
    print("@#@#")
    sql = "select a from b where c = 3;select c from a;"
    tmp=strToBytearray(sql)
    print(repr)
    print(fuzz(tmp,None,None))