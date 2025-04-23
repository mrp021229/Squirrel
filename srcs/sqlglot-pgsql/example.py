# -*- coding: utf-8 -*-

import random
import sqlglot_pgsql
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
                mutated_out = sqlglot_pgsql.mutation(sql.strip())

            except Exception as e:
                mutated_out = None
            else:
                pass
            if mutated_out is None:
                print("SDSD")
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)
                print("SDFSDFsdf")
                # # 将原始SQL和变异后的SQL写入文件
                # with open("/home/mutated_sql.txt", "a") as file:
                #     file.write("sql: " + sql + "\n")
                #     file.write("new_sql: " + mutated_out + "\n")
            else:
                return None

    print("SD")
    
    mutated_sql = '; '.join(mutated_sql_statements)
    mutated_sql = mutated_sql.replace('\ufffd', '[INV]')
    mutated_sql = mutated_sql.encode('utf-8', errors='ignore')
    buf = mutated_sql
    buf = bytearray(buf)
    return buf
def strToBytearray(sql):
    byte = sql.encode('utf-8')
    byteArray = bytearray(byte)
    return byteArray
if __name__ == "__main__":
    print("@#@#")
    sql = "select a from b where c = 3;"
    tmp = strToBytearray(sql)
    tnt = fuzz(tmp,None,None)
    if tnt is None:
        print("is None")
    else:
        print(repr(tnt))