# -*- coding: utf-8 -*-

import random
import sqlglot_pgsql
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
    with open("/home/mutated_test.txt", "a") as f:
        f.write("========== NEW TEST ==========\n")
        f.write("repr(buf):\n" + repr(buf) + "\n")
        f.write("hex(buf):\n" + buf.hex() + "\n")
        try:
            f.write("decoded(utf-8):\n" + buf.decode('utf-8') + "\n")
        except:
            f.write("utf-8 decode failed\n")

    buf = buf.decode('utf-8')
    
    
    sql_statements = buf.split(';')
    
    
    mutated_sql_statements = []
    

    for sql in sql_statements:
        if sql.strip():  
            num = 0
            mutated_out = None
            
            while num <= 10 and mutated_out is None:
                mutated_out = sqlglot_pgsql.mutation(sql.strip())  
                num = num + 1
            if mutated_out is not None:
                mutated_sql_statements.append(mutated_out)  
                # 将原始SQL和变异后的SQL写入文件
                with open("/home/mutated_sql.txt", "a") as file:
                    file.write("sql: " + sql + "\n")
                    file.write("new_sql: " + mutated_out + "\n")
            else:
                mutated_sql_statements.append(sql)  
        else:
            mutated_sql_statements.append(sql)  
    
    
    mutated_sql = '; '.join(mutated_sql_statements)
    mutated_sql = mutated_sql.replace('\ufffd', '[INV]')
    print(mutated_sql)
    mutated_sql = mutated_sql.encode('utf-8', errors='ignore')
    print(mutated_sql)
    buf = mutated_sql
    return buf

if __name__ == "__main__":
    print("@#@#")
    print(fuzz("create table v0(v1 INT, v2 INT);",None,None))