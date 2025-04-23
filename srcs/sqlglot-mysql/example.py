# -*- coding: utf-8 -*-

import random
import sqlglot_mysql
import sqlglot


def init(seed):
    pass


def deinit():
    pass


# def deinit():  # optional for Python
#     passs
def queue_new_entry(filename_new_queue, filename_orig_queue):
    return False


def fuzz_count(buf):
    return 10


def fuzz(buf, add_buf, max_size):
    buf = buf.decode('utf-8')
    sql_statements = buf.split(';')

    mutated_sql_statements = []

    for sql in sql_statements:
        if sql.strip():

            mutated_out = None

            try:
                mutated_out = sqlglot_mysql.mutation(sql.strip())

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
    if len(buf) == 0:
        return bytearray(b'0')
    return buf

if __name__ == "__main__":
    print("@#@#")
    sql = "select a from b where c = 3;select c from a;"
    tmp=strToBytearray(sql)
    print(repr)
    print(fuzz(tmp,None,None))